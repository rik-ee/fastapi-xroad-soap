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


__all__ = [
	"Enumeration",
	"RegexPattern",
	"MinInclusive",
	"MaxInclusive",
	"MinExclusive",
	"MaxExclusive",
	"FractionDigits",
	"TotalDigits",
	"Length",
	"MinLength",
	"MaxLength",
	"WhiteSpace"
]


class Enumeration(BaseXmlModel, tag="enumeration"):
	value: str = Attribute()


class RegexPattern(BaseXmlModel, tag="pattern"):
	value: str = Attribute()


class MinInclusive(BaseXmlModel, tag="minInclusive"):
	value: str = Attribute()


class MaxInclusive(BaseXmlModel, tag="maxInclusive"):
	value: str = Attribute()


class MinExclusive(BaseXmlModel, tag="minExclusive"):
	value: str = Attribute()


class MaxExclusive(BaseXmlModel, tag="maxExclusive"):
	value: str = Attribute()


class FractionDigits(BaseXmlModel, tag="fractionDigits"):
	value: str = Attribute()


class TotalDigits(BaseXmlModel, tag="totalDigits"):
	value: str = Attribute()


class Length(BaseXmlModel, tag="length"):
	value: str = Attribute()


class MinLength(BaseXmlModel, tag="minLength"):
	value: str = Attribute()


class MaxLength(BaseXmlModel, tag="maxLength"):
	value: str = Attribute()


class WhiteSpace(BaseXmlModel, tag="whiteSpace"):
	value: t.Literal["preserve", "replace", "collapse"] = Attribute(default="preserve")
