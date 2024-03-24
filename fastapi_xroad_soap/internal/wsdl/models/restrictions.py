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
from fastapi_xroad_soap.internal.wsdl.models.conditions import (
	Enumeration,
	RegexPattern,
	MinInclusive,
	MaxInclusive,
	MinExclusive,
	MaxExclusive,
	FractionDigits,
	TotalDigits,
	Length,
	MinLength,
	MaxLength,
	WhiteSpace
)


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
	base: str = Attribute(default="string")
	length: t.Union[Length, None] = None
	min_length: t.Union[MinLength, None] = None
	max_length: t.Union[MaxLength, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class IntegerRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="integer")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	total_digits: t.Union[TotalDigits, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	pattern: t.Union[RegexPattern, None] = None


class DecimalRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="decimal")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	total_digits: t.Union[TotalDigits, None] = None
	fraction_digits: t.Union[FractionDigits, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class FloatRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="float")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class DoubleRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="double")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class DateRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="date")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	pattern: t.Union[RegexPattern, None] = None


class TimeRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="time")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class DateTimeRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="dateTime")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class DurationRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="duration")
	min_inclusive: t.Union[MinInclusive, None] = None
	max_inclusive: t.Union[MaxInclusive, None] = None
	min_exclusive: t.Union[MinExclusive, None] = None
	max_exclusive: t.Union[MaxExclusive, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
	pattern: t.Union[RegexPattern, None] = None


class AnyURIRestriction(BaseXmlModel, tag="restriction"):
	base: str = Attribute(default="anyURI")
	length: t.Union[Length, None] = None
	min_length: t.Union[MinLength, None] = None
	max_length: t.Union[MaxLength, None] = None
	pattern: t.Union[RegexPattern, None] = None
	enumerations: t.Union[t.List[Enumeration], None] = None
	whiteSpace: t.Union[WhiteSpace, None] = None
