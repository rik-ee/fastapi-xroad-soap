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
import inflection
from pydantic_xml import model, element
from pydantic import PrivateAttr, Field, model_validator
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.multipart import DecodedBodyPart
from fastapi_xroad_soap.internal.file_size import FileSize
from fastapi_xroad_soap.internal.envelope import (
	BaseElementSpec,
	MessageBody
)


__all__ = ["SwaRefFile", "SwaRefSpec", "SwaRefList"]


_FileType = t.Union[DecodedBodyPart, None]
_FileSizeType = t.Union[int, FileSize, None]
_MimeTypes = t.Union[t.List[str], t.Literal["all"]]
_HashFuncType = t.Literal["sha256", "sha512", "sha3_256", "sha3_384", "sha3_512"]
_MaxOccursType = t.Union[int, t.Literal["unbounded"]]


class SwaRefFile(MessageBody):
	fingerprint: str = Field(exclude=True)

	name: str = element(default='')
	mimetype: str = element(default='')
	size: int = element(default=0)
	digest: str = element(default='')
	content: bytes = element(default=b'')

	_file: _FileType = PrivateAttr(default=None)
	_max_filesize: _FileSizeType = PrivateAttr(default=None)
	_allow_mimetypes: _MimeTypes = PrivateAttr(default="all")
	_hash_func: _HashFuncType = PrivateAttr(default="sha3_512")

	@model_validator(mode="after")
	def _init_data(self):
		if self._file is None:
			file: DecodedBodyPart = GlobalWeakStorage.retrieve_object(self.fingerprint)
			self.name = file.file_name
			suffix = self.name.split(".")[-1]
			self.mimetype = file.mime_type
			if self._allow_mimetypes != "all" and suffix not in self._allow_mimetypes:
				raise ValueError(f"file type not allowed: {suffix} (allowed: {self._allow_mimetypes})$${file.content_id}$$")
			self.size = len(file.content)
			if self._max_filesize and self.size > self._max_filesize:
				raise ValueError(f"file size too large: {round(self.size / 1000, 2)}kB (max: {round(self._max_filesize / 1000, 2)}kB) $${file.content_id}$$")
			hash_func = getattr(hashlib, self._hash_func)
			h_obj = hash_func(file.content)
			self.digest = h_obj.hexdigest()
			self.content = file.content
		return self

	@classmethod
	def new(cls, spec: SwaRefSpec) -> t.Type[SwaRefFile]:
		kwargs = dict(
			_max_filesize=spec.max_filesize,
			_allow_mimetypes=spec.allow_mimetypes,
			_hash_func=spec.hash_func
		)
		new_cls = type("CustomSwaRef", (cls,), kwargs)
		return t.cast(t.Type[SwaRefFile], new_cls)


class SwaRefSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.tag = kwargs["tag"]
		self.ns = kwargs["ns"]
		self.nsmap = kwargs["nsmap"]
		self.min_occurs = kwargs["min_occurs"]
		self.max_occurs = kwargs["max_occurs"]
		self.max_filesize = kwargs["max_filesize"]
		self.allow_mimetypes = kwargs["allow_mimetypes"]
		self.hash_func = kwargs["hash_func"]

	def use_list_type(self) -> bool:
		if self.max_occurs == "unbounded":
			return True
		elif self.max_occurs > 1 or self.min_occurs > 1:
			return True
		return False

	def annotation(self) -> t.Any:
		return SwaRefFile.new(self)
		# return t.List[SwaRefFile.new(self)]

	def element(self, attr_name: str) -> model.XmlEntityInfo:
		is_inf = self.max_occurs == "unbounded"
		return element(
			ns=self.ns or '',
			nsmap=self.nsmap or dict(),
			tag=self.tag or inflection.camelize(attr_name),
			# max_length=None if is_inf else self.max_occurs,
			# min_length=self.min_occurs
		)


class SwaRefList:
	def __new__(
			cls,
			*,
			tag: str = None,
			ns: str = None,
			nsmap: str = None,
			min_occurs: int = 1,
			max_occurs: _MaxOccursType = 1,
			max_filesize: _FileSizeType = None,
			allow_mimetypes: _MimeTypes = "all",
			hash_func: _HashFuncType = "sha3_512"
	) -> t.List[SwaRefFile]:  # For IDE code completion
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(t.List[SwaRefFile], SwaRefSpec(**kwargs))
