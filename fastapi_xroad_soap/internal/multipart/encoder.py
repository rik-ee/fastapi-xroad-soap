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
from email import policy
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from ..elements import SwaRefInternal


__all__ = ["MultipartEncoder"]


class MultipartEncoder:
	def __init__(self, content: bytes, files: t.List[SwaRefInternal]) -> None:
		multipart = self.compute_multipart(content, files)
		headers, message = multipart.split(b"\r\n\r\n", 1)
		self.headers = self.raw_headers_to_dict(headers)
		self.message = b'\r\n' + message  # type: bytes
		self.headers["Content-Length"] = str(len(self.message))

	@classmethod
	def compute_multipart(cls, xml_str: bytes, files: t.List[SwaRefInternal]) -> bytes:
		root = MIMEMultipart("related", type="text/xml", start="<rootpart>")
		cls.attach_soap_envelope(xml_str, root)
		if len(files) > 1:
			mixed = MIMEMultipart("mixed")
			mixed.add_header("Content-Transfer-Encoding", "binary")
			for file in files:
				cls.attach_file(file, mixed)
			root.attach(mixed)
		else:
			cls.attach_file(files[0], root)
		return root.as_bytes(policy=policy.HTTP)

	@staticmethod
	def attach_soap_envelope(xml_str: bytes, parent: MIMEMultipart):
		part = MIMEText(xml_str.decode('utf-8'))
		part.replace_header("Content-Transfer-Encoding", "8bit")
		part.replace_header("Content-Type", "text/xml; charset=UTF-8")
		part.add_header("Content-ID", "<rootpart>")
		parent.attach(part)

	@staticmethod
	def attach_file(file: SwaRefInternal, parent: MIMEMultipart):
		part = MIMEBase(*file.mimetype.split('/'))
		part.add_header("Content-ID", file.mime_cid)
		part.add_header("Content-Digest", file.digest)
		part.add_header("Content-Length", str(file.size))
		part.add_header('Content-Disposition', '; '.join([
			"attachment", f'name="{file.name}"', f'filename="{file.name}"'
		]))
		part.set_payload(file.content)
		encoders.encode_base64(part)
		parent.attach(part)

	@staticmethod
	def raw_headers_to_dict(raw_headers: bytes) -> t.Dict[str, str]:
		headers = dict()
		parts = raw_headers.split(b"\r\n")
		for part in parts:
			key, value = part.decode().split(': ')
			headers[key] = value
		return headers
