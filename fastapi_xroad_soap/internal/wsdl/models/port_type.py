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
from pydantic_xml import BaseXmlModel, element, attr
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
    message: str = attr(default="tns:FaultResponse")
    name: str = attr(default="FaultResponse")


class WSDLOutputPort(BaseXmlModel, tag="output", nsmap=WSDL_NSMAP):
    message: str = attr()
    name: str = attr()


class WSDLInputPort(BaseXmlModel, tag="input", nsmap=WSDL_NSMAP):
    message: str = attr()
    name: str = attr()


class WSDLDocumentation(BaseXmlModel, tag="documentation", nsmap=WSDL_NSMAP):
    title: str = element(ns='xro', nsmap=WSDL_NSMAP)
    notes: str = element(ns='xro', nsmap=WSDL_NSMAP)


class WSDLOperationPort(BaseXmlModel, tag="operation", ns="wsdl", nsmap=WSDL_NSMAP, skip_empty=True):
    documentation: t.Optional[WSDLDocumentation] = None
    input: t.Optional[WSDLInputPort] = None
    output: t.Optional[WSDLOutputPort] = None
    fault: WSDLFaultPort = WSDLFaultPort()
    name: str = attr()


class WSDLPortType(BaseXmlModel, tag="portType", ns="wsdl", nsmap=WSDL_NSMAP):
    name: str = attr(default="servicePortType")
    operations: t.List[WSDLOperationPort]
