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


__all__ = [
    "WSDLFaultPort",
    "WSDLOutputPort",
    "WSDLInputPort",
    "WSDLDocumentation",
    "WSDLOperationPort",
    "WSDLPortType"
]


class WSDLFaultPort(BaseXmlModel, tag="fault", nsmap=WSDL_NSMAP):
    message: str = Attribute()
    name: str = Attribute()


class WSDLOutputPort(BaseXmlModel, tag="output", nsmap=WSDL_NSMAP):
    message: str = Attribute()
    name: str = Attribute()


class WSDLInputPort(BaseXmlModel, tag="input", nsmap=WSDL_NSMAP):
    message: str = Attribute()
    name: str = Attribute()


class WSDLDocumentation(BaseXmlModel, tag="documentation", nsmap=WSDL_NSMAP):
    title: str = Element(ns='xroad', nsmap=WSDL_NSMAP)
    notes: str = Element(ns='xroad', nsmap=WSDL_NSMAP)


class WSDLOperationPort(BaseXmlModel, tag="operation", ns="wsdl", nsmap=WSDL_NSMAP):
    documentation: WSDLDocumentation
    input: WSDLInputPort
    output: WSDLOutputPort
    fault: WSDLFaultPort
    name: str = Attribute()


class WSDLPortType(BaseXmlModel, tag="portType", ns="wsdl", nsmap=WSDL_NSMAP):
    name: str = Attribute(default="servicePortType")
    operations: t.List[WSDLOperationPort]
