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
from pydantic_xml import BaseXmlModel, attr
from fastapi_xroad_soap.internal.constants import WSDL_NSMAP


__all__ = [
	"SOAPAddress",
	"WSDLPortBinding",
	"WSDLService"
]


class SOAPAddress(BaseXmlModel, tag="address", ns="soap", nsmap=WSDL_NSMAP):
	location: str = attr()


class WSDLPortBinding(BaseXmlModel, tag="port", ns="wsdl", nsmap=WSDL_NSMAP):
	binding: str = attr(default="tns:serviceBinding")
	name: str = attr(default="servicePort")
	address: SOAPAddress = SOAPAddress()


class WSDLService(BaseXmlModel, tag="service", nsmap=WSDL_NSMAP):
	name: str = attr(default="xroadService")
	port: WSDLPortBinding = WSDLPortBinding()
