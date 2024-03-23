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
from typing import Any
from fastapi.types import DecoratedCallable
from src.envelope.header import XroadHeader
from src.envelope.parts import MessageBody


__all__ = [
	"get_annotations",
	"validate_annotations"
]


def get_annotations(func: Any) -> dict:
	key: str = "__annotations__"
	atd = getattr(func, key, None)
	if atd is None and hasattr(func, "__dict__"):
		atd = func.__dict__.get(key, None)
	return atd or dict()


def validate_annotations(name: str, func: DecoratedCallable) -> dict:
	atd = get_annotations(func)
	for key, value in atd.items():
		if key not in ["body", "header", "return"]:
			raise ValueError(
				f"Parameter name '{key}' not allowed for SOAP action '{name}'."
				"\nOnly names 'body' and 'header' can be used for parameters."
			)
		if key == "return":
			if value is None:
				continue
			elif not isinstance(value, type) or not issubclass(value, MessageBody):
				raise TypeError(
					f"Return type annotation of the '{name}' SOAP action "
					"must be either 'None' or a subclass of 'MessageBody' ."
				)
		elif key == "body":
			if value == XroadHeader:
				raise TypeError(
					f"Cannot set the 'XroadHeader' class as a type annotation "
					f"to the 'body' parameter of the '{name}' SOAP action."
				)
			elif not isinstance(value, type) or not issubclass(value, MessageBody):
				raise TypeError(
					f"The annotation of the '{key}' parameter of the '{name}' "
					f"SOAP action must be a subclass of 'MessageBody'."
				)
		elif key == "header" and value != XroadHeader:
			raise ValueError(
				f"The annotation of the 'headers' parameter of the '{name}' "
				f"SOAP action must be the 'XroadHeaders' class."
			)
	return atd
