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
from .. import BaseElementSpec, MessageBody


__all__ = [
	"SwaRef",
	"SwaRefSpec",
	"SwaRefInternal"
]


_NSMap = t.Optional[t.Dict[str, str]]
_FileType = t.Union[DecodedBodyPart, None]
_FileSizeType = t.Union[int, FileSize, None]
_MimeTypes = t.Union[t.List[str], t.Literal["all"]]
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
			min_occurs: int = 1,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = 1,
			max_filesize: _FileSizeType = None,
			allow_mimetypes: _MimeTypes = "all",
			hash_func: _HashFuncType = "sha3_512"
	) -> SwaRef:
		kwargs = {k: v for k, v in locals().items()}
		return t.cast(SwaRef, SwaRefSpec(**kwargs))

	@classmethod
	def _real_new_(cls):
		return super().__new__(cls)


class SwaRefSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.tag = kwargs["tag"]
		self.ns = kwargs["ns"]
		self.nsmap = kwargs["nsmap"]
		self.max_filesize = kwargs["max_filesize"]
		self.allow_mimetypes = kwargs["allow_mimetypes"]
		self.hash_func = kwargs["hash_func"]
		self.min_occurs = kwargs["min_occurs"]
		self.max_occurs = {
			True: None, False: kwargs["max_occurs"]
		}["unbounded" == kwargs["max_occurs"]]

	def annotation(self, anno: t.Any) -> t.Any:
		self.anno_is_list = t.get_origin(anno) == list
		new = SwaRefInternal.new(self)
		if self.min_occurs == 0:
			return t.Optional[t.List[new]]
		return t.List[new]

	def element(self, attr: str) -> model.XmlEntityInfo:
		return element(
			ns=self.ns or '',
			nsmap=self.nsmap or dict(),
			tag=self.tag or inflection.camelize(attr),
			max_length=self.max_occurs,
			min_length=self.min_occurs,
			default_factory=list
		)


class SwaRefInternal(SwaRef):
	fingerprint: str = Field(exclude=True)

	_file: _FileType = PrivateAttr(default=None)
	_max_filesize: _FileSizeType = PrivateAttr(default=None)
	_allow_mimetypes: _MimeTypes = PrivateAttr(default="all")
	_hash_func: _HashFuncType = PrivateAttr(default="sha3_512")

	def __new__(cls, *args, **kwargs):
		return super()._real_new_()

	@classmethod
	def new(cls, spec: SwaRefSpec) -> t.Type[SwaRef]:
		kwargs = dict(
			_max_filesize=spec.max_filesize,
			_allow_mimetypes=spec.allow_mimetypes,
			_hash_func=spec.hash_func
		)
		new_cls = type("SwaRef", (cls,), kwargs)
		return t.cast(t.Type[SwaRef], new_cls)

	@model_validator(mode="after")
	def init_values(self):
		# TODO: Refactor this awful code
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
			self._file = file
		return self
