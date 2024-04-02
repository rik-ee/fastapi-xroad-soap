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
import io
import os
import chardet
import mimetypes
import contextlib
import typing as t
import charset_normalizer as charset


__all__ = [
	"split_on_find",
	"encode_with",
	"reset",
	"total_len",
	"guess_mime_type",
	"detect_decode"
]


_USBType = t.Union[str, bytes]


def split_on_find(content: _USBType, separator: _USBType) -> t.Tuple[_USBType, _USBType]:
	point, sep_len = content.find(separator), len(separator)
	first, second = content[:point], content[point + sep_len:]
	return first.strip(), second.strip()


def encode_with(string: t.Union[str, bytes, t.Any], encoding: str = 'utf-8') -> t.Union[bytes, t.Any]:
	if not (string is None or isinstance(string, bytes)):
		return string.encode(encoding)
	return string


@contextlib.contextmanager
def reset(buffer) -> None:
	original_position = buffer.tell()
	buffer.seek(0, 2)
	yield
	buffer.seek(original_position, 0)


def total_len(o: t.Any) -> int:
	if hasattr(o, '__len__'):
		return len(o)
	if hasattr(o, 'len'):
		return o.len
	if hasattr(o, 'fileno'):
		try:
			file_no = o.fileno()
		except io.UnsupportedOperation:
			pass
		else:
			return os.fstat(file_no).st_size
	if hasattr(o, 'getvalue'):
		return len(o.getvalue())


def guess_mime_type(file_name: t.Union[str, None]) -> str:
	guess = mimetypes.guess_type(file_name)[0]
	default = "application/octet-stream"
	return guess or default


def detect_decode(
		string: bytes,
		encoding: str = 'utf-8'
) -> t.Tuple[t.Union[str, bytes], t.Union[str, None]]:
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
