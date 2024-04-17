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
from ..uid_gen import UIDGenerator
from ..multipart import MultipartEncoder
from ..elements.models import SwaRefUtils
from ..envelope import (
	EnvelopeFactory,
	XroadHeader
)


__all__ = ["SoapResponse"]


class SoapResponse(Response):
	media_type = 'text/xml'

	def __init__(
			self,
			content: MessageBody,
			header: t.Optional[XroadHeader] = None,
			http_status_code: t.Optional[int] = 200
	) -> None:
		if files := SwaRefUtils.gather_specs_and_files(content)[1]:
			cid = UIDGenerator(mode="cid")
			for file in files:
				file.content_id = cid.generate()
			message = self.serialize(content, header)
			encoder = MultipartEncoder(message, files)
			xml_str = encoder.message
			http_headers = encoder.headers
		else:
			xml_str = self.serialize(content, header)
			http_headers = {"Content-Type": "text/xml; charset=UTF-8"}
		super().__init__(
			content=xml_str,
			headers=http_headers,
			status_code=http_status_code
		)

	@staticmethod
	def serialize(content: MessageBody, header: t.Optional[XroadHeader]) -> bytes:
		envelope = EnvelopeFactory[content.__class__]()
		return envelope.serialize(
			content=content,
			header=header,
			pretty_print=False,
			skip_empty=True
		)
