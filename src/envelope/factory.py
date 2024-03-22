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
from typing import ClassVar, Type, Generic, Union, cast
from src.envelope.header import XroadHeader
from src.constants import ENV_NSMAP
from src.envelope.parts import *


__all__ = ["EnvelopeFactory"]


class EnvelopeFactory(Generic[MessageBodyType]):
	_type: ClassVar[Type[MessageBody]]

	def __class_getitem__(cls, content_type: Type[MessageBodyType]):
		cls_name = f"{cls.__name__}[{content_type.__name__}]"
		return type(cls_name, (cls,), {"_type": content_type})

	def __init__(self) -> None:
		nsmap = {**ENV_NSMAP, **(self._type.__xml_nsmap__ or {})}
		factory = type('Factory', (GenericEnvelope,), {}, ns="soapenv", nsmap=nsmap)
		self._factory_ = cast(Type[MessageBody], factory)

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
		factory = cast(
			Type[MessageBody],
			self._factory_[GenericBody[content.__class__]]
		)
		body = GenericBody[content.__class__](content=content)
		obj = factory(header=header, body=body)
		return obj.to_xml(
			pretty_print=pretty_print,
			skip_empty=skip_empty
		)

	def deserialize(self, content: Union[str, bytes]) -> MessageBodyType:
		if not isinstance(content, bytes):
			content = content.encode("utf-8")
		model = self._factory_[GenericBody[self._type]]
		return cast(self._type, model.from_xml(content))
