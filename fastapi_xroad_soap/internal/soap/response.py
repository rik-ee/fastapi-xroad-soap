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
from fastapi import Response
from ..base import MessageBody
from ..cid_gen import CIDGenerator
from ..multipart import MultipartEncoder
from ..elements import (
	SwaRefInternal,
	SwaRefSpec
)
from ..envelope import (
	EnvelopeFactory,
	XroadHeader
)


__all__ = ["SoapResponse"]


FileObject = t.Union[SwaRefInternal, t.List[SwaRefInternal]]


class SoapResponse(Response):
	media_type = 'text/xml'

	def __init__(
			self,
			content: MessageBody,
			header: t.Optional[XroadHeader] = None,
			http_status_code: t.Optional[int] = 200
	) -> None:
		if files := self.assign_content_ids(content):
			message = self.serialize(content, header)
			encoder = MultipartEncoder(message, files)
			xml_str = encoder.message
			http_headers = encoder.headers
		else:
			xml_str = self.serialize(content, header)
			http_headers = {
				"Content-Type": "text/xml;charset=UTF-8"
			}
		super().__init__(
			content=xml_str,
			headers=http_headers,
			status_code=http_status_code
		)

	@classmethod
	def assign_content_ids(cls, content: MessageBody, gen: CIDGenerator = None) -> t.List[SwaRefInternal]:
		gen, files = gen or CIDGenerator(), list()
		if not isinstance(content, MessageBody):
			return []

		# Define recursion behavior
		for sub_content in vars(content).values():
			if isinstance(sub_content, MessageBody):
				nested = cls.assign_content_ids(sub_content, gen)
				files.extend(nested)

		# Add files from content
		specs = getattr(content, "_element_specs", None)
		if specs is None:
			return files
		for attr, spec in specs.items():
			if not isinstance(spec, SwaRefSpec):
				continue
			obj: FileObject = getattr(content, attr)
			if isinstance(obj, SwaRefInternal):
				obj.content_id = gen.token
				files.append(obj)
			elif isinstance(obj, list):
				for item in obj:
					if isinstance(item, SwaRefInternal):
						item.content_id = gen.token
						files.append(item)
		return files

	@staticmethod
	def serialize(content: MessageBody, header: t.Optional[XroadHeader]) -> bytes:
		envelope = EnvelopeFactory[content.__class__]()
		return envelope.serialize(
			content=content,
			header=header,
			pretty_print=False,
			skip_empty=True
		)
