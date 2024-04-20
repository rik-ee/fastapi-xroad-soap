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

try:
	from .body import MessageBody
except ImportError:  # pragma: no cover
	MessageBody: t.TypeAlias = t.Any
try:
	from .spec import BaseElementSpec
except ImportError:  # pragma: no cover
	BaseElementSpec: t.TypeAlias = t.Any


__all__ = ["validate_list_items", "validate_a8n_args"]


def validate_list_items(attr: str, data: t.List[MessageBody], spec: BaseElementSpec):
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


def validate_a8n_args(a8n: t.Any, attr: str, cls_name: str, expected_type: t.Type) -> None:
	if a8n in [t.Optional, t.Union, t.List, list]:
		raise TypeError(
			f"Not permitted to provide '{a8n}' "
			f"annotation without a type argument."
		)
	if args := t.get_args(a8n):
		if len(args) == 1 and args[0] != expected_type:
			raise TypeError(
				f"Single annotation argument for class '{cls_name}' "
				f"attribute '{attr}' must be '{expected_type.__name__}'."
			)
		for arg in args:
			if arg is type(None) or arg == expected_type:
				continue
			arg_name = "None" if arg is type(None) else arg.__name__
			raise TypeError(
				f"Invalid annotation argument '{arg_name}' "
				f"for '{cls_name}' class attribute '{attr}'."
			)
