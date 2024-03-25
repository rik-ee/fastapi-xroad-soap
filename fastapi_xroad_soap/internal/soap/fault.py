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
from dataclasses import dataclass
from fastapi_xroad_soap.internal.envelope import (
	EnvelopeFactory,
	GenericFault,
	MessageBody,
	XroadHeader,
)


class SoapFault(Response):
	media_type = 'text/xml'

	def __init__(
			self,
			code: str,
			string: str,
			actor: t.Optional[str] = None,
			detail: t.Optional[MessageBody] = None,
			http_status_code: t.Optional[int] = 400
	) -> None:
		fault_type = MessageBody
		kwargs = dict(
			faultcode=code,
			faultstring=string,
			faultactor=actor
		)
		if isinstance(detail, MessageBody):
			fault_type = detail.__class__
			kwargs["detail"] = detail

		typed_fault = GenericFault[fault_type]
		fault = typed_fault(**kwargs)

		super().__init__(
			content=fault,
			status_code=http_status_code
		)

	def render(self, content: MessageBody) -> bytes:
		envelope = EnvelopeFactory[content.__class__]()
		return envelope.serialize(
			content,
			pretty_print=False,
			skip_empty=True
		)
