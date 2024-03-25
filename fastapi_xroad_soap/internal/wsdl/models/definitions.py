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
from fastapi_xroad_soap.internal.envelope import BaseXmlModel, Attribute, Element
from fastapi_xroad_soap.internal.constants import WSDL_NSMAP
from fastapi_xroad_soap.internal.wsdl.models.port_type import WSDLPortType
from fastapi_xroad_soap.internal.wsdl.models.binding import WSDLBinding
from fastapi_xroad_soap.internal.wsdl.models.service import WSDLService
from fastapi_xroad_soap.internal.wsdl.models.schema import Schema


__all__ = [
    "WSDLTypes",
    "WSDLPart",
    "WSDLMessage",
    "WSDLDefinitions"
]


class WSDLTypes(BaseXmlModel, tag="types", nsmap=WSDL_NSMAP):
    service_schema: Schema


class WSDLPart(BaseXmlModel, tag="part", ns='wsdl', nsmap=WSDL_NSMAP):
    element: str = Attribute()
    name: str = Attribute(default="parameters")


class WSDLMessage(BaseXmlModel, tag="message", ns='wsdl', nsmap=WSDL_NSMAP):
    name: str = Attribute()
    parts: t.List[WSDLPart]


class WSDLDefinitions(BaseXmlModel, tag="definitions", ns="wsdl", nsmap=WSDL_NSMAP):
    target_ns: str = Attribute(name="targetNamespace")
    name: str = Attribute()
    types: WSDLTypes = Element()
    messages: t.List[WSDLMessage]
    port_type: WSDLPortType
    binding: WSDLBinding
    service: WSDLService
