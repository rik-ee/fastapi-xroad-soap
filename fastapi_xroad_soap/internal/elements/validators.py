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
import re
import typing as t
from enum import Enum


__all__ = [
	"CommonValidators",
	"StringValidators",
	"NumberValidators"
]


class CommonValidators:
	pattern: t.Optional[str] = None
	enumerations: t.Optional[t.Type[Enum]] = None

	def validate_pattern(self, obj: t.Any) -> None:
		string = str(obj)
		if self.pattern is not None:
			match = re.search(self.pattern, string)
			if match is None:
				raise ValueError(
					f"input value does not match regex "
					f"pattern '{self.pattern}' $${string}$$"
				)

	def validate_enumerations(self, obj: t.Any) -> None:
		if self.enumerations is not None:
			values = [item.value for item in self.enumerations]
			if obj not in values:
				raise ValueError(
					f"input value is not one of the "
					f"allowed values: {values} $${obj}$$"
				)


class StringValidators:
	length: t.Optional[int] = None
	min_length: t.Optional[int] = None
	max_length: t.Optional[int] = None
	whitespace: t.Literal["preserve", "replace", "collapse"] = "preserve"

	def validate_string_length(self, string: str) -> None:
		lstr = len(string)
		if self.length is not None and lstr != self.length:
			raise ValueError(
				f"input value length of {lstr} not equal "
				f"to {self.length} chars $${string}$$"
			)
		else:
			if self.min_length is not None and lstr < self.min_length:
				raise ValueError(
					f"input value length does not meet minimum requirement "
					f"of {self.min_length} chars $${string}$$"
				)
			if self.max_length is not None and lstr > self.max_length:
				raise ValueError(
					f"input value length exceeds maximum allowable "
					f"length of {self.max_length} chars $${string}$$"
				)

	def process_whitespace(self, string) -> str:
		if self.whitespace == "replace":
			return re.sub(r'\s', ' ', string)
		elif self.whitespace == "collapse":
			return re.sub(r'\s+', ' ', string)
		return string


class NumberValidators:
	min_value: t.Optional[int] = None
	max_value: t.Optional[int] = None
	total_digits: t.Optional[int] = None

	def validate_integer_digits(self, integer: int) -> None:
		if self.total_digits is not None:
			int_len = len(str(abs(integer)))
			if int_len > self.total_digits:
				raise ValueError(
					f"input value digits count exceeds the maximum allowable "
					f"count of {self.total_digits} digits $${integer}$$"
				)

	def validate_integer_value(self, integer: int) -> None:
		if self.min_value is not None and integer < self.min_value:
			raise ValueError(
				f"input value is less than the minimal value "
				f"of {self.min_value} $${integer}$$"
			)
		if self.max_value is not None and integer > self.max_value:
			raise ValueError(
				f"input value is greater than the maximum allowable "
				f"value of {self.max_value} $${integer}$$"
			)
