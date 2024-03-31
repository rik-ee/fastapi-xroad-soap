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
	@abstractmethod
	def annotation(self) -> t.Any: ...

	@abstractmethod
	def element(self, field_name: str) -> model.XmlEntityInfo: ...


class ElementSpecMeta(type):
	def __new__(cls, name, bases, class_fields, **kwargs):
		annotations = class_fields.get("__annotations__", {})
		element_specs = dict()
		for attr, obj in class_fields.items():
			if isinstance(obj, BaseElementSpec):
				class_fields[attr] = obj.element(attr)
				annotations[attr] = obj.annotation()
				element_specs[attr] = obj
		class_fields["_element_specs"] = element_specs
		return super().__new__(cls, name, bases, class_fields, **kwargs)


class CompositeMeta(ElementSpecMeta, model.XmlModelMeta):
	pass


class MessageBody(model.BaseXmlModel, metaclass=CompositeMeta, search_mode='unordered', skip_empty=True):
	_element_specs: t.Dict[str, BaseElementSpec] = PrivateAttr(default_factory=dict)


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)
