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


__all__ = ["FloatSpec", "Float"]


class FloatSpec(BaseElementSpec, CommonValidators, NumberValidators):
	def __init__(self, **kwargs) -> None:
		self.min_value = kwargs.pop("min_value")
		self.max_value = kwargs.pop("max_value")
		self.enumerations = kwargs.pop("enumerations")
		self.pattern = kwargs.pop("pattern")
		super().__init__(
			element_type=float,
			**kwargs
		)

	def process(self, floater: float) -> float:
		self.validate_pattern(floater)
		self.validate_numeric_value(floater)
		self.validate_enumerations(floater)
		return floater

	def init_instantiated_data(self, data: t.List[float]) -> t.List[float]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[float]) -> t.List[float]:
		return [self.process(obj) for obj in data]


class Float:
	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None,
			min_value: t.Optional[float] = None,
			max_value: t.Optional[float] = None,
			enumerations: t.Optional[t.Type[Enum]] = None,
			pattern: t.Optional[str] = None
	) -> t.Union[float, t.List[float]]:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(float, FloatSpec(**kwargs))
