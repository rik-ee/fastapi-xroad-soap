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
from email.parser import HeaderParser
from fastapi_xroad_soap.internal.multipart.errors import CorruptMultipartError, NonMultipartError
from fastapi_xroad_soap.internal.multipart.structures import CaseInsensitiveDict
from fastapi_xroad_soap.internal.multipart.encoder import encode_with


def _split_on_find(content: t.Union[str, bytes], bound: t.Union[str, bytes]):
    point = content.find(bound)
    return content[:point], content[point + len(bound):]


def _header_parser(string: bytes, encoding: str):
    string = string.decode(encoding)
    headers = HeaderParser().parsestr(string).items()
    return ((
        encode_with(k, encoding),
        encode_with(v, encoding)
    ) for k, v in headers)


class BodyPart:
    def __init__(self, content: bytes, encoding: str) -> None:
        self.encoding = encoding
        headers = {}
        if b'\r\n\r\n' in content:
            first, self.content = _split_on_find(content, b'\r\n\r\n')
            if first != b'':
                headers = _header_parser(first.lstrip(), encoding)
        else:
            raise CorruptMultipartError()
        self.headers = CaseInsensitiveDict(headers)

    @property
    def text(self) -> str:
        return self.content.decode(self.encoding)


class MultipartDecoder:
    def __init__(self, content, content_type, encoding='utf-8') -> None:
        self.content_type = content_type
        self.encoding = encoding
        self.parts = tuple()
        self._find_boundary()
        self._parse_body(content)

    def _find_boundary(self):
        ct_info = tuple(x.strip() for x in self.content_type.split(';'))
        mimetype = ct_info[0]
        if mimetype.split('/')[0].lower() != 'multipart':
            raise NonMultipartError(mimetype)
        for item in ct_info[1:]:
            attr, value = _split_on_find(
                item,
                '='
            )
            if attr.lower() == 'boundary':
                self.boundary = encode_with(value.strip('"'), self.encoding)

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
            return BodyPart(fixed, self.encoding)

        def test_part(part):
            return (part != b'' and
                    part != b'\r\n' and
                    part[:4] != b'--\r\n' and
                    part != b'--')

        parts = content.split(b''.join((b'\r\n', boundary)))
        self.parts = tuple(body_part(x) for x in parts if test_part(x))

    @classmethod
    def from_response(cls, response, encoding='utf-8'):
        content = response.content
        content_type = response.headers.get('content-type', None)
        return cls(content, content_type, encoding)
