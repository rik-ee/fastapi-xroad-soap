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
from .errors import MultipartBoundaryError
from .. import utils


__all__ = ["MultipartDecoder"]


class MultipartDecoder:
    def __init__(self, content: bytes, content_type: str) -> None:
        self.parts: t.Tuple[DecodedBodyPart, ...] = tuple()
        self.boundary = self._find_boundary(content_type)
        self._parse_body(content)

    @staticmethod
    def _find_boundary(content_type) -> bytes:
        ct_info = tuple(x.strip() for x in content_type.split(';'))
        for item in ct_info[1:]:
            attr, value = utils.split_on_find(item, separator='=')
            if attr.lower() == 'boundary':
                return value.strip('"').encode('utf-8')
        raise MultipartBoundaryError

    @staticmethod
    def _fix_first_part(part, boundary_marker):
        bm_len = len(boundary_marker)
        if boundary_marker == part[:bm_len]:  # pragma: no cover
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
