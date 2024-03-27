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
from fastapi_xroad_soap.internal.soap import SoapAction


__all__ = ["generate"]


def generate(actions: t.Dict[str, SoapAction], name: str, tns: str) -> bytes:
	return b"dynamically generated wsdl"  # TODO: Implement generator logic
