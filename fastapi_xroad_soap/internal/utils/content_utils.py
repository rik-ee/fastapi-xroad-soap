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
import chardet
import mimetypes
import typing as t


__all__ = ["guess_content_type", "detect_decode"]


def guess_content_type(file_name: t.Union[str, None]) -> str:
    guess = mimetypes.guess_type(file_name)[0]
    default = "application/octet-stream"
    return guess or default


def detect_decode(string: bytes) -> t.Tuple[t.Union[str, bytes], t.Union[str, None]]:
    try:
        return string.decode('utf-8'), 'utf-8'
    except UnicodeDecodeError:
        if encoding := chardet.detect(string, should_rename_legacy=True)["encoding"]:
            return string.decode(encoding), encoding
    return string, None
