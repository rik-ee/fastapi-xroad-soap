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
	value: str = attr()


class RegexPattern(BaseXmlModel, tag="pattern"):
	value: str = attr()


class MinInclusive(BaseXmlModel, tag="minInclusive"):
	value: str = attr()


class MaxInclusive(BaseXmlModel, tag="maxInclusive"):
	value: str = attr()


class MinExclusive(BaseXmlModel, tag="minExclusive"):
	value: str = attr()


class MaxExclusive(BaseXmlModel, tag="maxExclusive"):
	value: str = attr()


class FractionDigits(BaseXmlModel, tag="fractionDigits"):
	value: str = attr()


class TotalDigits(BaseXmlModel, tag="totalDigits"):
	value: str = attr()


class Length(BaseXmlModel, tag="length"):
	value: str = attr()


class MinLength(BaseXmlModel, tag="minLength"):
	value: str = attr()


class MaxLength(BaseXmlModel, tag="maxLength"):
	value: str = attr()


class WhiteSpace(BaseXmlModel, tag="whiteSpace"):
	value: t.Literal["preserve", "replace", "collapse"] = attr(default="preserve")
