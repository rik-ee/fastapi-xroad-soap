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
from abc import ABC, abstractmethod
from pydantic import model_validator
from pydantic_xml import model, attr as Attribute
from pydantic import PrivateAttr


__all__ = [
	"Attribute",
	"BaseElementSpec",
	"ElementSpecMeta",
	"CompositeMeta",
	"MessageBody",
	"MessageBodyType"
]


class BaseElementSpec(ABC):
	anno_is_list: bool
	min_occurs: int
	max_occurs: int

	@abstractmethod
	def annotation(self, anno: t.Any) -> t.Any: ...

	@abstractmethod
	def element(self, attr: str) -> model.XmlEntityInfo: ...


class ElementSpecMeta(type):
	def __new__(cls, name, bases, class_fields, **kwargs):
		annotations: dict = class_fields.get("__annotations__", {})
		element_specs = dict()
		for attr, obj in class_fields.items():
			if isinstance(obj, BaseElementSpec):
				anno = annotations.get(attr)
				annotations[attr] = obj.annotation(anno)
				class_fields[attr] = obj.element(attr)
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
			if not spec.anno_is_list:
				count = len(v)
				if count > 1:
					raise ValueError("cannot provide more than one file")
				setattr(self, k, v[0] if count == 1 else None)
		self._element_specs.clear()
		return self


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)
