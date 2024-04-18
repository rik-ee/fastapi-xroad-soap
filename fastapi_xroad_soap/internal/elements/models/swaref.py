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
from pydantic.fields import Field
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.multipart import DecodedBodyPart
from fastapi_xroad_soap.internal.file_size import FileSize
from fastapi_xroad_soap.internal.base import (
	BaseElementSpec,
	CompositeMeta,
	MessageBody
)


__all__ = [
	"SwaRefFile",
	"SwaRefInternal",
	"SwaRefSpec",
	"SwaRefElement",
	"SwaRef",
	"SwaRefUtils"
]


_NSMap = t.Optional[t.Dict[str, str]]
_FileType = t.Union[DecodedBodyPart, None]
_FileSizeType = t.Union[FileSize, None]
_Filetypes = t.Union[t.List[str], t.Literal["all"]]
_HashFuncType = t.Literal["sha256", "sha512", "sha3_256", "sha3_384", "sha3_512"]
_SwaRefTypes = t.Tuple[t.List["SwaRefSpec"], t.List["SwaRefFile"]]


class SwaRefFile(MessageBody):
	name: str = Field(exclude=True, default='')
	size: int = Field(exclude=True, default=0)
	digest: str = Field(exclude=True, default='')
	mimetype: str = Field(exclude=True, default='')
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

	@property
	def mime_cid(self) -> str:
		cid = self.content_id
		if isinstance(cid, str) and ':' in cid:
			raw = self.content_id.split(':')[1]
			return f"<{raw}>"
		return ''


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

	@property
	def has_constraints(self) -> bool:
		return False

	def wsdl_type_name(self, *, with_tns: bool = False) -> str:
		return "wsi:swaRef"

	def digest(self, content: bytes) -> str:
		hash_func = getattr(hashlib, self.hash_func)
		digest = hash_func(content).digest()
		name = self.hash_func.replace('_', '-')
		b64_hash = base64.b64encode(digest).decode()
		return f"{name}={b64_hash}"

	def validate_file(self, name: str, size: int, content_id: str = None) -> None:
		extract = '' if content_id is None else f"$$Content-ID: {content_id}$$"
		if '.' not in name:
			raise ValueError(f"invalid file name $${name}$$")
		aft = self.allowed_filetypes
		if aft != "all" and isinstance(aft, list):
			file_ext = '.' + name.split('.')[-1]
			if file_ext not in self.allowed_filetypes:
				raise ValueError(
					f"file type '{file_ext}' not in allowed "
					f"filetypes {self.allowed_filetypes}{extract}"
				)
		mfs = self.max_filesize
		if isinstance(mfs, FileSize) and size > mfs.value:
			input_size = FileSize.bytes_to_iec_str(size)
			raise ValueError(
				f"file size {input_size} larger than "
				f"allowed max size {mfs}{extract}"
			)

	def init_instantiated_data(self, data: t.List[SwaRefInternal]) -> t.List[SwaRefInternal]:
		for obj in data:
			obj.size = len(obj.content)
			self.validate_file(obj.name, obj.size)

			obj.digest = self.digest(obj.content)
			obj.mimetype = utils.guess_mime_type(obj.name)
			obj.content = utils.convert_to_utf8(obj.content)

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

			obj.name = file.name
			obj.size = len(file.content)
			self.validate_file(obj.name, obj.size, file.content_id)

			obj.digest = self.digest(file.content)
			obj.mimetype = utils.guess_mime_type(file.name)
			obj.content = utils.convert_to_utf8(file.content)

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


class SwaRefUtils:
	@classmethod
	def contains_swa_ref_specs(cls, content_cls: t.Type[MessageBody]) -> bool:
		# print(type(content_cls))
		has_swa_ref = False

		# Define recursion behavior
		fields = getattr(content_cls, "model_fields", {})
		for sub_content_cls in fields.values():
			res = cls.contains_swa_ref_specs(sub_content_cls)
			has_swa_ref |= res

		# Check private attributes for SwaRef specs
		if type(content_cls) is not CompositeMeta:
			return has_swa_ref
		specs = content_cls.model_specs()
		for spec in specs.values():
			if type(spec).__name__ == "SwaRefSpec":
				has_swa_ref |= True
		return has_swa_ref

	@classmethod
	def gather_specs_and_files(cls, content: MessageBody) -> _SwaRefTypes:
		specs, files = [], []
		if not isinstance(content, MessageBody):
			return specs, files

		# Define recursion behavior
		for sub_content in vars(content).values():
			if isinstance(sub_content, MessageBody):
				_specs, _files = cls.gather_specs_and_files(sub_content)
				for a, b in [(specs, _specs), (files, _files)]:
					a.extend(b)

		# Gather specs and files from content
		cls._add_specs_and_files(specs, files, content)
		return specs, files

	@staticmethod
	def _add_specs_and_files(
			specs: t.List[SwaRefSpec],
			files: t.List[SwaRefFile],
			content: MessageBody
	) -> None:
		_specs = getattr(content, "_element_specs", None)
		if _specs is None:
			return
		for attr, spec in _specs.items():
			if not isinstance(spec, SwaRefSpec):
				continue
			specs.append(spec)
			obj = getattr(content, attr)
			if isinstance(obj, SwaRefFile):
				files.append(obj)
			elif isinstance(obj, list):
				for item in obj:
					if isinstance(item, SwaRefFile):
						files.append(item)
