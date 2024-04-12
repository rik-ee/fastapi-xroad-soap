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
from enum import Enum
from ..base import BaseElementSpec
from .validators import CommonValidators, StringValidators


__all__ = ["StringSpec", "String"]


class StringSpec(BaseElementSpec, CommonValidators, StringValidators):
	def __init__(self, **kwargs) -> None:
		self.length = kwargs.pop("length")
		self.min_length = kwargs.pop("min_length")
		self.max_length = kwargs.pop("max_length")
		self.enumerations = kwargs.pop("enumerations")
		self.pattern = kwargs.pop("pattern")
		self.whitespace = kwargs.pop("whitespace")
		super().__init__(
			element_type=str,
			**kwargs
		)

	def process(self, string: str) -> str:
		self.validate_string_length(string)
		self.validate_pattern(string)
		self.validate_enumerations(string)
		return self.process_whitespace(string)

	def init_instantiated_data(self, data: t.List[str]) -> t.List[str]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[str]) -> t.List[str]:
		return [self.process(obj) for obj in data]


class String:
	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None,
			length: t.Optional[int] = None,
			min_length: t.Optional[int] = None,
			max_length: t.Optional[int] = None,
			enumerations: t.Optional[t.Type[Enum]] = None,
			pattern: t.Optional[str] = None,
			whitespace: t.Literal["preserve", "replace", "collapse"] = "preserve"
	) -> t.Union[str, t.List[str]]:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(str, StringSpec(**kwargs))
