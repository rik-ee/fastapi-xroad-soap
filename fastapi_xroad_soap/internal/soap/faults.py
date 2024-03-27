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
import re
import typing as t
from pydantic_xml import element
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
	"ServerFault",
	"ValidationFault"
]


class SoapFault(Exception):
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
		msg = f"Service does not support {method} method for SOAP action requests"
		super().__init__(string=msg)


class InvalidActionFault(SoapFault):
	def __init__(self, action: str) -> None:
		msg = f"Service does not support SOAP action: '{action}'"
		super().__init__(string=msg)


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


class ValidationFault(SoapFault):
	def __init__(self, ex: Exception) -> None:
		error = str(ex)
		match = re.search(r"^(.*?)\sfor", error)
		string = match.group(1) if match else "validation error"
		super().__init__(
			http_status_code=400,
			detail=self.extract_details(error),
			string=string + " for request",
			code="Client"
		)

	@staticmethod
	def extract_details(error: str) -> MessageBody:
		class Detail(MessageBody):
			location: str = element()
			reason: str = element()
			input_value: str = element()

		class ErrorDetails(MessageBody):
			details: t.List[Detail] = element(tag="validationError")

		details = list()
		pattern = r"(body\..+?)(?=\nbody\.|\Z)"
		matches = re.findall(pattern, error, re.DOTALL)
		for match in matches:
			loc, msg = match.split('\n')
			ln_match = re.search(r"(\[line \d+]: )", msg)
			em_match = re.search(r"\[line \d+]: (.+?) \[type=", msg)
			iv_match = re.search(r"\[type=.+?, input_value='(.+?)',", msg)
			details.append(Detail(
				location=(ln_match.group(1) + loc) if ln_match else "unknown",
				reason=em_match.group(1) if em_match else "unknown",
				input_value=iv_match.group(1) if iv_match else "unknown"
			))
		return ErrorDetails(details=details)
