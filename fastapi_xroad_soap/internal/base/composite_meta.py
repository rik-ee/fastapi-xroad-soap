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
from pydantic_xml import model
from ..constants import A8nType
from .base_element_spec import BaseElementSpec


__all__ = ["ElementSpecMeta", "CompositeMeta"]


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
