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
from pydantic_xml import BaseXmlModel, attr
from fastapi_xroad_soap.internal.constants import WSDL_NSMAP
from .restrictions import (
    NumericTypeRestriction,
    StringTypeRestriction
)


__all__ = [
    "AnyXML",
    "Element",
    "Sequence",
    "ComplexType",
    "SimpleType",
    "Import",
    "Include",
    "Schema"
]


class AnyXML(BaseXmlModel, tag="any"):
    process_contents: str = attr(name="processContents", default="lax")


class Element(BaseXmlModel, tag="element", skip_empty=True):
    name: str = attr()
    type: str = attr()
    min_occurs: t.Union[str, None] = attr(name="minOccurs", default=None)
    max_occurs: t.Union[str, None] = attr(name="maxOccurs", default=None)


class Sequence(BaseXmlModel, tag="sequence"):
    elements: t.List[t.Union[Element, AnyXML]]


class ComplexType(BaseXmlModel, tag="complexType"):
    name: str = attr()
    sequence: Sequence


class SimpleType(BaseXmlModel, tag="simpleType"):
    name: str = attr()
    restriction: t.Union[
        NumericTypeRestriction,
        StringTypeRestriction
    ]


class Import(BaseXmlModel, tag="import"):
    namespace: str = attr()
    schema_loc: str = attr(name="schemaLocation")


class Include(BaseXmlModel, tag="include"):
    schema_loc: str = attr(name="schemaLocation")


class Schema(BaseXmlModel, tag="schema"):
    xmlns: str = attr(default=WSDL_NSMAP["xsd"])
    target_ns: str = attr(name="targetNamespace")
    imports: t.List[Import]
    includes: t.List[Include]
    elements: t.List[Element]
    complex_types: t.List[ComplexType]
    simple_types: t.List[SimpleType]
