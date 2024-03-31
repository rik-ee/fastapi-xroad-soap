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
from __future__ import annotations
import typing as t
from .. import helpers


__all__ = ["RequestField"]


_TYPE_FIELD_VALUE = t.Union[str, bytes]
_TYPE_FIELD_VALUE_TUPLE = t.Union[
    t.Tuple[str, _TYPE_FIELD_VALUE, str],
    t.Tuple[str, _TYPE_FIELD_VALUE],
    _TYPE_FIELD_VALUE,
]
_TYPE_HEADER_PARTS = t.Union[
    t.Dict[str, t.Union[_TYPE_FIELD_VALUE, None]],
    t.Sequence[t.Tuple[str, t.Union[_TYPE_FIELD_VALUE, None]]]
]


class RequestField:
    def __init__(
        self,
        name: str,
        data: _TYPE_FIELD_VALUE,
        filename: t.Optional[str] = None,
        headers: t.Optional[t.Mapping[str, str]] = None
    ):
        self._name = name
        self._filename = filename
        self.data = data
        self.headers: t.Dict[str, t.Union[str, None]] = {}
        if headers:
            self.headers = dict(headers)

    @classmethod
    def from_tuples(cls, field_name: str, value: _TYPE_FIELD_VALUE_TUPLE) -> RequestField:
        filename: str | None
        content_type: str | None
        data: _TYPE_FIELD_VALUE
        if isinstance(value, tuple):
            if len(value) == 3:
                filename, data, content_type = value
            else:
                filename, data = value
                content_type = helpers.guess_mime_type(filename)
        else:
            filename = None
            content_type = None
            data = value
        request_param = cls(field_name, data, filename=filename)
        request_param.make_multipart(content_type=content_type)
        return request_param

    @staticmethod
    def _render_part(name: str, value: _TYPE_FIELD_VALUE) -> str:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        value = value.translate({10: "%0A", 13: "%0D", 34: "%22"})
        return f'{name}="{value}"'

    def _render_parts(self, header_parts: _TYPE_HEADER_PARTS) -> str:
        iterable: t.Iterable[t.Tuple[str, t.Union[_TYPE_FIELD_VALUE, None]]]
        parts = []
        if isinstance(header_parts, dict):
            iterable = header_parts.items()
        else:
            iterable = header_parts
        for name, value in iterable:
            if value is not None:
                parts.append(self._render_part(name, value))
        return "; ".join(parts)

    def render_headers(self) -> str:
        lines = []
        sort_keys = ["Content-Disposition", "Content-Type", "Content-Location"]
        for sort_key in sort_keys:
            if self.headers.get(sort_key, False):
                lines.append(f"{sort_key}: {self.headers[sort_key]}")
        for header_name, header_value in self.headers.items():
            if header_name not in sort_keys:
                if header_value:
                    lines.append(f"{header_name}: {header_value}")
        lines.append("\r\n")
        return "\r\n".join(lines)

    def make_multipart(
        self,
        content_disposition: t.Union[str, None] = None,
        content_type: t.Union[str, None] = None,
        content_location: t.Union[str, None] = None,
    ) -> None:
        content_disposition = (content_disposition or "form-data") + "; ".join([
            "",
            self._render_parts((
                ("name", self._name),
                ("filename", self._filename)
            )),
        ])
        self.headers["Content-Disposition"] = content_disposition
        self.headers["Content-Type"] = content_type
        self.headers["Content-Location"] = content_location
