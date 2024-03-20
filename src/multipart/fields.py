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
import warnings
import mimetypes
import email.utils
import typing as t


_TYPE_FIELD_VALUE = t.Union[str, bytes]
_TYPE_FIELD_VALUE_TUPLE = t.Union[
    t.Tuple[str, _TYPE_FIELD_VALUE, str],
    t.Tuple[str, _TYPE_FIELD_VALUE],
    _TYPE_FIELD_VALUE,
]


def guess_content_type(
        filename: t.Union[str, None],
        default: str = "application/octet-stream"
) -> str:
    return mimetypes.guess_type(filename)[0] or default


def format_header_param_rfc2231(name: str, value: _TYPE_FIELD_VALUE) -> str:
    warnings.warn(
        "'format_header_param_rfc2231' is deprecated and will be "
        "removed in urllib3 v2.1.0. This is not valid for "
        "multipart/form-data header parameters.",
        DeprecationWarning,
        stacklevel=2,
    )

    if isinstance(value, bytes):
        value = value.decode("utf-8")

    if not any(ch in value for ch in '"\\\r\n'):
        result = f'{name}="{value}"'
        try:
            result.encode("ascii")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        else:
            return result

    value = email.utils.encode_rfc2231(value, "utf-8")
    value = f"{name}*={value}"

    return value


def format_multipart_header_param(name: str, value: _TYPE_FIELD_VALUE) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    value = value.translate({10: "%0A", 13: "%0D", 34: "%22"})
    return f'{name}="{value}"'


def format_header_param_html5(name: str, value: _TYPE_FIELD_VALUE) -> str:
    warnings.warn(
        "'format_header_param_html5' has been renamed to "
        "'format_multipart_header_param'. The old name will be "
        "removed in urllib3 v2.1.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return format_multipart_header_param(name, value)


def format_header_param(name: str, value: _TYPE_FIELD_VALUE) -> str:
    warnings.warn(
        "'format_header_param' has been renamed to "
        "'format_multipart_header_param'. The old name will be "
        "removed in urllib3 v2.1.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return format_multipart_header_param(name, value)


class RequestField:
    def __init__(
        self,
        name: str,
        data: _TYPE_FIELD_VALUE,
        filename: str | None = None,
        headers: t.Mapping[str, str] | None = None,
        header_formatter: t.Union[t.Callable[[str, _TYPE_FIELD_VALUE], str], None] = None,
    ):
        self._name = name
        self._filename = filename
        self.data = data
        self.headers: dict[str, str | None] = {}
        if headers:
            self.headers = dict(headers)

        if header_formatter is not None:
            warnings.warn(
                "The 'header_formatter' parameter is deprecated and "
                "will be removed in urllib3 v2.1.0.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.header_formatter = header_formatter
        else:
            self.header_formatter = format_multipart_header_param

    @classmethod
    def from_tuples(
        cls,
        fieldname: str,
        value: _TYPE_FIELD_VALUE_TUPLE,
        header_formatter: t.Union[t.Callable[[str, _TYPE_FIELD_VALUE], str], None] = None,
    ) -> RequestField:
        filename: str | None
        content_type: str | None
        data: _TYPE_FIELD_VALUE
        if isinstance(value, tuple):
            if len(value) == 3:
                filename, data, content_type = value
            else:
                filename, data = value
                content_type = guess_content_type(filename)
        else:
            filename = None
            content_type = None
            data = value
        request_param = cls(
            fieldname, data, filename=filename, header_formatter=header_formatter
        )
        request_param.make_multipart(content_type=content_type)
        return request_param

    def _render_part(self, name: str, value: _TYPE_FIELD_VALUE) -> str:
        return self.header_formatter(name, value)

    def _render_parts(
        self,
        header_parts: t.Union[
            dict[str, _TYPE_FIELD_VALUE | None],
            t.Sequence[t.Tuple[str, t.Union[_TYPE_FIELD_VALUE | None]]]
        ],
    ) -> str:
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
        content_disposition = (content_disposition or "form-data") + "; ".join(
            [
                "",
                self._render_parts(
                    (("name", self._name), ("filename", self._filename))
                ),
            ]
        )
        self.headers["Content-Disposition"] = content_disposition
        self.headers["Content-Type"] = content_type
        self.headers["Content-Location"] = content_location
