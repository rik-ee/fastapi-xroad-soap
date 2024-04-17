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
from .conditions import (
	Enumeration,
	RegexPattern,
	MinInclusive,
	MaxInclusive,
	TotalDigits,
	Length,
	MinLength,
	MaxLength,
	WhiteSpace
)


__all__ = [
	"NumericTypeRestriction",
	"StringTypeRestriction"
]


class NumericTypeRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr()
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	total_digits: t.Union[TotalDigits, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	pattern: t.Union[RegexPattern, None] = None


class StringTypeRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr()
	length: t.Union[Length, None] = None
	min_length: t.Union[MinLength, None] = None
	max_length: t.Union[MaxLength, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None
