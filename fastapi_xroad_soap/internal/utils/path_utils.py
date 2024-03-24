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
import platform
import functools
import typing as t
from lxml import etree
from pathlib import (
	PureWindowsPath,
	PurePosixPath,
	Path
)


__all__ = [
	"search_upwards",
	"resolve_relpath",
	"read_cached_file",
	"read_cached_xml_file"
]


@functools.lru_cache(maxsize=None)
def search_upwards(
		for_path: t.Union[Path, str],
		from_path: t.Union[Path, str] = __file__
) -> Path:
	current = Path(from_path).resolve()
	while current != current.parent:
		new_path = current / for_path
		if new_path.exists():
			return new_path
		current = current.parent
	raise FileNotFoundError(for_path)


@functools.lru_cache(maxsize=None)
def resolve_relpath(path: t.Union[str, Path] = '.') -> Path:
	path_cls = PurePosixPath
	if platform.system().lower() == "windows":  # pragma: no cover
		path_cls = PureWindowsPath

	pure_path = path_cls(path)
	if pure_path.is_absolute():
		return Path(pure_path)
	return (Path.cwd() / path).resolve()


@functools.lru_cache(maxsize=None)
def read_cached_file(
		path: t.Union[str, Path],
		binary: bool = False,
		as_lines: bool = False,
		encoding: str = "UTF-8"
) -> t.Union[str, bytes, t.List[str], t.List[bytes]]:
	path = resolve_relpath(path)
	mode = 'rb' if binary else 'r'
	with path.open(mode, encoding=encoding) as file:
		func = file.readlines if as_lines else file.read
		return func()


@functools.lru_cache(maxsize=None)
def read_cached_xml_file(
		path: t.Union[str, Path],
		return_as_etree: bool = False
) -> t.Union[str, etree.Element]:
	"""
	Reads and parses the contents of an XML file.
	:param path: Either an absolute or a relative path to the XML file.
		If the path is relative, it is evaluated from the current working directory of the active shell.
	:param return_as_etree: If the file content should be returned as an instance of etree.Element.
		By default, the XML content is returned as a string.
	:raises etree.LxmlError: If lxml library fails to validate the content of the XML file.
		This error type is the superclass of lxml library errors.
	:return: The XML file content as a string or an etree.Element.
	"""
	path = resolve_relpath(path)
	with path.open('rb') as file:
		contents = file.read()
		obj = etree.fromstring(contents)  # Validates XML structure
		if return_as_etree:
			return obj
		return contents.decode('utf-8')
