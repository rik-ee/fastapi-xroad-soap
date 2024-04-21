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
from pydantic_xml import model
from pydantic import fields
from pydantic import (
	PrivateAttr,
	ValidationInfo,
	model_validator
)
from ..constants import A8nType
from .base_element_spec import BaseElementSpec
from .composite_meta import CompositeMeta
from .dynamic_spec import dynamic_spec
from . import validators as vld


__all__ = ["MessageBody", "MessageBodyType"]


class MessageBody(model.BaseXmlModel, metaclass=CompositeMeta, search_mode='unordered', skip_empty=True):
	_element_specs: t.Dict[str, BaseElementSpec] = PrivateAttr(default_factory=dict)
	_T = t.TypeVar('_T', bound="MessageBody")

	@classmethod
	def Element(
			cls: t.Type[_T],
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: t.Optional[t.Dict[str, str]] = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None
	) -> _T:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(MessageBody, dynamic_spec(cls, **kwargs))

	@classmethod
	def model_specs(cls) -> t.Dict[str, BaseElementSpec]:
		privates = getattr(cls, "__private_attributes__", {})
		attr: t.Union[fields.ModelPrivateAttr, None] = privates.get("_element_specs")
		return attr.get_default() if attr is not None else dict()

	@classmethod
	def nested_models(cls) -> t.List[t.Type["MessageBody"]]:
		models = []
		a8ns = getattr(cls, '__annotations__', {})
		for key, value in a8ns.items():
			origin = t.get_origin(value)
			if origin is None:
				continue
			if origin == list or "Union" in origin.__name__:
				args = t.get_args(value)
				args_len = len(args)
				opt_union = args_len == 2 and type(None) in args
				if not opt_union and args_len != 1:
					raise ValueError(
						f"Invalid type annotation arguments '{args}' "
						f"for class {cls.__name__} attribute '{key}'"
					)
				value = [a for a in args if a is not None][0]
			if type(value) is not CompositeMeta:
				continue
			models.extend(value.nested_models())
		models.append(cls)
		return models

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
				vld.validate_list_items(attr, value, spec)
				spec.init_instantiated_data(value)
				continue
			elif spec.a8n_type == A8nType.OPT and value is None:
				data[attr] = []
				continue
			elif spec.a8n_type == A8nType.MAND and attr not in data:
				raise ValueError(f"argument '{attr}' is missing")
			elif not isinstance(value, expected):
				arg_type = type(value).__name__
				raise ValueError(f"unexpected type '{arg_type}' for argument '{attr}'")
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
			elem_name = spec.tag or inflection.camelize(attr)

			if count > 1 and spec.a8n_type in [A8nType.MAND, A8nType.OPT]:
				raise ValueError(f"only one {elem_name} element is allowed, got {count}")
			elif count == 0 and spec.a8n_type == A8nType.MAND:
				raise ValueError(f"must provide at least one {elem_name} element")
			elif spec.a8n_type == A8nType.LIST:
				vld.validate_list_items(attr, value, spec)
				spec.init_deserialized_data(value)
				continue

			spec.init_deserialized_data(value)
			value = value[0] if count == 1 else None
			setattr(self, attr, value)
		return self


MessageBodyType = t.TypeVar("MessageBodyType", bound=MessageBody)