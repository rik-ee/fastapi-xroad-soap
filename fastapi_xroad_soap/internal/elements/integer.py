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
from .validators import CommonValidators, NumberValidators


__all__ = ["IntegerSpec", "Integer"]


class IntegerSpec(BaseElementSpec, CommonValidators, NumberValidators):
	def __init__(self, **kwargs) -> None:
		self.min_value = kwargs.pop("min_value")
		self.max_value = kwargs.pop("max_value")
		self.total_digits = kwargs.pop("total_digits")
		self.enumerations = kwargs.pop("enumerations")
		self.pattern = kwargs.pop("pattern")
		super().__init__(
			element_type=int,
			**kwargs
		)

	def process(self, integer: int) -> int:
		self.validate_pattern(integer)
		self.validate_integer_digits(integer)
		self.validate_integer_value(integer)
		self.validate_enumerations(integer)
		return integer

	def init_instantiated_data(self, data: t.List[int]) -> t.List[int]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[int]) -> t.List[int]:
		return [self.process(obj) for obj in data]


class Integer:
	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None,
			min_value: t.Optional[int] = None,
			max_value: t.Optional[int] = None,
			total_digits: t.Optional[int] = None,
			enumerations: t.Optional[t.Type[Enum]] = None,
			pattern: t.Optional[str] = None
	) -> t.Union[int, t.List[int]]:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(int, IntegerSpec(**kwargs))
