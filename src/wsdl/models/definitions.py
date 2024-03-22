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
from typing import List
from pydantic_xml import BaseXmlModel, element, attr
from src.constants import WSDL_NSMAP
from .port_type import WSDLPortType
from .binding import WSDLBinding
from .service import WSDLService
from .schema import Schema


__all__ = [
    "WSDLTypes",
    "WSDLPart",
    "WSDLMessage",
    "WSDLDefinitions"
]


class WSDLTypes(BaseXmlModel, tag="types", nsmap=WSDL_NSMAP):
    service_schema: Schema


class WSDLPart(BaseXmlModel, tag="part", ns='wsdl', nsmap=WSDL_NSMAP):
    element: str = attr()
    name: str = attr(default="parameters")


class WSDLMessage(BaseXmlModel, tag="message", ns='wsdl', nsmap=WSDL_NSMAP):
    name: str = attr()
    parts: List[WSDLPart]


class WSDLDefinitions(BaseXmlModel, tag="definitions", ns="wsdl", nsmap=WSDL_NSMAP):
    target_ns: str = attr(name="targetNamespace", default="__TARGET_NAMESPACE_PLACEHOLDER__")
    name: str = attr()
    types: WSDLTypes = element()
    messages: List[WSDLMessage]
    port_type: WSDLPortType
    binding: WSDLBinding
    service: WSDLService
