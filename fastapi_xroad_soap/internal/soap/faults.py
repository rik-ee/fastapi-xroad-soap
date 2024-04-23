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
import inflection
from pydantic_xml import element
from ..base import MessageBody
from ..envelope import GenericFault
from .response import SoapResponse


__all__ = [
	"SoapFault",
	"ClientFault",
	"ServerFault",
	"InvalidMethodFault",
	"InvalidActionFault",
	"MissingActionFault",
	"MissingBodyFault",
	"MissingHeaderFault",
	"MissingCIDFault",
	"DuplicateCIDFault",
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


class ClientFault(SoapFault):
	def __init__(self, ex: t.Union[str, Exception]) -> None:
		super().__init__(string=str(ex))


class ServerFault(SoapFault):
	def __init__(self, ex: t.Union[str, Exception]) -> None:
		super().__init__(
			http_status_code=500,
			string=str(ex),
			code="Server"
		)


class InvalidMethodFault(SoapFault):
	def __init__(self, method: str) -> None:
		msg = f"Service does not support {method} method for SOAP action requests"
		super().__init__(string=msg)


class InvalidActionFault(SoapFault):
	def __init__(self, action: str) -> None:
		msg = f"Service does not support SOAP action: {action}"
		super().__init__(string=msg)


class MissingActionFault(SoapFault):
	def __init__(self):
		msg = "SOAP action HTTP header is missing"
		super().__init__(string=msg)


class MissingBodyFault(SoapFault):
	def __init__(self, action_name: str) -> None:
		msg = f"Body element missing from envelope for SOAP action: {action_name}"
		super().__init__(string=msg)


class MissingHeaderFault(SoapFault):
	def __init__(self, action_name: str) -> None:
		msg = f"X-Road header element missing from envelope for SOAP action: {action_name}"
		super().__init__(string=msg)


class MissingCIDFault(SoapFault):
	def __init__(self, cid: str) -> None:
		msg = f"Content-ID missing from envelope: {cid}"
		super().__init__(string=msg)


class DuplicateCIDFault(SoapFault):
	def __init__(self, cid: str) -> None:
		msg = f"Duplicate Content-ID not allowed: {cid[4:]}"
		super().__init__(string=msg)


class ValidationFault(SoapFault):
	def __init__(self, ex: Exception) -> None:
		error = str(ex)
		parts = re.split(r'\n(?!\s\s)', error)
		match = re.search(r"^(.*?)\sfor", parts[0])
		string = match.group(1) if match else "validation error"
		super().__init__(
			http_status_code=400,
			detail=self.extract_details(parts),
			string=string + " in SOAP envelope",
			code="Client"
		)

	@classmethod
	def extract_details(cls, parts: t.List[str]) -> MessageBody:
		class Detail(MessageBody):
			location: str = element()
			reason: str = element()
			input_value: str = element(tag="inputValue")

		class ErrorDetails(MessageBody):
			details: t.List[Detail] = element(tag="validationError")

		details = list()
		for part in parts:
			sub_parts = part.split('\n')
			loc, msg = sub_parts[:2]

			msg, input_value = cls.extract_input_value(msg)
			location = cls.extract_location(loc, msg)
			reason = cls.extract_reason(msg)

			params = [location, reason, input_value]
			if any(d != "Unknown" for d in params):
				details.append(Detail(
					location=location,
					reason=reason,
					input_value=input_value,
				))
		return ErrorDetails(details=details)

	@staticmethod
	def extract_input_value(msg: str) -> t.Tuple[str, str]:
		match = re.search(r"\$\$(.*?)\$\$", msg)
		if match:  # pragma: no cover
			msg = msg.replace(f"$${match.group(1)}$$", '')
		return msg, match.group(1) if match else "Unknown"

	@staticmethod
	def extract_reason(msg: str) -> str:
		match = re.search(r"\[line -?\d+]: (.+?) \[type=", msg)
		if match is None:
			match = re.search(r"^\s\s(.+?) \[type=", msg)
		return match.group(1) if match else "Unknown"

	@staticmethod
	def extract_location(loc: str, msg: str) -> str:
		ln_match = re.search(r"(\[line -?\d+]: )", msg)
		return inflection.camelize(loc) if ln_match else "Unknown"
