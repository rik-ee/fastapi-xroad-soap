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
from dataclasses import dataclass
from fastapi_xroad_soap.internal.envelope import (
	XroadHeader,
	MessageBody
)


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
