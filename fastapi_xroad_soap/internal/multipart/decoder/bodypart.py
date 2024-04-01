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
from ..errors import (
    CorruptMultipartError,
    MissingContentIDError
)
from .. import helpers


__all__ = ["DecodedBodyPart"]


class DecodedBodyPart:
    headers: t.Optional[Message] = None
    file_name: t.Optional[str] = None
    mime_type: t.Optional[str] = None
    content: t.Optional[bytes] = None
    content_id: t.Optional[str] = None
    is_mixed_multipart: bool = False

    def __init__(self, content: bytes) -> None:
        separator = b'\r\n\r\n'
        if separator not in content:
            raise CorruptMultipartError()

        headers, content = helpers.split_on_find(content, separator)
        if headers:
            dec_headers = helpers.detect_decode(headers)[0]
            self.headers = HeaderParser().parsestr(dec_headers)

            if content:
                self.content = content
                content_type = self.headers.get_content_type()
                content_disp = self.headers.get_content_disposition()
                boundary = self.headers.get_boundary()

                if content_type and "multipart/mixed" in content_type:
                    self.is_mixed_multipart = True
                elif content_disp == "attachment" and boundary is None:
                    self.set_decode_content(content)
                    self.set_file_metadata()

    def set_decode_content(self, content: bytes) -> None:
        transfer_enc = self.headers.get("Content-Transfer-Encoding")
        if transfer_enc == "binary":
            return
        elif transfer_enc == "base64":
            content = base64.b64decode(content)
        elif transfer_enc == "quoted-printable":
            content = quopri.decodestring(content)
        dec_content, encoding = helpers.detect_decode(content)
        if encoding not in [None, 'utf-8']:
            content = dec_content.encode('utf-8')
        self.content = content

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
            self.mime_type = helpers.guess_mime_type(self.file_name)
            cid = self.headers.get("Content-ID")
            if cid is None:
                raise MissingContentIDError
            cid = f"cid:{cid.lstrip('<').rstrip('>')}"
            self.content_id = cid
