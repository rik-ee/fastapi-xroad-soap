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
import re
import typing as t
from fastapi import Request, Response
from pydantic import (
	BaseModel,
	ValidationError,
	field_validator
)
from ..base import MessageBody
from ..storage import GlobalWeakStorage
from ..constants import HEADER_NSMAP
from ..multipart import (
	MultipartDecoder,
	DecodedBodyPart
)
from ..envelope import (
	EnvelopeFactory,
	GenericEnvelope,
	XroadHeader
)
from .response import SoapResponse
from . import faults as f


__all__ = ["SoapAction"]


_ArgsFrom = t.List[t.Union[MessageBody, XroadHeader]]
_RespFrom = t.Union[Response, SoapResponse]


class SoapAction(BaseModel, arbitrary_types_allowed=True):
	name: str
	handler: t.Callable[..., t.Optional[MessageBody]]
	description: t.Optional[str]
	body_type: t.Optional[t.Type[MessageBody]]
	body_index: t.Optional[int]
	header_type: t.Optional[t.Type[XroadHeader]]
	header_index: t.Optional[int]
	return_type: t.Optional[t.Type[MessageBody]]
	storage: GlobalWeakStorage

	# noinspection PyNestedDecorators
	@field_validator("name")
	@classmethod
	def validate_name(cls, value: t.Any) -> str:
		vl = len(value)
		if vl < 5 or vl > 30:
			raise ValueError(
				f"Invalid SOAP action name length {vl} chars for "
				f"name '{value}'. Length must be >= 5 and <= 30."
			)
		return value

	def arguments_from(self, envelope: GenericEnvelope) -> _ArgsFrom:
		args = list()
		if self.body_type is not None:
			if envelope.body is None:
				raise f.MissingBodyFault(self.name)
			args.insert(self.body_index, envelope.body.content)
		if self.header_type is not None:
			if envelope.header is None:
				raise f.MissingHeaderFault(self.name)
			args.insert(self.header_index, envelope.header)
		return args

	def response_from(
			self,
			ret: t.Optional[MessageBody] = None,
			header: t.Optional[XroadHeader] = None
	) -> _RespFrom:
		has_return = self.return_type is not None
		if not has_return and ret is None:
			return Response()
		elif has_return and isinstance(ret, self.return_type):
			return SoapResponse(content=ret, header=header)
		raise TypeError(f"Expected return type {self.return_type}, but received {ret}")

	async def parse(self, http_body: bytes, content_type: str) -> GenericEnvelope:
		body_type = content_type.split(';')[0]
		if body_type in ["text/xml", "application/xml", "application/soap+xml"]:
			return self.deserialize(http_body)
		elif body_type in ["multipart/related", "multipart/mixed"]:
			files: t.List[DecodedBodyPart] = list()
			decoder = MultipartDecoder(http_body, content_type)
			envelope = None
			for index, part in enumerate(decoder.parts):
				if index == 0:
					envelope = part
				elif part.is_mixed_multipart:
					content_type = part.headers.get('content-type')
					nested_decoder = MultipartDecoder(part.content, content_type)
					for nested_part in nested_decoder.parts:
						files.append(nested_part)
				else:
					files.append(part)
			http_body = self.process_files(envelope.content, files)
			return self.deserialize(http_body)
		raise f.ClientFault(f"Invalid content type: {body_type}")

	def process_files(self, xml_str: bytes, files: t.List[DecodedBodyPart]) -> bytes:
		ids = [file.content_id for file in files]
		for cid in ids:
			if ids.count(cid) > 1:
				raise f.DuplicateCIDFault(cid)
		for file in files:
			cid = file.content_id.encode()
			count = xml_str.count(cid)
			if count == 0:
				raise f.MissingCIDFault(cid.decode())
			elif count > 1:
				raise f.DuplicateCIDFault(cid.decode())
			uid = self.storage.insert_object(file).encode()
			xml_str = xml_str.replace(cid, uid)
		return xml_str

	def deserialize(self, http_body: bytes) -> GenericEnvelope:
		if self.body_type is None:
			return EnvelopeFactory().deserialize(http_body)

		extra_nsmap = self.extract_extra_nsmap(http_body)
		attrs = self.body_type.__private_attributes__
		name = self.body_type.__name__
		last_err = None

		def inner(**kwargs) -> GenericEnvelope:
			strict_type = t.cast(t.Type[MessageBody], type(
				name, (self.body_type,), {}, extra="forbid", **kwargs
			))
			strict_type.__private_attributes__ = attrs
			envelope = EnvelopeFactory[strict_type]()
			return envelope.deserialize(http_body)

		if not extra_nsmap:
			return inner()
		for ns in extra_nsmap.keys():
			try:
				return inner(ns=ns, nsmap=extra_nsmap)
			except ValidationError as ex:
				last_err = ex
		raise last_err

	@staticmethod
	def extract_extra_nsmap(http_body: bytes) -> t.Dict[str, str]:
		parts = re.split(r'>\s*<', http_body.decode(), maxsplit=1)
		match = re.search(r'envelope', parts[0], re.IGNORECASE)
		if len(parts) == 1 or match is None:
			raise f.ClientFault("Unexpected envelope structure")
		parts = re.split(r' |xmlns:', parts[0])
		nsmap = dict()
		for part in parts:
			if '=' not in part:
				continue
			key, value = part.split('=')  # type: str, str
			if key not in HEADER_NSMAP:
				nsmap[key] = value.strip('"')
		return nsmap
