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
import charset_normalizer as charset


__all__ = [
	"split_on_find",
	"guess_mime_type",
	"detect_decode"
]


_USB = t.Union[str, bytes]
_USN = t.Union[str, None]


def split_on_find(content: _USB, separator: _USB) -> t.Tuple[_USB, _USB]:
	point, sep_len = content.find(separator), len(separator)
	first, second = content[:point], content[point + sep_len:]
	return first.strip(), second.strip()


def guess_mime_type(file_name: t.Union[str, None]) -> str:
	guess = mimetypes.guess_type(file_name)[0]
	default = "application/octet-stream"
	return guess or default


def detect_decode(string: bytes, encoding: str = 'utf-8') -> t.Tuple[_USB, _USN]:
	try:
		return string.decode(encoding), encoding
	except UnicodeDecodeError:
		if charset.is_binary(string):
			return string, None
		kwargs = dict(should_rename_legacy=True)
		match = chardet.detect(string, **kwargs)
		if match and match["confidence"] >= 0.7:
			enc = match["encoding"]
			return string.decode(enc), enc
	return string, None
