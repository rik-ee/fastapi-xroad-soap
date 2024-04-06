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
from pydantic import Field, PrivateAttr, model_validator
from pydantic_xml import element
from fastapi_xroad_soap.internal import base as b


__all__ = [
	"CustomElement",
	"CustomElementSpec",
	"CustomElementInternal",
	"GoodCustomBody",
	"BadCustomBody"
]


class CustomElement(b.MessageBody):
	text: str = element(default='')

	def __new__(cls, *, raise_error: bool = False):
		kwargs = dict(raise_error=raise_error)
		return CustomElementSpec(**kwargs)

	@classmethod
	def _real_new_(cls, *args, **kwargs):
		return super().__new__(cls, *args, **kwargs)


class CustomElementSpec(b.BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.raise_error = kwargs.pop("raise_error")
		super().__init__(
			internal_type=CustomElementInternal,
			element_type=CustomElement,
			**kwargs
		)

	def get_a8n(self) -> t.Any:
		new = type("CustomElement", (CustomElementInternal,), dict(
			_raise_error=self.raise_error
		))
		return t.List[new]


class CustomElementInternal(CustomElement):
	ex_text: str = Field(exclude=True)
	_raise_error: str = PrivateAttr(default=None)

	def __new__(cls, *_, **__):
		return super()._real_new_()

	@model_validator(mode="after")
	def init_values(self):
		self.text = self.ex_text
		if self._raise_error == "raise":
			raise ValueError(self)
		delattr(self, "ex_text")
		return self


class GoodCustomBody(b.MessageBody):
	cust_elem = CustomElement(raise_error=False)


class BadCustomBody(b.MessageBody):
	cust_elem = CustomElement(raise_error=True)
