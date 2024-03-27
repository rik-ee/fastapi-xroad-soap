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
from fastapi_xroad_soap.internal.soap.faults import ClientFault
from fastapi_xroad_soap.internal.envelope import (
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

	class ReturnTypeError(Exception):
		def __init__(self, ret_obj: t.Any):
			super().__init__(f"Unexpected return type: {ret_obj}")

	def parse(self, http_body: bytes, content_type: t.Optional[str]) -> GenericEnvelope:
		if "text/xml" in content_type:
			factory = EnvelopeFactory
			if self.body_type is not None:
				factory = EnvelopeFactory[self.body_type]
			return factory().deserialize(http_body)
		return None  # TODO: parse multipart body into xml model

	def arguments_from(self, envelope: GenericEnvelope) -> t.List[t.Union[MessageBody, XroadHeader]]:
		args = list()
		if self.body_type is not None:
			if envelope.body is None:
				raise ClientFault(f"Body element missing from envelope for {self.name} SOAP action.")
			args.insert(self.body_index, envelope.body.content)
		if self.header_type is not None:
			args.insert(self.header_index, envelope.header)
		return args

	def response_from(self, ret_obj: t.Optional[MessageBody], header: XroadHeader) -> t.Optional[Response]:
		if self.return_type is None and ret_obj is None:
			return None
		elif isinstance(ret_obj, MessageBody):
			envelope = EnvelopeFactory[ret_obj.__class__]()
			return Response(envelope.serialize(
				content=ret_obj,
				header=header
			))
		raise self.ReturnTypeError(ret_obj)
