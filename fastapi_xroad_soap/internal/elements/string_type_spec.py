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
from .validators import CommonValidators, StringValidators


__all__ = ["StringTypeSpec"]


class StringTypeSpec(BaseElementSpec, CommonValidators, StringValidators):
	def __init__(self, element_type: t.Any, **kwargs) -> None:
		self.length = kwargs.get("length", None)
		self.min_length = kwargs.get("min_length", None)
		self.max_length = kwargs.get("max_length", None)
		self.enumerations = kwargs.get("enumerations", None)
		self.pattern = kwargs.get("pattern", None)
		self.whitespace = (
			kwargs.get("whitespace", None)
			or t.cast(t.Literal, "preserve")
		)
		super().__init__(
			element_type=element_type,
			**kwargs
		)

	def process(self, obj: t.Any) -> t.Any:
		self.validate_string_length(obj)
		self.validate_pattern(obj)
		self.validate_enumerations(obj)
		return self.process_whitespace(obj)

	def init_instantiated_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	@property
	@functools.lru_cache(maxsize=1)
	def has_constraints(self) -> bool:
		return self.whitespace != 'preserve' or any(
			attr is not None for attr in [
				self.length,
				self.min_length,
				self.max_length,
				self.pattern,
				self.enumerations
			]
		)

	@property
	@functools.lru_cache(maxsize=1)
	def wsdl_type_name(self) -> str:
		return self._compute_wsdl_type_name(
			default=self.default_wsdl_type_name,
			data=[
				self.length,
				self.min_length,
				self.max_length,
				self.whitespace,
				self.enumerations,
				self.pattern
			]
		)

	@property
	@abstractmethod
	def default_wsdl_type_name(self) -> str: ...
