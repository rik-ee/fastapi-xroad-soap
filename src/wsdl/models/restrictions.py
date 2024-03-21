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
from .conditions import *


__all__ = [
	"StringRestriction",
	"IntegerRestriction",
	"DecimalRestriction",
	"FloatRestriction",
	"DoubleRestriction",
	"DateRestriction",
	"TimeRestriction",
	"DateTimeRestriction",
	"DurationRestriction",
	"AnyURIRestriction"
]


class StringRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="string")
	length: Union[Length, None] = None
	min_length: Union[MinLength, None] = None
	max_length: Union[MaxLength, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class IntegerRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="integer")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	total_digits: Union[TotalDigits, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class DecimalRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="decimal")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	total_digits: Union[TotalDigits, None] = None
	fraction_digits: Union[FractionDigits, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class FloatRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="float")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class DoubleRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="double")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class DateRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="date")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class TimeRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="time")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class DateTimeRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="dateTime")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class DurationRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="duration")
	min_inclusive: Union[MinInclusive, None] = None
	max_inclusive: Union[MaxInclusive, None] = None
	min_exclusive: Union[MinExclusive, None] = None
	max_exclusive: Union[MaxExclusive, None] = None
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None


class AnyURIRestriction(BaseXmlModel, tag="restriction"):
	base: str = attr(default="anyURI")
	enumerations: Union[List[Enumeration], None] = None
	pattern: Union[RegexPattern, None] = None
