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
from fastapi_xroad_soap.internal.envelope.header import XroadHeader
from fastapi_xroad_soap.internal.envelope.generics import GenericEnvelope, GenericBody, GenericFault
from fastapi_xroad_soap.internal.envelope.base import MessageBody, MessageBodyType
from fastapi_xroad_soap.internal.constants import ENV_NSMAP, XRO_NSMAP, IDEN_NSMAP


__all__ = ["EnvelopeFactory"]


class EnvelopeFactory(t.Generic[MessageBodyType]):
	_type: t.ClassVar[t.Type[MessageBody]]

	def __class_getitem__(cls, content_type: t.Type[MessageBody]):
		cls_name = f"{cls.__name__}[{content_type.__name__}]"
		if content_type.__xml_tag__ is None:
			content_type.__xml_tag__ = content_type.__name__
		return type(cls_name, (cls,), {"_type": content_type})

	def __init__(self) -> None:
		nsmap = {**ENV_NSMAP}
		if not issubclass(self._type, GenericFault):
			nsmap.update({**XRO_NSMAP, **IDEN_NSMAP})
			if isinstance(self._type.__xml_nsmap__, dict):
				nsmap.update(self._type.__xml_nsmap__)
		self._factory = t.cast(GenericEnvelope, type(
			'Factory', (GenericEnvelope,), {},
			ns="soapenv", nsmap=nsmap
		))

	def serialize(
			self,
			content: MessageBody,
			header: XroadHeader = None,
			pretty_print: bool = False,
			skip_empty: bool = False,
			standalone: bool = False,
			encoding: str = 'utf-8'
	) -> bytes:
		if content.__class__ != self._type:
			raise TypeError(
				f"Cannot use '{content.__class__.__name__}' type instances "
				f"with '{self._type.__name__}' type envelope factory."
			)
		body_type = GenericBody[content.__class__]
		body = body_type(content=content)

		factory = self._factory[body_type]
		obj = factory(header=header, body=body)

		return obj.to_xml(
			pretty_print=pretty_print,
			skip_empty=skip_empty,
			standalone=standalone,
			encoding=encoding
		)

	def deserialize(self, content: t.Union[str, bytes]) -> MessageBodyType:
		"""
		:param content: The XML string to be deserialized into an object.
		:raises pydantic.ValidationError: When the input XML string does
			not conform to the EnvelopeFactory subtype.
		:raises lxml.etree.LxmlError: When the input XML string contains
			syntax or structural errors.
		:return: An instance of MessageBody
		"""
		if not isinstance(content, bytes):
			content = content.encode("utf-8")

		model = self._factory[GenericBody[self._type]]
		return model.from_xml(content)
