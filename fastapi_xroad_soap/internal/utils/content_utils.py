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
from ..base import MessageBody, BaseElementSpec


__all__ = [
	"split_on_find",
	"guess_mime_type",
	"detect_decode",
	"object_has_spec"
]


_USB = t.Union[str, bytes]
_USN = t.Union[str, None]


def split_on_find(content: _USB, separator: _USB) -> t.Tuple[_USB, _USB]:
	point, sep_len = content.find(separator), len(separator)
	end = point if point != -1 else len(content) + 1
	start = end + sep_len if point != -1 else 0
	first, second = content[:end], content[start:]
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
		if match and match["confidence"] >= 0.7:  # pragma: no cover
			enc = match["encoding"]
			return string.decode(enc), enc
		return string, None  # pragma: no cover


def object_has_spec(obj: MessageBody, spec_cls: t.Type[BaseElementSpec]):
	if not isinstance(obj, MessageBody):
		return False
	elif specs := getattr(obj, "_element_specs", None):
		for spec in specs.values():
			if isinstance(spec, spec_cls):
				return True
	for value in vars(obj).values():
		if isinstance(value, MessageBody):
			ret = object_has_spec(value, spec_cls)
			if ret is False:
				continue
			return True
	return False
