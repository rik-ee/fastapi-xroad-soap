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
from ..elements import SwaRefUtils
from ..base import (
	BaseElementSpec,
	CompositeMeta,
	MessageBody
)
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
				complex_types=_generate_complex_types(actions),
				simple_types=_generate_simple_types(actions)
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
	xro_xsd = "http://x-road.eu/xsd/xroad.xsd"
	xro_import = Import(namespace=xro_xsd, schema_loc=xro_xsd)
	imports = [xro_import]
	for action in actions.values():
		if (
			action.body_type is not None
			and SwaRefUtils.contains_swa_ref_specs(action.body_type)
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
		if action.body_type is not None:
			cls_name = action.body_type_name
			elements.append(Element(
				name=cls_name,
				type=f"tns:{cls_name}"
			))
		if action.return_type is not None:
			cls_name = action.return_type_name
			elements.append(Element(
				name=cls_name,
				type=f"tns:{cls_name}"
			))
	return [
		*elements,
		Element(
			name="FaultResponse",
			type="tns:FaultResponse"
		)
	]


def get_complex_types(composite_type: t.Type[MessageBody]) -> t.List[t.Type[MessageBody]]:
	complex_types = [composite_type]
	a8ns = getattr(composite_type, '__annotations__', {})
	for key, value in a8ns.items():
		if type(value) is CompositeMeta:
			_ct = get_complex_types(value)
			complex_types.extend(_ct)
	return complex_types


def get_simple_types(complex_type: t.Type[MessageBody]) -> t.List[BaseElementSpec]:
	simple_types = []
	for k, v in complex_type.model_specs().items():
		print(k, isinstance(v, BaseElementSpec))


def _generate_complex_types(actions: t.Dict[str, SoapAction]) -> t.List[ComplexType]:
	complex_types = []
	for action in actions.values():
		if action.body_type is not None:
			_ct = get_complex_types(action.body_type)
			complex_types.extend(_ct)
		if action.return_type is not None:
			_ct = get_complex_types(action.return_type)
			complex_types.extend(_ct)
	for item in complex_types:
		get_simple_types(item)

	return [
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
	]


def _generate_simple_types(actions: t.Dict[str, SoapAction]) -> t.List[SimpleType]:
	return []


def _generate_messages(actions: t.Dict[str, SoapAction]) -> t.List[WSDLMessage]:
	messages = []
	for name, action in actions.items():
		if action.body_type is not None:
			cls_name = action.body_type_name
			messages.append(WSDLMessage(
				name=cls_name,
				parts=[WSDLPart(element=f"tns:{cls_name}")]
			))
		if action.return_type is not None:
			cls_name = action.return_type_name
			messages.append(WSDLMessage(
				name=cls_name,
				parts=[WSDLPart(element=f"tns:{cls_name}")]
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
		_docs, _input, _output = {}, {}, {}
		if action.description is not None:
			_docs = {"documentation": WSDLDocumentation(
				title=inflection.titleize(name),
				notes=action.description
			)}
		if action.body_type is not None:
			cls_name = action.body_type_name
			_input = {"input": WSDLInputPort(
				message=f"tns:{cls_name}",
				name=cls_name
			)}
		if action.return_type is not None:
			cls_name = action.return_type_name
			_output = {"output": WSDLOutputPort(
				message=f"tns:{cls_name}",
				name=cls_name
			)}
		ops.append(WSDLOperationPort(
			**_docs,
			**_input,
			**_output,
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
