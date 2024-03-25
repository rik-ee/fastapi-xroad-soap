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
from fastapi_xroad_soap.internal.envelope import BaseXmlModel, Attribute
from fastapi_xroad_soap.internal.constants import WSDL_NSMAP
from fastapi_xroad_soap.internal.wsdl.models.restrictions import (
    StringRestriction,
    IntegerRestriction,
    DecimalRestriction,
    FloatRestriction,
    DoubleRestriction,
    DateRestriction,
    TimeRestriction,
    DateTimeRestriction,
    DurationRestriction,
    AnyURIRestriction
)


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
    name: str = Attribute()
    restriction: t.Union[
        StringRestriction,
        IntegerRestriction,
        DecimalRestriction,
        FloatRestriction,
        DoubleRestriction,
        DateRestriction,
        TimeRestriction,
        DateTimeRestriction,
        DurationRestriction,
        AnyURIRestriction
    ]


class AnyXML(BaseXmlModel, tag="any"):
    process_contents: str = Attribute(default="lax")


class Element(BaseXmlModel, tag="element"):
    name: str = Attribute()
    type: str = Attribute()
    min_occurs: t.Union[str, None] = Attribute(name="minOccurs", default=None)
    max_occurs: t.Union[str, None] = Attribute(name="maxOccurs", default=None)


class Sequence(BaseXmlModel, tag="sequence"):
    elements: t.List[t.Union[Element, AnyXML]]


class ComplexType(BaseXmlModel, tag="complexType"):
    name: str = Attribute()
    sequence: Sequence


class Import(BaseXmlModel, tag="import"):
    schema_loc: str = Attribute(name="schemaLocation")
    namespace: str = Attribute()


class Include(BaseXmlModel, tag="include"):
    schema_loc: str = Attribute(name="schemaLocation")


class Schema(BaseXmlModel, tag="schema"):
    xmlns: str = Attribute(default=WSDL_NSMAP["xs"])
    target_ns: str = Attribute(name="targetNamespace")
    imports: t.List[Import]
    includes: t.List[Include]
    elements: t.List[Element]
    complex_types: t.List[ComplexType]
    simple_types: t.List[SimpleType]
