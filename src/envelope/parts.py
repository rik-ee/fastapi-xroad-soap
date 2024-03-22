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
from pydantic_xml import (
	BaseXmlModel,
	element as Element,
	attr as Attribute
)
from typing import (
	ClassVar, TypeVar, Dict, Generic,
	Optional, TypeAlias, Callable
)
from src.envelope.header import XroadHeader
from src.constants import ENV_NSMAP


__all__ = [
	"Element",
	"Attribute",
	"MessageBody",
	"MessageBodyType",
	"FactoryAlias",
	"GenericBody",
	"GenericEnvelope",
	"GenericFault"
]


class MessageBody(BaseXmlModel):
	pass


MessageBodyType = TypeVar("MessageBodyType", bound=MessageBody)
FactoryAlias: TypeAlias = Callable[..., MessageBodyType]


class GenericBody(MessageBody, Generic[MessageBodyType], tag='Body'):
	content: MessageBodyType


class GenericEnvelope(MessageBody, Generic[MessageBodyType], tag="Envelope"):
	ns: ClassVar[str]
	nsmap: ClassVar[Dict[str, str]]
	header: Optional[XroadHeader] = None
	body: MessageBodyType


class GenericFault(MessageBody, Generic[MessageBodyType], tag="Fault", ns="soapenv", nsmap=ENV_NSMAP):
	envelope: ClassVar[FactoryAlias]
	faultcode: str = Element(tag="faultcode", ns='')
	faultstring: str = Element(tag="faultstring", ns='')
	faultactor: str = Element(tag="faultactor", ns='')
	detail: MessageBodyType = Element(tag="detail", ns='', default=None)
