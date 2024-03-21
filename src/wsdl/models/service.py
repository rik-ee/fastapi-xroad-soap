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
from src.constants import NSMAP, service_url


__all__ = [
	"SOAPAddress",
	"WSDLPortBinding",
	"WSDLService"
]


class SOAPAddress(BaseXmlModel, tag="address", ns="soap", nsmap=NSMAP):
	location: str = attr(default=service_url())


class WSDLPortBinding(BaseXmlModel, tag="port", ns="wsdl", nsmap=NSMAP):
	binding: str = attr(default="tns:serviceBinding")
	name: str = attr(default="servicePort")
	address: SOAPAddress = SOAPAddress()


class WSDLService(BaseXmlModel, tag="service", nsmap=NSMAP):
	name: str = attr(default="xroadService")
	port: WSDLPortBinding = WSDLPortBinding()
