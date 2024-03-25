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
from fastapi_xroad_soap.internal.errors import BaseError
from fastapi_xroad_soap.internal.soap.response import SoapResponse
from fastapi_xroad_soap.internal.envelope import (
	GenericFault,
	MessageBody
)


__all__ = [
	"SoapFault",
	"InvalidMethodFault",
	"InvalidActionFault",
	"ClientFault",
	"ServerFault"
]


class SoapFault(BaseError):
	def __init__(
			self,
			code: str = "Client",
			string: str = "Bad Request",
			actor: t.Optional[str] = None,
			detail: t.Optional[MessageBody] = None,
			http_status_code: t.Optional[int] = 400
	) -> None:
		fault_type = MessageBody
		kwargs = dict(
			faultcode=code,
			faultstring=string,
			faultactor=actor
		)
		if isinstance(detail, MessageBody):
			fault_type = detail.__class__
			kwargs["detail"] = detail

		typed_fault = GenericFault[fault_type]
		fault = typed_fault(**kwargs)

		self.response = SoapResponse(
			http_status_code=http_status_code,
			content=fault,
			header=None
		)


class InvalidMethodFault(SoapFault):
	def __init__(self, method: str) -> None:
		super().__init__(
			string=f"Service does not support {method} method for SOAP action requests"
		)


class InvalidActionFault(SoapFault):
	def __init__(self, action: str) -> None:
		super().__init__(
			string=f"Service does not support SOAP action: '{action}'"
		)


class ClientFault(SoapFault):
	def __init__(self, ex: Exception) -> None:
		super().__init__(string=str(ex))


class ServerFault(SoapFault):
	def __init__(self, ex: Exception) -> None:
		super().__init__(
			http_status_code=500,
			string=str(ex),
			code="Server"
		)
