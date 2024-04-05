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
from pydantic_xml import BaseXmlModel, attr
from ..constants import WSDL_NSMAP


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
	name: str = attr(default="FaultResponse")
	use: str = attr(default="literal")


class SOAPBody(BaseXmlModel, tag="body", ns="soap", nsmap=WSDL_NSMAP):
	use: str = attr(default="literal")


class SOAPHeader(BaseXmlModel, tag="header", ns="soap", nsmap=WSDL_NSMAP):
	message: str = attr(default="tns:xroadHeader")
	use: str = attr(default="literal")
	part: str = attr()


class WSDLFaultBinding(BaseXmlModel, tag="fault", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = attr(default="FaultResponse")
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
	soap_action: str = attr(name="soapAction")


class WSDLOperationBinding(BaseXmlModel, tag="operation", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = attr()
	operation: SOAPOperationBinding
	version: XROADVersion = XROADVersion()
	input: WSDLInputBinding = WSDLInputBinding()
	output: WSDLOutputBinding = WSDLOutputBinding()
	fault: WSDLFaultBinding = WSDLFaultBinding()


class SOAPBinding(BaseXmlModel, tag="binding", ns="soap", nsmap=WSDL_NSMAP):
	style: str = attr(default="document")
	transport: str = attr(default="http://schemas.xmlsoap.org/soap/http")


class WSDLBinding(BaseXmlModel, tag="binding", ns="wsdl", nsmap=WSDL_NSMAP):
	name: str = attr(default="serviceBinding")
	type: str = attr(default="tns:servicePortType")
	binding: SOAPBinding
	operations: t.List[WSDLOperationBinding]
