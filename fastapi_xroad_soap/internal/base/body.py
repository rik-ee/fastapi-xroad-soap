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
from pydantic_xml import model
from pydantic.fields import ModelPrivateAttr
from pydantic import (
	PrivateAttr,
	ValidationInfo,
	model_validator
)
from ..constants import A8nType
from .meta import CompositeMeta

try:
	from .spec import BaseElementSpec
except ImportError:  # pragma: no cover
	BaseElementSpec: t.TypeAlias = t.Any


__all__ = ["NestedModels", "MessageBody", "MessageBodyType"]


NestedModels = t.List[t.Tuple[
	t.Type["MessageBody"],
	t.List[t.Type["MessageBody"]]
]]
ModelConfig = dict(
	metaclass=CompositeMeta,
	search_mode='unordered',
	skip_empty=True,
	extra="forbid"
)


class MessageBody(model.BaseXmlModel, **ModelConfig):
	_element_specs: t.Dict[str, BaseElementSpec] = PrivateAttr(default_factory=dict)

	@classmethod
	def model_specs(cls) -> t.Dict[str, BaseElementSpec]:
		privates = getattr(cls, "__private_attributes__", {})
		attr: t.Union[ModelPrivateAttr, None] = privates.get("_element_specs")
		return attr.get_default() if attr is not None else dict()

	@classmethod
	def nested_models(cls) -> NestedModels:
		models, children = [], []
		a8ns = getattr(cls, '__annotations__', {})
		for key, value in a8ns.items():
			if type(value) is CompositeMeta:
				models.extend(value.get_nested_models())
				children.append(value)
		models.append((cls, children))
		return models

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

	# noinspection PyNestedDecorators
	@model_validator(mode="before")
	@classmethod
	def _validate_before(cls, data: t.Dict[str, t.Any], info: ValidationInfo) -> t.Any:
		# Used for validating model instantiation in user code
		is_incoming_request = (info.context or {}).get("deserializing", False)
		if is_incoming_request or not isinstance(data, dict):
			return data

		for attr, spec in cls.model_specs().items():
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
		is_incoming_request = (info.context or {}).get("deserializing", False)
		if not is_incoming_request:  # is model instantiation in user code
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
				raise ValueError(f"only one {spec.tag} element is allowed $$Count: {count}$$")
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
