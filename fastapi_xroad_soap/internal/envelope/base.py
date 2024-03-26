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


__all__ = [
	"Attribute",
	"BaseElement",
	"AnnotationsMixin",
	"CompositeMeta",
	"MessageBody",
	"MessageBodyType"
]


class BaseElement(ABC):
	@abstractmethod
	def annotation(self) -> t.Any: ...

	@abstractmethod
	def element(self, field_name: str) -> model.XmlEntityInfo: ...


class AnnotationsMixin(type):
	def __new__(cls, name, bases, class_fields, **kwargs):
		annotations = class_fields.get('__annotations__', {})
		for attr, obj in class_fields.items():
			if isinstance(obj, BaseElement):
				class_fields[attr] = obj.element(attr)
				annotations[attr] = obj.annotation()
		return super().__new__(cls, name, bases, class_fields, **kwargs)


class CompositeMeta(AnnotationsMixin, model.XmlModelMeta):
	pass


class MessageBody(model.BaseXmlModel, metaclass=CompositeMeta, search_mode='unordered', skip_empty=True):
	pass


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)
