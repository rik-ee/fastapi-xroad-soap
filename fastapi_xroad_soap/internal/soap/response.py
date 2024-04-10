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
from .. import utils
from ..base import MessageBody
from ..cid_gen import CIDGenerator
from ..elements import (
	SwaRefInternal,
	SwaRefSpec
)
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
		if utils.object_has_spec(content, SwaRefSpec):
			self.assign_content_ids(content, CIDGenerator())

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

	@classmethod
	def assign_content_ids(cls, content: MessageBody, gen: CIDGenerator) -> None:
		if not isinstance(content, MessageBody):
			return
		elif specs := getattr(content, "_element_specs", None):
			for attr, spec in specs.items():
				if not isinstance(spec, SwaRefSpec):
					continue
				obj = getattr(content, attr)  # type: SwaRefInternal
				if isinstance(obj, SwaRefInternal):
					obj.content_id = gen.token
					continue
				elif not isinstance(obj, list):
					continue
				for item in obj:
					if isinstance(item, SwaRefInternal):
						item.content_id = gen.token
		for value in vars(content).values():
			if isinstance(value, MessageBody):
				cls.assign_content_ids(value, gen)
