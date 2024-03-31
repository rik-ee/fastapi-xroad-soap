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
from .bodypart import DecodedBodyPart
from ..errors import NonMultipartError
from .. import helpers


__all__ = ["MultipartDecoder"]


class MultipartDecoder:
    def __init__(self, content, content_type) -> None:
        self.content_type = content_type
        self.parts: t.Tuple[DecodedBodyPart, ...] = tuple()
        self._find_boundary()
        self._parse_body(content)

    def _find_boundary(self):
        ct_info = tuple(x.strip() for x in self.content_type.split(';'))
        mimetype = ct_info[0]
        if mimetype.split('/')[0].lower() != 'multipart':
            raise NonMultipartError(mimetype)
        for item in ct_info[1:]:
            attr, value = helpers.split_on_find(item, separator='=')
            if attr.lower() == 'boundary':
                self.boundary = helpers.encode_with(value.strip('"'))

    @staticmethod
    def _fix_first_part(part, boundary_marker):
        bm_len = len(boundary_marker)
        if boundary_marker == part[:bm_len]:
            return part[bm_len:]
        return part

    def _parse_body(self, content: bytes) -> None:
        boundary = b''.join((b'--', self.boundary))

        def body_part(part):
            fixed = MultipartDecoder._fix_first_part(part, boundary)
            return DecodedBodyPart(fixed)

        def test_part(part):
            return (part != b'' and
                    part != b'\r\n' and
                    part[:4] != b'--\r\n' and
                    part != b'--')

        parts = content.split(b''.join((b'\r\n', boundary)))
        self.parts = tuple(body_part(x) for x in parts if test_part(x))
