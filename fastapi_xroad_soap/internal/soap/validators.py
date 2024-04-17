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
from ..envelope import XroadHeader
from ..base import MessageBody
from .. import utils


__all__ = ["validate_annotations"]


def validate_annotations(name: str, func: DecoratedCallable) -> dict:
	anno = utils.get_annotations(func)
	for key, value in anno.items():
		_validate_a8n_key(key, name)
		if key == "return":
			_validate_a8n_return(value, name)
		elif key == "body":
			_validate_a8n_body(key, value, name)
		elif key == "header":
			_validate_a8n_header(value, name)
	return anno


def _validate_a8n_key(key: str, name: str) -> None:
	if key not in ["body", "header", "return"]:
		raise ValueError(
			f"Parameter name '{key}' not allowed for SOAP action {name}."
			"\nOnly names 'body' and 'header' can be used for parameters."
		)


def _validate_a8n_return(value: t.Any, name: str) -> None:
	if value is None:
		return
	if not isinstance(value, type) or not issubclass(value, MessageBody):
		raise TypeError(
			f"Return type annotation of the {name} SOAP action "
			"must be either 'None' or a subclass of 'MessageBody'."
		)


def _validate_a8n_body(key: str, value: t.Any, name: str) -> None:
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


def _validate_a8n_header(value: t.Any, name: str) -> None:
	if value != XroadHeader:
		raise ValueError(
			f"The annotation of the 'headers' parameter of the {name} "
			f"SOAP action must be the 'XroadHeaders' class."
		)
