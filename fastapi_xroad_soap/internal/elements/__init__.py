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
from .boolean import BooleanSpec, Boolean
from .date import DateSpec, Date
from .datetime import DateTimeSpec, DateTime
from .time import TimeSpec, Time
from .float import FloatSpec, Float
from .integer import IntegerSpec, Integer
from .string import StringSpec, String
from .netres import NetResSpec, NetRes
from .swaref import (
	SwaRefFile,
	SwaRefInternal,
	SwaRefSpec,
	SwaRefElement,
	SwaRef
)


__all__ = [
	"BooleanSpec", "Boolean",
	"DateSpec", "Date",
	"DateTimeSpec", "DateTime",
	"TimeSpec", "Time",
	"FloatSpec", "Float",
	"IntegerSpec", "Integer",
	"StringSpec", "String",
	"NetResSpec", "NetRes",
	"SwaRefFile",
	"SwaRefInternal",
	"SwaRefSpec",
	"SwaRefElement",
	"SwaRef"
]
