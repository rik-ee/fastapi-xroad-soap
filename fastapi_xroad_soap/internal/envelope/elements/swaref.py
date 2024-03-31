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
import inflection
from pydantic_xml import model, element
from fastapi_xroad_soap.internal.envelope import (
	BaseElementSpec,
	MessageBody
)
from fastapi_xroad_soap.internal.file_size import (
	FileSize
)


__all__ = ["SwaRefFile", "SwaRefSpec", "SwaRef"]


class SwaRefFile(MessageBody):
	file_name: str = element(tag="FileName")
	mime_type: str = element(tag="MimeType")
	content_length: int = element(tag="ContentLength")
	content_digest: str = element(tag="ContentDigest")
	content: bytes = element(tag="Content")


class SwaRefSpec(BaseElementSpec):
	def __init__(self, **kwargs) -> None:
		self.tag = kwargs["tag"]
		self.ns = kwargs["ns"]
		self.nsmap = kwargs["nsmap"]
		self.min_occurs = kwargs["min_occurs"]
		self.max_occurs = kwargs["max_occurs"]
		self.max_file_size = kwargs["max_file_size"]
		self.allowed_mimetypes = kwargs["allowed_mimetypes"]

	def use_list_type(self) -> bool:
		if self.max_occurs == "unbounded":
			return True
		elif self.max_occurs > 1 or self.min_occurs > 1:
			return True
		return False

	def annotation(self) -> t.Any:
		if self.min_occurs == 1 and self.max_occurs == 1:
			return SwaRefFile
		elif self.use_list_type():
			return t.List[SwaRefFile]
		return t.Optional[SwaRefFile]

	def element(self, attr_name: str) -> model.XmlEntityInfo:
		base = dict(
			ns=self.ns or '',
			nsmap=self.nsmap or dict(),
			tag=self.tag or inflection.camelize(attr_name)
		)
		if not self.use_list_type():
			return element(**base)

		is_inf = self.max_occurs == "unbounded"
		max_occurs = None if is_inf else self.max_occurs
		return element(
			**base,
			min_length=self.min_occurs,
			max_length=max_occurs
		)


class SwaRef:
	def __new__(
			cls,
			*,
			tag: str = None,
			ns: str = None,
			nsmap: str = None,
			min_occurs: int = 1,
			max_occurs: t.Union[int, t.Literal["unbounded"]] = 1,
			max_file_size: t.Union[int, FileSize, None] = None,
			allowed_mimetypes: t.Union[t.List[str], t.Literal["all"]] = "all"
	) -> SwaRefFile:
		kwargs = {k: v for k, v in locals().items() if v != cls}
		return t.cast(SwaRefFile, SwaRefSpec(**kwargs))  # For IDE code completion
