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
from .common import CommonSpecTypeA
from .validators import NumberValidators


__all__ = ["IntegerSpec", "Integer"]


class IntegerSpec(CommonSpecTypeA, NumberValidators):
	def __init__(self, **kwargs) -> None:
		self.total_digits = kwargs.pop("total_digits")
		super().__init__(
			element_type=int,
			**kwargs
		)


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
