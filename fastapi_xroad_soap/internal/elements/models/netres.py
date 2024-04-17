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
from pydantic import AnyUrl
from ..string_type_spec import StringTypeSpec


__all__ = ["NetResSpec", "NetRes"]


class NetResSpec(StringTypeSpec):
	def __init__(self, **kwargs) -> None:
		super().__init__(element_type=AnyUrl, **kwargs)

	@property
	def _default_wsdl_type_name(self) -> str:
		return "anyURI"


class NetRes:
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
			pattern: t.Optional[str] = None
	) -> t.Union[AnyUrl, t.List[AnyUrl]]:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(AnyUrl, NetResSpec(**kwargs))
