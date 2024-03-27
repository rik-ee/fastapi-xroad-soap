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
from fastapi.types import DecoratedCallable
from fastapi_xroad_soap.internal.envelope import MessageBody, XroadHeader


__all__ = [
	"get_annotations",
	"validate_annotations",
	"extract_parameter_positions"
]


def get_annotations(func: t.Any) -> dict:
	key: str = "__annotations__"
	anno = getattr(func, key, None)
	if anno is None and hasattr(func, "__dict__"):
		anno = func.__dict__.get(key, None)
	return anno or dict()


def validate_annotations(name: str, func: DecoratedCallable) -> dict:
	anno = get_annotations(func)
	for key, value in anno.items():
		if key not in ["body", "header", "return"]:
			raise ValueError(
				f"Parameter name '{key}' not allowed for SOAP action {name}."
				"\nOnly names 'body' and 'header' can be used for parameters."
			)
		elif key == "return":
			if value is None:
				continue
			elif not isinstance(value, type) or not issubclass(value, MessageBody):
				raise TypeError(
					f"Return type annotation of the {name} SOAP action "
					"must be either 'None' or a subclass of 'MessageBody'."
				)
		elif key == "body":
			if value == XroadHeader:
				raise TypeError(
					f"Cannot set the 'XroadHeader' class as a type annotation "
					f"to the 'body' parameter of the {name} SOAP action."
				)
			elif not isinstance(value, type) or not issubclass(value, MessageBody):
				raise TypeError(
					f"The annotation of the '{key}' parameter of the {name} "
					f"SOAP action must be a subclass of 'MessageBody'."
				)
		elif key == "header" and value != XroadHeader:
			raise ValueError(
				f"The annotation of the 'headers' parameter of the {name} "
				f"SOAP action must be the 'XroadHeaders' class."
			)
	return anno


def extract_parameter_positions(anno: dict) -> dict:
	pos = dict(body=None, header=None)
	keys = list(anno.keys())
	for key in ["body", "header"]:
		if key in keys:
			pos[key] = keys.index(key)
	return pos
