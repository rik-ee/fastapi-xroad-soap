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
from pydantic_xml import (
	element as Element,
	attr as Attribute,
	BaseXmlModel
)


__all__ = [
	"Element",
	"Attribute",
	"BaseXmlModel",
	"MessageBody",
	"MessageBodyType"
]


class MessageBody(BaseXmlModel):
	pass


MessageBodyType = t.TypeVar(
	"MessageBodyType",
	bound=MessageBody
)
