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
from ..constants import ENV_NSMAP
from .header import XroadHeader
from .base import MessageBody, MessageBodyType
from .generics import GenericEnvelope, GenericBody


__all__ = ["EnvelopeFactory"]


class EnvelopeFactory(t.Generic[MessageBodyType]):
	_type: t.ClassVar[t.Type[MessageBody]]

	def __class_getitem__(cls, content_type: t.Type[MessageBody]):
		cls_name = f"{cls.__name__}[{content_type.__name__}]"
		if content_type.__xml_tag__ is None:
			content_type.__xml_tag__ = content_type.__name__
		return type(cls_name, (cls,), {"_type": content_type})

	def __init__(self) -> None:
		nsmap = {**ENV_NSMAP, **(self._type.__xml_nsmap__ or {})}
		self._factory = t.cast(GenericEnvelope, type(
			'Factory', (GenericEnvelope,), {},
			ns="soapenv", nsmap=nsmap
		))

	def serialize(
			self,
			content: MessageBody,
			header: XroadHeader = None,
			pretty_print: bool = False,
			skip_empty: bool = False
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
			skip_empty=skip_empty
		)

	def deserialize(self, content: t.Union[str, bytes]) -> MessageBodyType:
		if not isinstance(content, bytes):
			content = content.encode("utf-8")

		model = self._factory[GenericBody[self._type]]
		return model.from_xml(content)
