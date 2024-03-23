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
from ...envelope import BaseXmlModel, Attribute
from ...constants import WSDL_NSMAP


__all__ = [
	"SOAPFault",
	"SOAPBody",
	"SOAPHeader",
	"WSDLFaultBinding",
	"WSDLOutputBinding",
	"WSDLInputBinding",
	"XROADVersion",
	"SOAPOperationBinding",
	"WSDLOperationBinding",
	"SOAPBinding",
	"WSDLBinding"
]


class SOAPFault(BaseXmlModel, tag="fault", ns="soap", nsmap=WSDL_NSMAP):
	name: str = Attribute(default="FaultResponse")
	use: str = Attribute(default="literal")


class SOAPBody(BaseXmlModel, tag="body", ns="soap", nsmap=WSDL_NSMAP):
	use: str = Attribute(default="literal")


class SOAPHeader(BaseXmlModel, tag="header", ns="soap", nsmap=WSDL_NSMAP):
	message: str = Attribute(default="tns:xroadHeader")
	use: str = Attribute(default="literal")
	part: str = Attribute()


class WSDLFaultBinding(BaseXmlModel, tag="fault", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = Attribute(default="FaultResponse")
	fault: SOAPFault = SOAPFault()


class WSDLOutputBinding(BaseXmlModel, tag="output", ns="wsdl", nsmap=WSDL_NSMAP):
	headers: t.List[SOAPHeader] = [
		SOAPHeader(part="client"),
		SOAPHeader(part="service"),
		SOAPHeader(part="id"),
		SOAPHeader(part="userId"),
		SOAPHeader(part="protocolVersion")
	]
	body: SOAPBody = SOAPBody()


class WSDLInputBinding(BaseXmlModel, tag="input", ns="wsdl", nsmap=WSDL_NSMAP):
	headers: t.List[SOAPHeader] = [
		SOAPHeader(part="client"),
		SOAPHeader(part="service"),
		SOAPHeader(part="id"),
		SOAPHeader(part="protocolVersion"),
		SOAPHeader(part="userId")
	]
	body: SOAPBody = SOAPBody()


class XROADVersion(BaseXmlModel, tag="version", ns="xroad", nsmap=WSDL_NSMAP):
	version: str = "v1"


class SOAPOperationBinding(BaseXmlModel, tag="operation", ns="soap", nsmap=WSDL_NSMAP):
	soap_action: str = Attribute(name="soapAction")


class WSDLOperationBinding(BaseXmlModel, tag="operation", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = Attribute()
	operation: SOAPOperationBinding
	version: XROADVersion = XROADVersion()
	input: WSDLInputBinding = WSDLInputBinding()
	output: WSDLOutputBinding = WSDLOutputBinding()
	fault: WSDLFaultBinding = WSDLFaultBinding()


class SOAPBinding(BaseXmlModel, tag="binding", ns="soap", nsmap=WSDL_NSMAP):
	style: str = Attribute(default="document")
	transport: str = Attribute(default="http://schemas.xmlsoap.org/soap/http")


class WSDLBinding(BaseXmlModel, tag="binding", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = Attribute(default="serviceBinding")
	type: str = Attribute(default="tns:servicePortType")
	binding: SOAPBinding
	operations: t.List[WSDLOperationBinding]
