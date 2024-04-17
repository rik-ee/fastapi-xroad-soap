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
import base64
import string
import secrets
import typing as t
from weakref import WeakValueDictionary


__all__ = [
	"GlobalWeakStorage",
	"ExportableGWS"
]


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
		token = secrets.token_bytes(36)
		b64_token = base64.b64encode(token)
		return f"{filled}..{b64_token.decode()}"

	@classmethod
	def validate_fingerprint(cls, fingerprint: str, raise_on_invalid: bool = True) -> bool:
		"""Validates the fingerprint format and its unique identifiers."""
		is_valid = True
		if (
			not isinstance(fingerprint, str)
			or len(fingerprint) != 122
			or '-$$-' not in fingerprint
		):
			is_valid = False
		if is_valid:
			is_valid = cls._validate_unique_ids(fingerprint)
		if not is_valid and raise_on_invalid:
			raise ValueError(f"invalid fingerprint: {fingerprint}")
		return is_valid

	@staticmethod
	def _validate_unique_ids(fingerprint: str) -> bool:
		valid_b64_chars = string.ascii_letters + string.digits + '+/='
		is_valid = True
		for uid in fingerprint.split('-$$-'):
			if len(uid) != 59 or '..' not in uid:
				is_valid = False
			counter, token = uid.split('..')  # type: str, str
			if len(counter) != 9 or not counter.isdigit():
				is_valid = False
			for char in token:
				if char not in valid_b64_chars:
					is_valid = False
		return is_valid

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

	@classmethod
	def retrieve_object(cls, fingerprint: str, *, raise_on_miss: bool = True) -> t.Union[t.Any, None]:
		"""
		Retrieves an object from an instance of GlobalWeakStorage identified by the provided fingerprint.

		:param fingerprint: The unique identifier of the object.
		:param raise_on_miss: Whether a KeyError should be raised if the
			fingerprint does not relate to any object. Defaults to True.
		:raises ValueError: If the fingerprint has invalid format.
		:raises KeyError: if `raise_on_miss` is True and the fingerprint does not relate to any object.
		:returns: The object associated with the given fingerprint if it exists, otherwise None.
		"""
		cls.validate_fingerprint(fingerprint)
		inst_id, obj_id = fingerprint.split('-$$-')
		instance = cls._instances.get(inst_id) or {}
		store: WeakValueDictionary = getattr(instance, '_objects', {})
		if raise_on_miss:
			return store[obj_id]
		return store.get(obj_id, None)

	def get(self, fingerprint: str, *, raise_on_miss: bool = True) -> t.Union[t.Any, None]:
		"""
		Retrieves an object from this instance of GlobalWeakStorage identified by the provided fingerprint.

		:param fingerprint: The unique identifier of the object.
		:param raise_on_miss: Whether a KeyError should be raised if the
			fingerprint does not relate to any object. Defaults to True.
		:raises ValueError: If the fingerprint has invalid format.
		:raises KeyError: if `raise_on_miss` is True and the fingerprint does not relate to any object.
		:returns: The object associated with the given fingerprint if it exists, otherwise None.
		"""
		self.validate_fingerprint(fingerprint)
		obj_id = fingerprint.split('-$$-')[1]
		if raise_on_miss:
			return self._objects[obj_id]
		return self._objects.get(obj_id, None)


ExportableGWS = type('GlobalWeakStorage', (GlobalWeakStorage,), {})
