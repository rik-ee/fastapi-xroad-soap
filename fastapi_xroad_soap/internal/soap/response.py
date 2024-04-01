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
from ..envelope import (
	EnvelopeFactory,
	XroadHeader,
	MessageBody
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
		envelope = EnvelopeFactory[content.__class__]()
		xml_str = envelope.serialize(
			content=content,
			header=header,
			pretty_print=False,
			skip_empty=True
		)
		super().__init__(
			content=xml_str,
			status_code=http_status_code
		)
