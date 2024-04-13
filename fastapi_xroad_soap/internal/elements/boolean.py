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
from ..base import BaseElementSpec


__all__ = ["BooleanSpec", "Boolean"]


class BooleanSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		super().__init__(
			element_type=bool,
			**kwargs
		)

	def init_instantiated_data(self, data: t.List[bool]) -> t.List[bool]:
		return data

	def init_deserialized_data(self, data: t.List[bool]) -> t.List[bool]:
		return data


class Boolean:
	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None
	) -> t.Union[bool, t.List[bool]]:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(bool, BooleanSpec(**kwargs))