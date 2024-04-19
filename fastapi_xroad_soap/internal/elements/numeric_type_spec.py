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
import functools
import typing as t
from abc import abstractmethod
from ..base import BaseElementSpec
from .validators import CommonValidators, NumberValidators


__all__ = ["NumericTypeSpec"]


class NumericTypeSpec(BaseElementSpec, CommonValidators, NumberValidators):
	def __init__(self, element_type: t.Any, **kwargs) -> None:
		self.min_value = kwargs.get("min_value", None)
		self.max_value = kwargs.get("max_value", None)
		self.total_digits = kwargs.get("total_digits", None)
		self.enumerations = kwargs.get("enumerations", None)
		self.pattern = kwargs.get("pattern", None)
		self.validate_enum_value_types(element_type)
		super().__init__(
			element_type=element_type,
			**kwargs
		)

	def process(self, obj: t.Any) -> t.Any:
		self.validate_type(obj, self.element_type)
		self.validate_pattern(obj)
		self.validate_total_digits(obj)
		self.validate_min_max_value(obj)
		self.validate_enumerations(obj)
		return obj

	def init_instantiated_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	@property
	@functools.lru_cache(maxsize=1)
	def has_constraints(self) -> bool:
		return any([
			attr is not None for attr in [
				self.min_value,
				self.max_value,
				self.total_digits,
				self.enumerations,
				self.pattern
			]
		])

	def wsdl_type_name(self, *, with_tns: bool = False) -> str:
		return self._assemble_wsdl_type_name(
			signature=self._compute_signature(
				self.min_value,
				self.max_value,
				self.total_digits,
				self.enumerations,
				self.pattern
			),
			with_tns=with_tns
		)

	@property
	@abstractmethod
	def default_wsdl_type_name(self) -> str: ...
