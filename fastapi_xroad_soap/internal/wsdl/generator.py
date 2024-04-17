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
from ..soap.action import SoapAction
from ..elements.models import SwaRefUtils
from .helpers import *
from .models import *


__all__ = ["generate"]


def generate(actions: t.Dict[str, SoapAction], name: str, tns: str) -> bytes:
	return WSDLDefinitions(
		target_ns=tns,
		name=name,
		types=WSDLTypes(
			service_schema=Schema(
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
		service=WSDLService(
			port=WSDLPortBinding(
				address=SOAPAddress()
			)
		)
	).to_xml()


def _generate_imports(actions: t.Dict[str, SoapAction]) -> t.List[Import]:
	has_specs = SwaRefUtils.contains_swa_ref_specs
	xro_xsd = "http://x-road.eu/xsd/xroad.xsd"
	imports = [Import(
		namespace=xro_xsd,
		schema_loc=xro_xsd
	)]
	for action in actions.values():
		if (
			action.body_type is not None
			and has_specs(action.body_type)
		):
			wsi = "http://ws-i.org/profiles/basic/1.1/"
			imports.append(Import(
				namespace=f"{wsi}xsd",
				schema_loc=f"{wsi}swaref.xsd"
			))
	return imports


def _generate_elements(actions: t.Dict[str, SoapAction]) -> t.List[Element]:
	elements = []
	for name, action in actions.items():
		for model in [action.body_type, action.return_type]:
			if model is not None:
				elements.append(Element(
					name=model.__name__,
					type=f"tns:{model.__name__}"
				))
	return [
		*elements,
		Element(
			name="FaultResponse",
			type="tns:FaultResponse"
		)
	]


def _generate_types(actions: t.Dict[str, SoapAction]) -> t.Dict:
	complex_types, simple_types = gather_all_types(actions)
	return dict(
		complex_types=[
			*complex_types,
			ComplexType(
				name="FaultResponse",
				sequence=Sequence(
					elements=[
						Element(name="faultcode", type="string"),
						Element(name="faultstring", type="string"),
						Element(name="faultactor", type="string"),
						Element(name="detail", type="tns:FaultResponseDetail")
					]
				)
			),
			ComplexType(
				name="FaultResponseDetail",
				sequence=Sequence(
					elements=[AnyXML()]
				)
			)
		],
		simple_types=simple_types
	)


def _generate_messages(actions: t.Dict[str, SoapAction]) -> t.List[WSDLMessage]:
	messages = []
	for name, action in actions.items():
		for model in [action.body_type, action.return_type]:
			if model is not None:
				messages.append(WSDLMessage(
					name=model.__name__,
					parts=[WSDLPart(element=f"tns:{model.__name__}")]
				))
	return [
		*messages,
		WSDLMessage(
			name="FaultResponse",
			parts=[WSDLPart(element="tns:FaultResponse", name="fault")]
		),
		WSDLMessage(
			name="xroadHeader",
			parts=[
				WSDLPart(element="xro:userId", name="userId"),
				WSDLPart(element="xro:protocolVersion", name="protocolVersion"),
				WSDLPart(element="xro:id", name="id"),
				WSDLPart(element="xro:service", name="service"),
				WSDLPart(element="xro:client", name="client")
			]
		)
	]


def _generate_port_type(actions: t.Dict[str, SoapAction]) -> WSDLPortType:
	ops = []
	for name, action in actions.items():
		ops.append(WSDLOperationPort(
			documentation=(
				None if action.description is None else
				WSDLDocumentation(
					title=inflection.titleize(name),
					notes=action.description
				)
			),
			input=(
				None if action.body_type is None else
				WSDLInputPort(
					message=f"tns:{action.body_type.__name__}",
					name=action.body_type.__name__
				)
			),
			output=(
				None if action.return_type is None else
				WSDLOutputPort(
					message=f"tns:{action.return_type.__name__}",
					name=action.return_type.__name__
				)
			),
			name=name
		))
	return WSDLPortType(operations=ops)


def _generate_binding(actions: t.Dict[str, SoapAction]) -> WSDLBinding:
	return WSDLBinding(
		binding=SOAPBinding(),
		operations=[
			WSDLOperationBinding(
				name=key,
				operation=SOAPOperationBinding(
					soap_action=key
				)
			)
			for key in actions.keys()
		]
	)
