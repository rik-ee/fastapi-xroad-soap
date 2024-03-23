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
from pydantic_xml import BaseXmlModel, element as Element, attr as Attribute
from typing import TypeVar


__all__ = [
	"Element",
	"Attribute",
	"BaseXmlModel",
	"MessageBody",
	"MessageBodyType"
]


MessageBody = type("MessageBody", (BaseXmlModel,), {})
MessageBodyType = TypeVar("MessageBodyType", bound=MessageBody)
