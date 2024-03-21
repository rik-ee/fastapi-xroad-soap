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
from src.constants import NSMAP


__all__ = [
    "WSDLFaultPort",
    "WSDLOutputPort",
    "WSDLInputPort",
    "WSDLDocumentation",
    "WSDLOperationPort",
    "WSDLPortType"
]


class WSDLFaultPort(BaseXmlModel, tag="fault", nsmap=NSMAP):
    message: str = attr()
    name: str = attr()


class WSDLOutputPort(BaseXmlModel, tag="output", nsmap=NSMAP):
    message: str = attr()
    name: str = attr()


class WSDLInputPort(BaseXmlModel, tag="input", nsmap=NSMAP):
    message: str = attr()
    name: str = attr()


class WSDLDocumentation(BaseXmlModel, tag="documentation", nsmap=NSMAP):
    title: str = element(ns='xroad', nsmap=NSMAP)
    notes: str = element(ns='xroad', nsmap=NSMAP)


class WSDLOperationPort(BaseXmlModel, tag="operation", ns="wsdl", nsmap=NSMAP):
    documentation: WSDLDocumentation
    input: WSDLInputPort
    output: WSDLOutputPort
    fault: WSDLFaultPort
    name: str = attr()


class WSDLPortType(BaseXmlModel, tag="portType", ns="wsdl", nsmap=NSMAP):
    name: str = attr(default="servicePortType")
    operations: List[WSDLOperationPort]
