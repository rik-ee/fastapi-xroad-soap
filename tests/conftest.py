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
from __future__ import annotations
import typing as t
from pydantic import Field
from fastapi_xroad_soap.internal.base import (
	BaseElementSpec,
	MessageBody
)


__all__ = [
	"CustomModelObject",
	"CustomModelInternal",
	"CustomModelSpec",
	"CustomModelElement",
	"GoodCustomBody",
	"BadInstantiationCustomBody",
	"BadDeserializationCustomBody"
]


class CustomModelObject(MessageBody):
	text: str = Field(exclude=True, default='')

	def __new__(cls, text: str) -> CustomModelObject:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(CustomModelObject, CustomModelInternal(**kwargs))

	@classmethod
	def _real_new_(cls, sub_cls):
		return super().__new__(sub_cls)


class CustomModelInternal(CustomModelObject):
	text: str = Field(default=None)

	def __new__(cls, **__):
		return super()._real_new_(cls)


class CustomModelSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.raise_error_on_instantiation = kwargs.pop("raise_error_on_instantiation", False)
		self.raise_error_on_deserialization = kwargs.pop("raise_error_on_deserialization", False)
		super().__init__(
			element_type=CustomModelObject,
			internal_type=CustomModelInternal,
			**kwargs
		)

	def has_constraints(self) -> bool:
		return False

	def wsdl_type_name(self) -> bytes:
		return b''

	def init_instantiated_data(self, data: t.List) -> t.List:
		if self.raise_error_on_instantiation:
			raise ValueError("init_instantiated_data_value_error")
		return data

	def init_deserialized_data(self, data: t.List) -> t.List:
		if self.raise_error_on_deserialization:
			raise ValueError("init_deserialized_data_value_error")
		return data


class CustomModelElement(MessageBody):
	def __new__(
			cls,
			*,
			raise_error_on_instantiation: bool = False,
			raise_error_on_deserialization: bool = False
	) -> CustomModelObject:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(CustomModelObject, CustomModelSpec(**kwargs))


class GoodCustomBody(MessageBody):
	cust_elem = CustomModelElement()


class BadInstantiationCustomBody(MessageBody):
	cust_elem = CustomModelElement(raise_error_on_instantiation=True)


class BadDeserializationCustomBody(MessageBody):
	cust_elem = CustomModelElement(raise_error_on_deserialization=True)
