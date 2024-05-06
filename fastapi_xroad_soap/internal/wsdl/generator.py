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


def generate(actions: t.Dict[str, SoapAction], name: str, tns: str, version: int) -> bytes:
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
		binding=_generate_binding(actions, version),
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
	elements = {}
	for name, action in actions.items():
		for model in [action.body_type, action.return_type]:
			if model is None:
				continue
			wsdl_name = model.wsdl_name()
			if wsdl_name in elements:
				continue
			elements[wsdl_name] = mod.Element(
				name=wsdl_name,
				type=f"tns:{wsdl_name}"
			)
	return [
		*list(elements.values()),
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
						mod.Element(name="faultactor", type="string", min_occurs="0"),
						mod.Element(name="detail", type="tns:FaultResponseDetail", min_occurs="0")
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
	messages = {}
	for action in actions.values():
		for model in [action.body_type, action.return_type]:
			if model is None:
				continue
			wsdl_name = model.wsdl_name()
			if wsdl_name in messages:
				continue
			messages[wsdl_name] = mod.WSDLMessage(
				name=wsdl_name,
				parts=[mod.WSDLPart(
					element=f"tns:{wsdl_name}"
				)]
			)
	return [
		*list(messages.values()),
		mod.WSDLMessage(
			name="FaultResponse",
			parts=[mod.WSDLPart(element="tns:FaultResponse", name="fault")]
		),
		mod.WSDLMessage(
			name="xroadHeader",
			parts=[
				mod.WSDLPart(element="xro:client", name="client"),
				mod.WSDLPart(element="xro:service", name="service"),
				mod.WSDLPart(element="xro:id", name="id"),
				mod.WSDLPart(element="xro:protocolVersion", name="protocolVersion"),
				mod.WSDLPart(element="xro:userId", name="userId")
			]
		)
	]


def _generate_port_type(actions: t.Dict[str, SoapAction]) -> mod.WSDLPortType:
	ops = []
	for name, action in actions.items():
		port_docs = port_input = port_output = None
		if action.description is not None:
			port_docs = mod.WSDLDocumentation(
				title=inflection.titleize(name),
				notes=action.description
			)
		if action.body_type is not None:
			wsdl_name = action.body_type.wsdl_name()
			port_input = mod.WSDLInputPort(
				message=f"tns:{wsdl_name}",
				name=wsdl_name
			)
		if action.return_type is not None:
			wsdl_name = action.return_type.wsdl_name()
			port_output = mod.WSDLOutputPort(
				message=f"tns:{wsdl_name}",
				name=wsdl_name
			)
		ops.append(mod.WSDLOperationPort(
			documentation=port_docs,
			input=port_input,
			output=port_output,
			name=name
		))
	return mod.WSDLPortType(operations=ops)


def _generate_binding(actions: t.Dict[str, SoapAction], version: int) -> mod.WSDLBinding:
	return mod.WSDLBinding(
		binding=mod.SOAPBinding(),
		operations=[
			mod.WSDLOperationBinding(
				name=key,
				operation=mod.SOAPOperationBinding(
					soap_action=key
				),
				version=mod.XROADVersion(version=f"v{version}")
			)
			for key in actions.keys()
		]
	)
