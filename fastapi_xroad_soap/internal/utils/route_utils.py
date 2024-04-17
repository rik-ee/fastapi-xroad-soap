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


__all__ = [
	"get_annotations",
	"extract_parameter_positions"
]


def get_annotations(func: t.Any) -> dict:
	key: str = "__annotations__"
	anno = getattr(func, key, None)
	if anno is None and hasattr(func, "__dict__"):
		anno = func.__dict__.get(key, None)
	return anno or dict()


def extract_parameter_positions(anno: dict) -> dict:
	pos = dict(body=None, header=None)
	keys = list(anno.keys())
	for key in ["body", "header"]:
		if key in keys:
			pos[key] = keys.index(key)
	return pos
