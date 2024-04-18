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
from datetime import time
from ..numeric_type_spec import NumericTypeSpec


__all__ = ["TimeSpec", "Time"]


class TimeSpec(NumericTypeSpec):
	def __init__(self, **kwargs) -> None:
		super().__init__(element_type=time, **kwargs)

	@property
	def default_wsdl_type_name(self) -> str:
		return "time"


class Time:
	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None,
			min_value: t.Optional[time] = None,
			max_value: t.Optional[time] = None,
			enumerations: t.Optional[t.Type[Enum]] = None,
			pattern: t.Optional[str] = None
	) -> time:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(time, TimeSpec(**kwargs))
