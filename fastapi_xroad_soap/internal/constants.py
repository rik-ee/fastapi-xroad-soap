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
from enum import Enum


__all__ = [
    "XSD",
    "ENV_NSMAP",
    "XRO_NSMAP",
    "IDEN_NSMAP",
    "HEADER_NSMAP",
    "WSDL_NSMAP",
    "A8nType"
]


XSD = "http://www.w3.org/2001/XMLSchema"
ENV_NSMAP = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/"}
XRO_NSMAP = {"xro": "http://x-road.eu/xsd/xroad.xsd"}
IDEN_NSMAP = {"iden": "http://x-road.eu/xsd/identifiers"}
HEADER_NSMAP = {**ENV_NSMAP, **XRO_NSMAP, **IDEN_NSMAP}
WSDL_NSMAP = {
    "wsdl": "http://schemas.xmlsoap.org/wsdl/",
    "soap": "http://schemas.xmlsoap.org/wsdl/soap/",
    "wsi": "http://ws-i.org/profiles/basic/1.1/xsd",
    **XRO_NSMAP
}


class A8nType(Enum):
    LIST = "list"
    OPT = "optional"
    MAND = "mandatory"
    ABSENT = "absent"
