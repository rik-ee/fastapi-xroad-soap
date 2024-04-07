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
import hashlib
import typing as t
from pydantic_xml import element
from pydantic import Field, PrivateAttr, model_validator
from ..base import BaseElementSpec, MessageBody
from ..storage import GlobalWeakStorage
from ..multipart import DecodedBodyPart
from ..file_size import FileSize


__all__ = ["SwaRef", "SwaRefSpec", "SwaRefInternal"]


_NSMap = t.Optional[t.Dict[str, str]]
_FileType = t.Union[DecodedBodyPart, None]
_FileSizeType = t.Union[FileSize, None]
_Filetypes = t.Union[t.List[str], t.Literal["all"]]
_HashFuncType = t.Literal["sha256", "sha512", "sha3_256", "sha3_384", "sha3_512"]


class SwaRef(MessageBody):
	name: str = element(default='')
	mimetype: str = element(default='')
	size: int = element(default=0)
	digest: str = element(default='')
	content: bytes = element(default=b'')

	def __new__(
			cls,
			*,
			tag: t.Optional[str] = None,
			ns: t.Optional[str] = None,
			nsmap: _NSMap = None,
			min_occurs: int = None,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = None,
			allowed_filetypes: _Filetypes = "all",
			max_filesize: _FileSizeType = None,
			hash_func: _HashFuncType = "sha3_512"
	) -> SwaRef:
		kwargs = {k: v for k, v in locals().items()}
		return t.cast(SwaRef, SwaRefSpec(**kwargs))

	@classmethod
	def _real_new_(cls):
		return super().__new__(cls)


class SwaRefSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.allowed_filetypes = kwargs.pop("allowed_filetypes")
		self.max_filesize = kwargs.pop("max_filesize")
		self.hash_func = kwargs.pop("hash_func")
		super().__init__(element_type=SwaRef, **kwargs)

	def get_a8n(self) -> t.Type[t.List[t.Any]]:
		new = type("SwaRef", (SwaRefInternal,), dict(
			_allowed_filetypes=self.allowed_filetypes,
			_max_filesize=self.max_filesize,
			_hash_func=self.hash_func
		))
		return t.List[new]


class SwaRefInternal(SwaRef):
	fingerprint: str = Field(exclude=True)

	_allowed_filetypes: _Filetypes = PrivateAttr(default="all")
	_max_filesize: _FileSizeType = PrivateAttr(default=None)
	_hash_func: _HashFuncType = PrivateAttr(default="sha3_512")
	_file: _FileType = PrivateAttr(default=None)

	def __new__(cls, *_, **__):
		return super()._real_new_()

	@model_validator(mode="after")
	def init_values(self):
		if self._file is not None:
			return self
		file: DecodedBodyPart = GlobalWeakStorage.retrieve_object(
			self.fingerprint, raise_on_miss=False
		)
		if file is None:
			raise ValueError(f"no file attachment found by Content-ID: {self.fingerprint}")
		elif '.' not in file.file_name:
			raise ValueError(f"invalid file name: {file.file_name}")

		file_ext = '.' + file.file_name.split('.')[-1]
		if self._allowed_filetypes != "all" and file_ext not in self._allowed_filetypes:
			extra = f"(allowed: {self._allowed_filetypes})$${file.content_id}$$"
			raise ValueError(f"file type not allowed: {file_ext} {extra}")

		file_size = len(file.content)
		if self._max_filesize and file_size > self._max_filesize.value:
			size = FileSize.bytes_to_iec_str(file_size)
			extra = f"(max: {self._max_filesize})$${file.content_id}$$"
			raise ValueError(f"file size too large: {size} {extra}")

		hash_func = getattr(hashlib, self._hash_func)
		file_digest = hash_func(file.content).hexdigest()
		
		self.name = file.file_name
		self.mimetype = file.mime_type
		self.size = file_size
		self.digest = file_digest
		self.content = file.content
		self._file = file

		delattr(self, "fingerprint")
		return self
