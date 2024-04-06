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
from dataclasses import dataclass
from pydantic import ValidationError
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
			self.validate_files(xml_str, files)
			for file in files:
				cid = file.content_id.encode()
				uid = self.storage.insert_object(file).encode()
				xml_str = xml_str.replace(cid, uid)
			http_body = xml_str
		elif body_ct not in ["text/xml", "application/xml", "application/soap+xml"]:
			raise f.ClientFault(f"Invalid content type: {body_ct}")
		return self.deserialize(http_body)

	@staticmethod
	def validate_files(xml_str: bytes, files: t.List[DecodedBodyPart]) -> None:
		ids = [file.content_id for file in files]
		for cid in ids:
			if ids.count(cid) > 1:
				raise f.DuplicateCIDFault(cid)
		for file in files:
			cid = file.content_id
			count = xml_str.count(cid.encode())
			if count == 0:
				raise f. MissingCIDFault(cid)
			elif count > 1:
				raise f.DuplicateCIDFault(cid)

	def deserialize(self, http_body: bytes) -> GenericEnvelope:
		if self.body_type is None:
			return EnvelopeFactory().deserialize(http_body)
		try:
			factory = EnvelopeFactory[self.body_type]
			return factory().deserialize(http_body)
		except ValidationError:
			extra_nsmap = self.extract_extra_nsmap(http_body)
			name = f"Namespaced{self.body_type.__name__}"
			last_err = None
			for ns in extra_nsmap.keys():
				new = t.cast(t.Type[MessageBody], type(
					name, (self.body_type,), {},
					ns=ns, nsmap=extra_nsmap
				))
				attrs = self.body_type.__private_attributes__
				new.__private_attributes__ = attrs
				try:
					factory = EnvelopeFactory[new]
					return factory().deserialize(http_body)
				except ValidationError as ex:
					last_err = ex
			raise last_err

	@staticmethod
	def extract_extra_nsmap(http_body: bytes) -> t.Dict[str, str]:
		pattern = r'<.*?Envelope\s*([^>]*)>'
		match = re.search(pattern, http_body.decode(), re.IGNORECASE)
		if match is None:
			raise f.ClientFault(f"Unexpected envelope structure")
		nsmap = dict()
		for raw_ns in match.group(1).split(' '):
			key, value = raw_ns[len('xmlns:'):].split('=')  # type: str, str
			if key not in HEADER_NSMAP:
				nsmap[key] = value.strip('"')
		return nsmap
