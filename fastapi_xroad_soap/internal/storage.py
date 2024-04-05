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
		"""
		The GlobalWeakStorage class is a global repository for storing weak object
		references within its instances. This design allows Python to automatically
		garbage collect unused objects that are stored in GlobalWeakStorage, but
		have lost all strong references in the running program. Objects are inserted
		into and stored in instances of this class, but they can also be globally
		retrieved by their unique identifiers using GlobalWeakStorage class methods.
		"""
		self._objects = WeakValueDictionary()
		self._obj_counter = 0

	@staticmethod
	def _unique_id(index: int) -> str:
		"""Generates a unique identifier."""
		clamped = index % 1_000_000_000
		filled = str(clamped).zfill(9)
		token = secrets.token_hex(24).upper()
		return f"{filled}..{token}"

	@staticmethod
	def _validate_fingerprint(fingerprint: str) -> None:
		"""Validates the format of unique identifiers."""
		error = ValueError(f"Invalid fingerprint: {fingerprint}")
		if not isinstance(fingerprint, str):
			raise error
		elif len(fingerprint) != 122:
			raise error
		elif '-$$-' not in fingerprint:
			raise error
		for uid in fingerprint.split('-$$-'):
			if len(uid) != 59:
				raise error
			elif '..' not in uid:
				raise error
			counter, token = uid.split('..')  # type: str, str
			if len(counter) != 9:
				raise error
			elif len(token) != 48:
				raise error
			elif not counter.isdigit():
				raise error
			for char in token:
				if char not in "0123456789ABCDEF":
					raise error

	@classmethod
	def retrieve_object(cls, fingerprint: str) -> t.Union[t.Any, None]:
		"""
		Retrieves an object from a specific instance of GlobalWeakStorage
		identified by the provided fingerprint.

		:param fingerprint: The unique identifier of the object.
		:raises ValueError: If the fingerprint has invalid format.
		:returns: The object associated with the given fingerprint if it exists, otherwise None.
		"""
		cls._validate_fingerprint(fingerprint)
		inst_id, obj_id = fingerprint.split('-$$-')
		instance = cls._instances.get(inst_id) or {}
		store: WeakValueDictionary = getattr(instance, '_objects', {})
		return store.get(obj_id, None)

	def insert_object(self, obj: t.Any) -> str:
		"""
		Inserts an object into the GlobalWeakStorage, generating a unique identifier for it.
		:param obj: The object to be stored in this GlobalWeakStorage instance.
		:returns: A unique identifier for the object, which can be used to access the
			object from any instance of the GlobalWeakStorage class or the class itself.
		"""
		uid = self._unique_id(self._obj_counter)
		self._obj_counter += 1
		self._objects[uid] = obj
		return f"{self._uid}-$$-{uid}"

	def get(self, fingerprint: str) -> t.Union[t.Any, None]:
		"""
		Retrieves an object from this instance of GlobalWeakStorage
		identified by the provided fingerprint.

		:param fingerprint: The unique identifier of the object.
		:raises ValueError: If the fingerprint has invalid format.
		:returns: The object associated with the given fingerprint if it exists, otherwise None.
		"""
		self._validate_fingerprint(fingerprint)
		obj_id = fingerprint.split('-$$-')[1]
		return self._objects.get(obj_id)
