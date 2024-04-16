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
import hashlib
import typing as t
from ..base import BaseElementSpec
from ..uid_gen import UIDGenerator
from .validators import (
	CommonValidators,
	NumberValidators,
	StringValidators
)


__all__ = ["CommonSpecTypeA", "CommonSpecTypeB"]


class CommonSpecTypeA(BaseElementSpec, CommonValidators, NumberValidators):
	def __init__(self, element_type: t.Any, **kwargs) -> None:
		self.min_value = kwargs.pop("min_value", None)
		self.max_value = kwargs.pop("max_value", None)
		self.total_digits = kwargs.pop("total_digits", None)
		self.enumerations = kwargs.pop("enumerations", None)
		self.pattern = kwargs.pop("pattern", None)
		super().__init__(
			element_type=element_type,
			**kwargs
		)

	def process(self, obj: t.Any) -> t.Any:
		self.validate_pattern(obj)
		self.validate_total_digits(obj)
		self.validate_min_max_value(obj)
		self.validate_enumerations(obj)
		return obj

	def init_instantiated_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	def init_deserialized_data(self, data: t.List[t.Any]) -> t.List[t.Any]:
		return [self.process(obj) for obj in data]

	def has_constraints(self) -> bool:
		return any([
			attr is not None for attr in [
				self.min_value,
				self.max_value,
				self.total_digits,
				self.pattern,
				self.enumerations
			]
		])

	def signature(self) -> str:
		fp_str = ''.join([
			repr(self.min_value),
			repr(self.max_value),
			repr(self.total_digits),
			repr(self.pattern),
			(
				repr(vars(self.enumerations)) if
				isinstance(self.enumerations, (type, object))
				else repr(self.enumerations)
			)
		]).encode()
		digest = hashlib.shake_128(fp_str).digest(10)
		keygen = UIDGenerator(mode="key")
		return keygen.generate(digest)


class CommonSpecTypeB(BaseElementSpec, CommonValidators, StringValidators):
	def __init__(self, element_type: t.Any, **kwargs) -> None:
		self.length = kwargs.pop("length", None)
		self.min_length = kwargs.pop("min_length", None)
		self.max_length = kwargs.pop("max_length", None)
		self.enumerations = kwargs.pop("enumerations", None)
		self.pattern = kwargs.pop("pattern", None)
		self.whitespace = (
			kwargs.pop("whitespace", None)
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

	def signature(self) -> str:
		fp_str = ''.join([
			repr(self.length),
			repr(self.min_length),
			repr(self.max_length),
			repr(self.whitespace),
			repr(self.pattern),
			(
				repr(vars(self.enumerations)) if
				hasattr(self.enumerations, "__dict__")
				else repr(self.enumerations)
			)
		]).encode()
		digest = hashlib.shake_128(fp_str).digest(10)
		keygen = UIDGenerator(mode="key")
		return keygen.generate(digest)
