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
from typing import List, Union
from pydantic_xml import BaseXmlModel, attr
from src.constants import NSMAP, wsdl_url
from .restrictions import *


__all__ = [
    "SimpleType",
    "AnyXML",
    "Element",
    "Sequence",
    "ComplexType",
    "Import",
    "Include",
    "Schema"
]


class SimpleType(BaseXmlModel, tag="simpleType"):
    name: str = attr()
    restriction: Union[
        StringRestriction,
        IntegerRestriction,
        DecimalRestriction,
        FloatRestriction,
        DoubleRestriction,
        DateRestriction,
        TimeRestriction
    ]


class AnyXML(BaseXmlModel, tag="any"):
    process_contents: str = attr(default="lax")


class Element(BaseXmlModel, tag="element"):
    name: str = attr()
    type: str = attr()
    min_occurs: Union[str, None] = attr(name="minOccurs", default=None)
    max_occurs: Union[str, None] = attr(name="maxOccurs", default=None)


class Sequence(BaseXmlModel, tag="sequence"):
    elements: List[Union[Element, AnyXML]]


class ComplexType(BaseXmlModel, tag="complexType"):
    name: str = attr()
    sequence: Sequence


class Import(BaseXmlModel, tag="import"):
    schema_loc: str = attr(name="schemaLocation")
    namespace: str = attr()


class Include(BaseXmlModel, tag="include"):
    schema_loc: str = attr(name="schemaLocation")


class Schema(BaseXmlModel, tag="schema"):
    xmlns: str = attr(default=NSMAP["xs"])
    target_ns: str = attr(name="targetNamespace", default=wsdl_url())
    imports: List[Import]
    includes: List[Include]
    elements: List[Element]
    complex_types: List[ComplexType]
    simple_types: List[SimpleType]
