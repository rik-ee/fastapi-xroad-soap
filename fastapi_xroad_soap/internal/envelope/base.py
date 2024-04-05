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
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import PrivateAttr, model_validator
from pydantic_xml import model


__all__ = [
	"A8nType",
	"BaseElementSpec",
	"ElementSpecMeta",
	"CompositeMeta",
	"MessageBody",
	"MessageBodyType"
]


class A8nType(Enum):
	LIST = "list"
	OPT = "optional"
	MAND = "mandatory"
	ABSENT = "absent"


class BaseElementSpec(ABC):
	tag: t.Optional[str]
	ns: t.Optional[str]
	nsmap: t.Optional[t.Dict[str, str]]
	element_type: t.Type[MessageBody]
	a8n_type: A8nType
	min_occurs: int
	max_occurs: int

	@abstractmethod
	def get_element(self, attr: str) -> model.XmlEntityInfo: ...

	@abstractmethod
	def get_a8n(self, anno: t.Any) -> t.Any: ...

	def store_user_defined_a8n(self, a8n: t.Any, attr: str, name: str) -> None:
		if a8n in [A8nType.ABSENT, self.element_type]:
			self.a8n_type = A8nType.MAND
			return
		elif a8n in [t.Optional, t.Union, t.List, list]:
			raise TypeError(
				f"Not permitted to provide '{a8n}' "
				f"annotation without a type argument."
			)
		if args := t.get_args(a8n):
			if len(args) == 1 and args[0] != self.element_type:
				raise TypeError(
					f"Single annotation argument for class '{name}' "
					f"attribute '{attr}' must be '{self.element_type}'."
				)
			for arg in args:
				if arg is type(None):
					continue
				elif arg == self.element_type:
					continue
				raise TypeError(
					f"Invalid annotation argument '{arg.__name__}' "
					f"for '{name}' class attribute '{attr}'."
				)
		if origin := t.get_origin(a8n):
			if origin == list:
				self.a8n_type = A8nType.LIST
				return
			elif "Union" in origin.__name__:
				self.a8n_type = A8nType.OPT
				return
		raise TypeError(
			f"Unsupported annotation '{a8n}' for "
			f"class '{name}' attribute '{attr}'."
		)


class ElementSpecMeta(type):
	def __new__(cls, name, bases, class_fields, **kwargs):
		class_a8ns: dict = class_fields.get("__annotations__", {})
		element_specs = dict()
		for attr, obj in class_fields.items():
			if isinstance(obj, BaseElementSpec):
				a8n = class_a8ns.get(attr, A8nType.ABSENT)
				obj.store_user_defined_a8n(a8n, attr, name)
				class_fields[attr] = obj.get_element(attr)
				class_a8ns[attr] = obj.get_a8n(a8n)
				element_specs[attr] = obj
		class_fields["_element_specs"] = element_specs
		return super().__new__(cls, name, bases, class_fields, **kwargs)


class CompositeMeta(ElementSpecMeta, model.XmlModelMeta):
	pass


class MessageBody(model.BaseXmlModel, metaclass=CompositeMeta, search_mode='unordered', skip_empty=True):
	_element_specs: t.Dict[str, BaseElementSpec] = PrivateAttr(default_factory=dict)

	@model_validator(mode="after")
	def validate(self):
		if not self._element_specs:
			return self
		for k, v in vars(self).items():
			spec = self._element_specs.get(k)
			if spec is None:
				continue
			count = len(v)
			if count > 1 and spec.a8n_type in [A8nType.MAND, A8nType.OPT]:
				raise ValueError(f"only one {spec.tag} element is allowed")
			elif count == 0 and spec.a8n_type == A8nType.MAND:
				raise ValueError(f"must provide at least one {spec.tag} element")
			elif spec.a8n_type == A8nType.LIST:
				if count < spec.min_occurs:
					raise ValueError(
						f"expected at least {spec.min_occurs} "
						f"{spec.tag} elements, got {count}"
					)
				elif isinstance(spec.max_occurs, int) and count > spec.max_occurs:
					raise ValueError(
						f"expected at most {spec.max_occurs} "
						f"{spec.tag} elements, got {count}"
					)
				return self
			setattr(self, k, v[0] if count == 1 else None)
		self._element_specs.clear()
		return self


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)
