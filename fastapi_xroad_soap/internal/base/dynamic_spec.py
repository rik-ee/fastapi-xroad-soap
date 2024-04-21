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
from .base_element_spec import BaseElementSpec


__all__ = ["dynamic_spec"]


def dynamic_spec(_type: t.Type, **_kwargs) -> t.Any:
	class DynamicSpec(BaseElementSpec):
		def __init__(self) -> None:
			super().__init__(element_type=_type, **_kwargs)

		def init_instantiated_data(self, data: t.List) -> t.List:
			return data

		def init_deserialized_data(self, data: t.List) -> t.List:
			return data

		@property
		def has_constraints(self) -> bool:
			return False

		def wsdl_type_name(self, *, with_tns: bool = False) -> str:
			if with_tns:
				return f"tns:{_type.__name__}"
			return _type.__name__

	return DynamicSpec()
