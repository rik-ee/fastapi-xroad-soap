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
import secrets
import typing as t
from weakref import WeakValueDictionary


__all__ = ["GlobalWeakStorage"]


class GlobalWeakStorage:
	_instances = WeakValueDictionary()
	_inst_counter = 0
	_uid = ''

	def __new__(cls) -> GlobalWeakStorage:
		uid = cls._unique_id(cls._inst_counter)
		instance = super().__new__(cls)
		instance._uid = uid
		cls._instances[uid] = instance
		cls._inst_counter += 1
		return instance

	def __init__(self) -> None:
		self._objects = WeakValueDictionary()
		self._obj_counter = 0

	@staticmethod
	def _unique_id(index: int) -> str:
		clamped = index % 1_000_000_000
		filled = str(clamped).zfill(9)
		token = secrets.token_hex(24)
		return f"{filled}..{token}"

	def insert_object(self, obj: t.Any) -> str:
		uid = self._unique_id(self._obj_counter)
		self._obj_counter += 1
		self._objects[uid] = obj
		return f"{self._uid}-$$-{uid}"

	@classmethod
	def retrieve_object(cls, fingerprint: str) -> t.Union[t.Any, None]:
		inst_id, obj_id = fingerprint.split('-$$-')
		instance = cls._instances.get(inst_id) or {}
		return instance.get(obj_id)

	def get(self, fingerprint: str = None) -> t.Union[t.Any, None]:
		if '-$$-' not in fingerprint:
			obj_id = fingerprint  # assume obj_id
		else:
			obj_id = fingerprint.split('-$$-')[1]
		return self._objects.get(obj_id)
