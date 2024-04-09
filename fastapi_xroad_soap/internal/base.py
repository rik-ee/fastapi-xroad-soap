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
import inflection
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import PrivateAttr, ValidationInfo, model_validator
from pydantic_xml import model, element


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
	min_occurs: int
	max_occurs: t.Union[int, t.Literal["unbounded"]]
	element_type: t.Type[MessageBody]
	internal_type: t.Optional[t.Type[MessageBody]]
	a8n_type: t.Union[A8nType, None]

	def __init__(
			self,
			element_type: t.Type[MessageBody],
			internal_type: t.Optional[t.Type[MessageBody]] = None,
			**kwargs
	) -> None:
		self.tag = kwargs.get("tag")
		self.ns = kwargs.get("ns")
		self.nsmap = kwargs.get("nsmap")
		self.min_occurs = kwargs.get("min_occurs") or 0
		self.max_occurs = kwargs.get("max_occurs") or "unbounded"
		self.element_type = element_type
		self.internal_type = internal_type
		self.a8n_type = None

	@abstractmethod
	def init_instantiated_data(self, data: t.List[t.Any]) -> t.List[t.Any]: ...

	@abstractmethod
	def init_deserialized_data(self, data: t.List[t.Any]) -> t.List[t.Any]: ...

	def get_element_a8n(self) -> t.Type[t.List[t.Any]]:
		return t.List[self.internal_type or self.element_type]

	def get_element(self, attr: str) -> model.XmlEntityInfo:
		return element(
			tag=self.tag or inflection.camelize(attr),
			ns=self.ns or '',
			nsmap=self.nsmap or dict(),
			default_factory=list
		)

	def set_a8n_type_from(self, a8n: t.Any, attr: str, name: str) -> None:
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
				arg_name = "None" if arg is type(None) else arg.__name__
				raise TypeError(
					f"Invalid annotation argument '{arg_name}' "
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
				obj.set_a8n_type_from(a8n, attr, name)
				class_fields[attr] = obj.get_element(attr)
				class_a8ns[attr] = obj.get_element_a8n()
				element_specs[attr] = obj
		class_fields["__annotations__"] = class_a8ns
		class_fields["_element_specs"] = element_specs
		return super().__new__(cls, name, bases, class_fields, **kwargs)


class CompositeMeta(ElementSpecMeta, model.XmlModelMeta):
	pass


class MessageBody(model.BaseXmlModel, metaclass=CompositeMeta, search_mode='unordered', skip_empty=True):
	_element_specs: t.Dict[str, BaseElementSpec] = PrivateAttr(default_factory=dict)

	@staticmethod
	def _validate_list(attr: str, data: t.List[MessageBody], spec: BaseElementSpec):
		if not isinstance(data, list):
			raise ValueError(
				f"expected attribute '{attr}' value to be a list, "
				f"but received '{type(data).__name__}' instead."
			)
		count = len(data)
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
		expected = spec.internal_type or spec.element_type
		for item in data:
			if not isinstance(item, expected):
				raise ValueError(
					f"unexpected type '{type(item).__name__}' "
					f"in list for argument '{attr}'"
				)

	@model_validator(mode="before")
	@classmethod
	def _validate_before(cls, data: t.Dict[str, t.Any], info: ValidationInfo) -> t.Any:
		# Used for validating model instantiation in user code
		if (info.context or {}).get("deserializing", False):
			return data
		elif not isinstance(data, dict):
			return data

		private_attrs = getattr(cls, "__private_attributes__")
		class_specs = private_attrs.get("_element_specs").get_default()

		for attr, spec in class_specs.items():
			expected = spec.internal_type or spec.element_type
			value = data.get(attr)

			if spec.a8n_type == A8nType.LIST:
				cls._validate_list(attr, value, spec)
				spec.init_instantiated_data(value)
				continue
			elif spec.a8n_type == A8nType.OPT and value is None:
				data[attr] = []
				continue
			elif spec.a8n_type == A8nType.MAND and attr not in data:
				raise ValueError(f"argument '{attr}' is missing")
			elif not isinstance(value, expected):
				arg_type = type(value).__name__
				raise ValueError(
					f"unexpected type '{arg_type}' "
					f"for argument '{attr}'"
				)
			data[attr] = [value]
			spec.init_instantiated_data(data[attr])
		return data

	@model_validator(mode="after")
	def _validate_after(self, info: ValidationInfo) -> MessageBody:
		# Used for validating deserialized incoming requests
		if not (info.context or {}).get("deserializing", False):
			return self

		specs = getattr(self, "_element_specs", None)
		if not specs:
			return self

		for attr, value in vars(self).items():
			spec = specs.get(attr)  # type: BaseElementSpec
			if spec is None:
				continue
			elif not isinstance(value, list):
				value = [value]
			count = len(value)

			if count > 1 and spec.a8n_type in [A8nType.MAND, A8nType.OPT]:
				raise ValueError(f"only one {spec.tag} element is allowed")
			elif count == 0 and spec.a8n_type == A8nType.MAND:
				raise ValueError(f"must provide at least one {spec.tag} element")
			elif spec.a8n_type == A8nType.LIST:
				self._validate_list(attr, value, spec)
				spec.init_deserialized_data(value)
				continue

			spec.init_deserialized_data(value)
			value = value[0] if count == 1 else None
			setattr(self, attr, value)
		return self


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)
