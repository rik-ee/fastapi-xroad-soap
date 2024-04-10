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
import hashlib
import typing as t
from pydantic import Field
from ..base import BaseElementSpec, MessageBody
from ..storage import GlobalWeakStorage
from ..multipart import DecodedBodyPart
from ..file_size import FileSize
from .. import utils


__all__ = [
	"SwaRefFile",
	"SwaRefInternal",
	"SwaRefSpec",
	"SwaRefElement",
	"SwaRef"
]


_NSMap = t.Optional[t.Dict[str, str]]
_FileType = t.Union[DecodedBodyPart, None]
_FileSizeType = t.Union[FileSize, None]
_Filetypes = t.Union[t.List[str], t.Literal["all"]]
_HashFuncType = t.Literal["sha256", "sha512", "sha3_256", "sha3_384", "sha3_512"]


class SwaRefFile(MessageBody):
	name: str = Field(exclude=True, default='')
	mimetype: str = Field(exclude=True, default='')
	size: int = Field(exclude=True, default=0)
	digest: str = Field(exclude=True, default='')
	content: bytes = Field(exclude=True, default='')

	def __new__(cls, name: str, content: bytes) -> SwaRefFile:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(SwaRefFile, SwaRefInternal(**kwargs))

	@classmethod
	def _real_new_(cls, sub_cls):
		return super().__new__(sub_cls)


class SwaRefInternal(SwaRefFile):
	content_id: str = Field(default=None)

	def __new__(cls, **__):
		return super()._real_new_(cls)

	def __init__(self, **kwargs):
		if len(kwargs) == 1:
			key, value = list(kwargs.items())[0]
			if key == "name":
				kwargs = dict(content_id=value)
		super().__init__(**kwargs)


class SwaRefSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.allowed_filetypes = kwargs.pop("allowed_filetypes")
		self.max_filesize = kwargs.pop("max_filesize")
		self.hash_func = kwargs.pop("hash_func")
		super().__init__(
			element_type=SwaRefFile,
			internal_type=SwaRefInternal,
			**kwargs
		)

	def digest(self, content: bytes) -> str:
		hash_func = getattr(hashlib, self.hash_func)
		digest = hash_func(content).digest()
		return base64.b64encode(digest).decode()

	def validate_file(self, name: str, size: int, content_id: str = None) -> None:
		extract = '' if content_id is None else f"$${content_id}$$"
		if '.' not in name:
			raise ValueError(f"invalid file name: {name}")
		if self.allowed_filetypes != "all":
			file_ext = '.' + name.split('.')[-1]
			if file_ext not in self.allowed_filetypes:
				raise ValueError(
					f"file type not allowed: {file_ext} "
					f"(allowed: {self.allowed_filetypes}){extract}"
				)
		if self.max_filesize and size > self.max_filesize.value:
			size_str = FileSize.bytes_to_iec_str(size)
			raise ValueError(
				f"file size too large: {size_str} "
				f"(max: {self.max_filesize}){extract}"
			)

	def init_instantiated_data(self, data: t.List[SwaRefInternal]) -> t.List[SwaRefInternal]:
		for obj in data:
			obj.size = len(obj.content)
			self.validate_file(obj.name, obj.size)
			obj.mimetype = utils.guess_mime_type(obj.name)
			obj.digest = self.digest(obj.content)
			if hasattr(obj, "content_id"):
				delattr(obj, "content_id")
		return data

	def init_deserialized_data(self, data: t.List[SwaRefInternal]) -> t.List[SwaRefInternal]:
		for obj in data:
			if not hasattr(obj, "content_id"):
				continue
			try:
				file: DecodedBodyPart = GlobalWeakStorage.retrieve_object(obj.content_id)
			except ValueError:
				raise ValueError(f"no file attachment found $${obj.content_id}$$")

			file_size = len(file.content)
			self.validate_file(file.file_name, file_size, file.content_id)

			obj.name = file.file_name
			obj.mimetype = utils.guess_mime_type(file.file_name)
			obj.size = file_size
			obj.digest = self.digest(file.content)
			obj.content = file.content

			setattr(obj, "_file", file)
			delattr(obj, "content_id")
		return data


class SwaRefElement:
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
	) -> SwaRefFile:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(SwaRefFile, SwaRefSpec(**kwargs))


class SwaRef:
	File: t.Type[SwaRefFile] = SwaRefFile
	Element: t.Type[SwaRefElement] = SwaRefElement

	def __init__(self):
		raise NotImplementedError(
			"Cannot directly instantiate SwaRef, you must "
			"instantiate one of its attribute classes."
		)
