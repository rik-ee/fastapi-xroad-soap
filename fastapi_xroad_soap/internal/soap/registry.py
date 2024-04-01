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
import hashlib
import typing as t
from datetime import datetime
from weakref import WeakValueDictionary
from fastapi_xroad_soap.internal.multipart import DecodedBodyPart


__all__ = ["FileRegistry"]


class FileRegistry:
	__instances__: t.Dict[int, FileRegistry] = dict()
	__reg_id__: int = 0

	def __new__(cls) -> FileRegistry:
		current = cls.__reg_id__
		new_obj = super().__new__(cls)
		new_obj.__reg_id__ = current
		cls.__instances__[current] = new_obj
		cls.__reg_id__ += 1
		return new_obj

	def __init__(self):
		wvd_type = WeakValueDictionary[str, DecodedBodyPart]
		self.files: wvd_type = WeakValueDictionary()

	@staticmethod
	def _file_id():
		dtn = datetime.now().isoformat()
		h = hashlib.sha3_256(dtn.encode())
		dtn_hex = h.hexdigest()[:16]
		rand_hex = secrets.token_hex(32)
		return f"{dtn_hex}||{rand_hex}"

	def _fingerprint(self, file_id: str) -> str:
		return f"{self.__reg_id__}--{file_id}"

	def register_file(self, file: DecodedBodyPart) -> str:
		file_id = self._file_id()
		self.files[file_id] = file
		return self._fingerprint(file_id)

	@classmethod
	def retrieve_file(cls, fingerprint: str) -> DecodedBodyPart:
		reg_id, file_id = fingerprint.split('--')
		registry = cls.__instances__[int(reg_id)]
		return registry.files[file_id]
