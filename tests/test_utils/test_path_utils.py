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
import pytest
import platform
from lxml import etree
from pathlib import Path, PurePosixPath, PureWindowsPath
from fastapi_xroad_soap.internal.utils import path_utils as utils
from .conftest import (
	setup_search_upwards,
	create_temp_file,
	create_temp_xml_file
)


def test_search_upwards_finds_file(setup_search_upwards):
	root_dir, target_file_path, _ = setup_search_upwards
	found_path = utils.search_upwards(
		for_path="target_file.txt",
		from_path=root_dir / "nested/dir/structure"
	)
	assert found_path == target_file_path


def test_search_upwards_raises_file_not_found_error(setup_search_upwards):
	root_dir, _, _ = setup_search_upwards
	with pytest.raises(FileNotFoundError):
		utils.search_upwards(
			for_path="non_existent_file.txt",
			from_path=root_dir
		)


def test_search_upwards_with_str_inputs(setup_search_upwards):
	root_dir, target_file_path, _ = setup_search_upwards
	found_path = utils.search_upwards(
		for_path="target_file.txt",
		from_path=str(root_dir / "nested/dir/structure")
	)
	assert found_path == target_file_path


@pytest.mark.parametrize("input_path, expected_path_cls", [
	("/absolute/path", PurePosixPath if platform.system() != "Windows" else PureWindowsPath),
	("relative/path", Path),
])
def test_resolve_relpath_path_type(input_path, expected_path_cls):
	resolved_path = utils.resolve_relpath(input_path)
	assert isinstance(resolved_path, Path)
	assert isinstance(resolved_path, expected_path_cls)


def test_resolve_relpath_absolute_path():
	absolute_path = Path("/" if platform.system() != "Windows" else "C:\\").as_posix()
	resolved_path = utils.resolve_relpath(absolute_path)
	assert resolved_path == Path(absolute_path).resolve()


def test_resolve_relpath_relative_path(tmpdir):
	with tmpdir.as_cwd():
		relative_path = "some/relative/path"
		resolved_path = utils.resolve_relpath(relative_path)
		expected_path = Path(tmpdir / relative_path).resolve()
		assert resolved_path == expected_path


@pytest.mark.parametrize("content, binary, as_lines, expected_result", [
	("Hello, World!", False, False, "Hello, World!"),
	("Hello, World!", True, False, b"Hello, World!"),
	("Line 1\nLine 2\nLine 3", False, True, ["Line 1\n", "Line 2\n", "Line 3"]),
	(b"Line 1\nLine 2\nLine 3", True, True, [b"Line 1\n", b"Line 2\n", b"Line 3"]),
])
def test_read_cached_file(content, binary, as_lines, expected_result):
	temp_file_path = create_temp_file(content, binary=binary)
	result = utils.read_cached_file(temp_file_path, binary=binary, as_lines=as_lines)
	assert result == expected_result, "The function did not return the expected result."


def test_read_cached_file_encoding():
	content = "Café"
	temp_file_path = create_temp_file(content)
	result = utils.read_cached_file(temp_file_path, encoding="UTF-8")
	assert result == content


@pytest.mark.parametrize("invalid_path", [
	"nonexistent_file.txt",
	"/path/to/nonexistent/file",
])
def test_read_cached_file_nonexistent_file(invalid_path):
	with pytest.raises(FileNotFoundError):
		utils.read_cached_file(invalid_path)


def test_read_cached_file_cached_result():
	content = "This is some text."
	temp_file_path = create_temp_file(content)
	_ = utils.read_cached_file(temp_file_path)
	with temp_file_path.open('w', encoding="UTF-8") as f:
		f.write("Modified content")
	result = utils.read_cached_file(temp_file_path)
	assert result == content


@pytest.mark.parametrize("content,return_as_etree,expected_type", [
	("<root><child>Text</child></root>", False, str),
	("<root><child>Text</child></root>", True, getattr(etree, "_Element")),
])
def test_read_cached_xml_file(content, return_as_etree, expected_type):
	temp_xml_path = create_temp_xml_file(content)
	result = utils.read_cached_xml_file(temp_xml_path, return_as_etree=return_as_etree)
	assert isinstance(result, expected_type), f"Expected result type {expected_type}, got {type(result)}"


def test_read_cached_xml_file_invalid_xml():
	temp_xml_path = create_temp_xml_file("<root><child></root>")
	with pytest.raises(etree.LxmlError):
		utils.read_cached_xml_file(temp_xml_path, return_as_etree=True)


def test_read_cached_xml_file_return_content():
	xml_content = "<root><child>Some text</child></root>"
	temp_xml_path = create_temp_xml_file(xml_content)
	result = utils.read_cached_xml_file(temp_xml_path)
	assert result == xml_content


def test_read_cached_xml_file_return_etree():
	xml_content = "<root><child>Some text</child></root>"
	temp_xml_path = create_temp_xml_file(xml_content)
	result = utils.read_cached_xml_file(temp_xml_path, return_as_etree=True)
	assert isinstance(result, getattr(etree, "_Element"))
	assert result.tag == "root"
	assert getattr(result[0], "tag") == "child"
	assert getattr(result[0], "text") == "Some text"
