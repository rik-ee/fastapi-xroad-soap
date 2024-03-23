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
from fastapi_xroad_soap.internal.constants import ENV_NSMAP
from fastapi_xroad_soap.internal.envelope.header import XroadHeader
from fastapi_xroad_soap.internal.envelope.base import Element, MessageBody, MessageBodyType


__all__ = ["GenericBody", "GenericEnvelope", "GenericFault"]


class GenericBody(MessageBody, t.Generic[MessageBodyType], tag='Body'):
	content: MessageBodyType


class GenericEnvelope(MessageBody, t.Generic[MessageBodyType], tag="Envelope"):
	header: t.Optional[XroadHeader] = None
	body: MessageBodyType


class GenericFault(MessageBody, t.Generic[MessageBodyType], tag="Fault", ns="soapenv", nsmap=ENV_NSMAP):
	faultcode: str = Element(tag="faultcode", ns='')
	faultstring: str = Element(tag="faultstring", ns='')
	faultactor: str = Element(tag="faultactor", ns='')
	detail: MessageBodyType = Element(tag="detail", ns='', default=None)
