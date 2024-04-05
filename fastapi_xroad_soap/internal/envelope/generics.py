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
from pydantic_xml import element
from ..constants import ENV_NSMAP
from .base import MessageBody, MessageBodyType
from .header import XroadHeader


__all__ = [
	"GenericEnvelope",
	"GenericFault",
	"GenericBody",
	"AnyBody"
]


bases = [MessageBody, t.Generic[MessageBodyType]]


class GenericEnvelope(*bases, tag="Envelope", nsmap=ENV_NSMAP, search_mode='unordered'):
	header: t.Optional[XroadHeader] = element(tag="Header", default=None)
	body: MessageBodyType = element(tag="Body", default=None)


class GenericFault(*bases, tag="Fault", ns="soapenv", nsmap=ENV_NSMAP):
	faultcode: str = element(tag="faultcode", ns='')
	faultstring: str = element(tag="faultstring", ns='')
	faultactor: t.Optional[str] = element(tag="faultactor", ns='', default=None)
	detail: MessageBodyType = element(tag="detail", ns='', default=None)


class GenericBody(*bases, tag="Body", nsmap=ENV_NSMAP):
	content: MessageBodyType


class AnyBody(MessageBody, tag="Body", nsmap=ENV_NSMAP):
	content: t.Optional[MessageBody] = element(default_factory=MessageBody)
