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
import quopri
import base64
import typing as t
from email.parser import HeaderParser
from email.message import Message
from .errors import (
    InvalidSeparatorError,
    MissingContentIDError
)
from .. import utils


__all__ = ["DecodedBodyPart"]


class DecodedBodyPart:
    headers: t.Optional[Message] = None
    file_name: t.Optional[str] = None
    content: t.Optional[bytes] = None
    content_id: t.Optional[str] = None
    is_mixed_multipart: bool = False

    def __init__(self, content: bytes) -> None:
        separator = b'\r\n\r\n'
        if separator not in content:
            raise InvalidSeparatorError()

        headers, content = utils.split_on_find(content, separator)
        if headers:
            decoded: str = utils.detect_decode(headers)[0]
            self.headers = HeaderParser().parsestr(decoded)

            if content:
                self.content = content
                content_type = self.headers.get_content_type()
                content_disp = self.headers.get_content_disposition()
                boundary = self.headers.get_boundary()

                if content_type and "multipart/mixed" in content_type:
                    self.is_mixed_multipart = True
                elif content_disp == "attachment" and boundary is None:
                    self.content = self.decode_transfer(content)
                    self.set_file_metadata()

    def decode_transfer(self, content: bytes) -> bytes:
        transfer_enc = self.headers.get("Content-Transfer-Encoding")
        if transfer_enc == "base64":
            return base64.b64decode(content)
        elif transfer_enc == "quoted-printable":
            return quopri.decodestring(content)
        elif transfer_enc == "binary":
            return content
        return content

    def set_file_metadata(self) -> None:
        boundary = self.headers.get_boundary()
        content_disp = self.headers.get_content_disposition()
        if boundary is None and content_disp == "attachment":
            self.file_name = self.headers.get_filename()
            if self.file_name is None:
                self.file_name = self.headers.get_param(
                    header='content-disposition',
                    param='name'
                )
            cid = self.headers.get("Content-ID")
            if cid is None:
                raise MissingContentIDError
            cid = f"cid:{cid.lstrip('<').rstrip('>')}"
            self.content_id = cid
