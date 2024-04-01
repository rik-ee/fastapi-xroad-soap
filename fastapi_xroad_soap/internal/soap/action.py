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
from dataclasses import dataclass
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.multipart import (
	MultipartDecoder,
	DecodedBodyPart
)
from .response import SoapResponse
from . import faults as f
from ..envelope import (
	EnvelopeFactory,
	GenericEnvelope,
	XroadHeader,
	MessageBody
)


__all__ = ["SoapAction"]


@dataclass(frozen=True)
class SoapAction:
	name: str
	handler: t.Callable[..., t.Optional[MessageBody]]
	body_type: t.Type[MessageBody]
	body_index: t.Optional[int]
	header_type: t.Type[XroadHeader]
	header_index: t.Optional[int]
	return_type: t.Optional[t.Type[MessageBody]]
	storage: GlobalWeakStorage

	def arguments_from(
			self,
			envelope: GenericEnvelope,
			action_name: str
	) -> t.List[t.Union[MessageBody, XroadHeader]]:
		args = list()
		if self.body_type is not None:
			if envelope.body is None:
				raise f.MissingBodyFault(action_name)
			args.insert(self.body_index, envelope.body.content)
		if self.header_type is not None:
			if envelope.header is None:
				raise f.MissingHeaderFault(action_name)
			args.insert(self.header_index, envelope.header)
		return args

	def response_from(
			self,
			ret_obj: t.Optional[MessageBody],
			header: XroadHeader
	) -> t.Optional[SoapResponse]:
		has_return = self.return_type is not None
		if not has_return and ret_obj is None:
			return None
		elif has_return and isinstance(ret_obj, self.return_type):
			return SoapResponse(content=ret_obj, header=header)
		raise TypeError(
			f"Expected return type {self.return_type}, "
			f"but received {ret_obj}"
		)

	def parse(self, http_body: bytes, content_type: t.Optional[str]) -> GenericEnvelope:
		body_ct = content_type.split(';')[0]

		if body_ct == "multipart/related":
			files: t.List[DecodedBodyPart] = list()
			decoder1 = MultipartDecoder(http_body, content_type)
			envelope = None

			for index, part1 in enumerate(decoder1.parts):
				if index == 0:
					envelope = part1
				elif part1.is_mixed_multipart:
					content_type = part1.headers.get('content-type')
					decoder2 = MultipartDecoder(part1.content, content_type)
					for part2 in decoder2.parts:
						files.append(part2)
				else:
					files.append(part1)

			xml_str = envelope.content
			for file in files:
				fingerprint = self.storage.insert_object(file)
				xml_str = xml_str.replace(
					file.content_id.encode(),
					fingerprint.encode()
				)
			http_body = xml_str

		elif body_ct not in ["text/xml", "application/xml", "application/soap+xml"]:
			raise f.ClientFault(f"Invalid content type: {body_ct}")

		factory = EnvelopeFactory
		if self.body_type is not None:
			factory = EnvelopeFactory[self.body_type]
		return factory().deserialize(http_body)
