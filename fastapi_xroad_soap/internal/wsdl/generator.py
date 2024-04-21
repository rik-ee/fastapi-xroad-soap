#
#   European Union Public License 1.2
#
#   Copyright (c) 2024, Centre of Registers and Information Systems
#
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#
#   SPDX-License-Identifier: EUPL-1.2
#
import typing as t
import inflection
from ..base import MessageBody
from ..constants import WSDL_NSMAP
from ..soap.action import SoapAction
from ..elements.models import SwaRefSpec
from . import helpers, models as mod


__all__ = ["generate"]


def generate(actions: t.Dict[str, SoapAction], name: str, tns: str) -> bytes:
	wsdl_def = type(
		"WSDLDefinitions", (mod.WSDLDefinitions,),
		{}, nsmap={**WSDL_NSMAP, "tns": tns}
	)
	wsdl_data: str = wsdl_def(
		target_ns=tns,
		name=name,
		types=mod.WSDLTypes(
			service_schema=mod.Schema(
				target_ns=tns,
				includes=[],
				imports=_generate_imports(actions),
				elements=_generate_elements(actions),
				**_generate_types(actions)
			)
		),
		messages=_generate_messages(actions),
		port_type=_generate_port_type(actions),
		binding=_generate_binding(actions),
		service=mod.WSDLService(
			port=mod.WSDLPortBinding(
				address=mod.SOAPAddress()
			)
		)
	).to_xml(pretty_print=True).decode()
	return helpers.format_wsdl_definitions(wsdl_data)


def _generate_imports(actions: t.Dict[str, SoapAction]) -> t.List[mod.Import]:
	xro = "http://x-road.eu/xsd/xroad.xsd"
	imports = [mod.Import(
		namespace=xro,
		schema_loc=xro
	)]
	for action in actions.values():
		for model in [action.body_type, action.return_type]:
			if model is None:
				continue
			_add_swaref_import(model, imports)
	return imports


def _add_swaref_import(model: t.Type[MessageBody], imports: t.List[mod.Import]) -> None:
	wsi = "http://ws-i.org/profiles/basic/1.1/"
	for nested_model in model.nested_models():
		specs = nested_model.model_specs()
		for spec in specs.values():
			if not isinstance(spec, SwaRefSpec):
				continue
			imports.append(mod.Import(
				namespace=f"{wsi}xsd",
				schema_loc=f"{wsi}swaref.xsd"
			))
			return


def _generate_elements(actions: t.Dict[str, SoapAction]) -> t.List[mod.Element]:
	elements = []
	for name, action in actions.items():
		for model in [action.body_type, action.return_type]:
			if model is None:
				continue
			elements.append(mod.Element(
				name=model.__name__,
				type=f"tns:{model.__name__}"
			))
	return [
		*elements,
		mod.Element(
			name="FaultResponse",
			type="tns:FaultResponse"
		)
	]


def _generate_types(actions: t.Dict[str, SoapAction]) -> t.Dict:
	complex_types, simple_types = helpers.gather_all_types(actions)
	return dict(
		complex_types=[
			*complex_types,
			mod.ComplexType(
				name="FaultResponse",
				sequence=mod.Sequence(
					elements=[
						mod.Element(name="faultcode", type="string"),
						mod.Element(name="faultstring", type="string"),
						mod.Element(name="faultactor", type="string"),
						mod.Element(name="detail", type="tns:FaultResponseDetail")
					]
				)
			),
			mod.ComplexType(
				name="FaultResponseDetail",
				sequence=mod.Sequence(
					elements=[mod.AnyXML()]
				)
			)
		],
		simple_types=simple_types
	)


def _generate_messages(actions: t.Dict[str, SoapAction]) -> t.List[mod.WSDLMessage]:
	messages = []
	for name, action in actions.items():
		for model in [action.body_type, action.return_type]:
			if model is None:
				continue
			messages.append(mod.WSDLMessage(
				name=model.__name__,
				parts=[mod.WSDLPart(element=f"tns:{model.__name__}")]
			))
	return [
		*messages,
		mod.WSDLMessage(
			name="FaultResponse",
			parts=[mod.WSDLPart(element="tns:FaultResponse", name="fault")]
		),
		mod.WSDLMessage(
			name="xroadHeader",
			parts=[
				mod.WSDLPart(element="xro:userId", name="userId"),
				mod.WSDLPart(element="xro:protocolVersion", name="protocolVersion"),
				mod.WSDLPart(element="xro:id", name="id"),
				mod.WSDLPart(element="xro:service", name="service"),
				mod.WSDLPart(element="xro:client", name="client")
			]
		)
	]


def _generate_port_type(actions: t.Dict[str, SoapAction]) -> mod.WSDLPortType:
	ops = []
	for name, action in actions.items():
		ops.append(mod.WSDLOperationPort(
			documentation=(
				None if action.description is None else
				mod.WSDLDocumentation(
					title=inflection.titleize(name),
					notes=action.description
				)
			),
			input=(
				None if action.body_type is None else
				mod.WSDLInputPort(
					message=f"tns:{action.body_type.__name__}",
					name=action.body_type.__name__
				)
			),
			output=(
				None if action.return_type is None else
				mod.WSDLOutputPort(
					message=f"tns:{action.return_type.__name__}",
					name=action.return_type.__name__
				)
			),
			name=name
		))
	return mod.WSDLPortType(operations=ops)


def _generate_binding(actions: t.Dict[str, SoapAction]) -> mod.WSDLBinding:
	return mod.WSDLBinding(
		binding=mod.SOAPBinding(),
		operations=[
			mod.WSDLOperationBinding(
				name=key,
				operation=mod.SOAPOperationBinding(
					soap_action=key
				)
			)
			for key in actions.keys()
		]
	)
