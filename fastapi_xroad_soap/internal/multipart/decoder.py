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
import chardet
from charset_normalizer import from_bytes
from email.parser import HeaderParser
from fastapi_xroad_soap.internal.multipart.structures import CaseInsensitiveDict
from fastapi_xroad_soap.internal.multipart import errors, helpers
from fastapi_xroad_soap.internal.utils import content_utils


__all__ = ["BodyPart", "MultipartDecoder"]


class BodyPart:
    def __init__(self, content: bytes) -> None:
        separator = b'\r\n\r\n'
        if separator not in content:
            raise errors.CorruptMultipartError()

        self.headers = CaseInsensitiveDict()
        self.content, self.encoding = b'', ''

        header, content = helpers.split_on_find(content, separator)
        if header:
            decoded_header = content_utils.detect_decode(header)[0]
            header_msg = HeaderParser().parsestr(decoded_header)
            self.headers = CaseInsensitiveDict(dict(header_msg))
        if content:
            ct_enc = self.headers.get("Content-Transfer-Encoding")
            if ct_enc == "quoted-printable":
                content = quopri.decodestring(content)
            dec_content, self.encoding = content_utils.detect_decode(content)
            if self.encoding not in [None, 'utf-8']:
                content = dec_content.encode('utf-8')
            self.content = content


class MultipartDecoder:
    def __init__(self, content, content_type, encoding: str = None) -> None:
        self.content_type = content_type
        self.encoding = encoding
        self.parts = tuple()
        self._find_boundary()
        self._parse_body(content)

    def _find_boundary(self):
        ct_info = tuple(x.strip() for x in self.content_type.split(';'))
        mimetype = ct_info[0]
        if mimetype.split('/')[0].lower() != 'multipart':
            raise errors.NonMultipartError(mimetype)
        for item in ct_info[1:]:
            attr, value = helpers.split_on_find(item, separator='=')
            if attr.lower() == 'boundary':
                self.boundary = helpers.encode_with(value.strip('"'))

    @staticmethod
    def _fix_first_part(part, boundary_marker):
        bm_len = len(boundary_marker)
        if boundary_marker == part[:bm_len]:
            return part[bm_len:]
        else:
            return part

    def _parse_body(self, content: bytes) -> None:
        boundary = b''.join((b'--', self.boundary))

        def body_part(part):
            fixed = MultipartDecoder._fix_first_part(part, boundary)
            return BodyPart(fixed)

        def test_part(part):
            return (part != b'' and
                    part != b'\r\n' and
                    part[:4] != b'--\r\n' and
                    part != b'--')

        parts = content.split(b''.join((b'\r\n', boundary)))
        self.parts = tuple(body_part(x) for x in parts if test_part(x))
