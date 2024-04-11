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
import tempfile
from pathlib import Path


__all__ = [
	"setup_search_upwards",
	"create_temp_file",
	"create_temp_xml_file"
]


@pytest.fixture
def setup_search_upwards():
	def create_nested_files(root_path, nested_path, file_name):
		full_path = Path(root_path, nested_path)
		full_path.mkdir(parents=True, exist_ok=True)
		file_path = full_path / file_name
		file_path.touch()
		return file_path

	with tempfile.TemporaryDirectory() as temp_dir:
		root_dir = Path(temp_dir)
		target_file_path = create_nested_files(
			root_path=root_dir,
			nested_path="nested/dir/structure",
			file_name="target_file.txt"
		)
		unrelated_file_path = create_nested_files(
			root_dir,
			nested_path="another/nested/dir",
			file_name="unrelated_file.txt"
		)
		yield root_dir, target_file_path, unrelated_file_path


def create_temp_file(content, binary=False):
	mode = "wb" if binary else "w"
	encoding = "utf-8" if not binary else None

	temp_file = tempfile.NamedTemporaryFile(
		encoding=encoding,
		delete=False,
		mode=mode
	)
	if binary and isinstance(content, str):
		content = content.encode('utf-8')
	elif not binary and isinstance(content, bytes):
		content = content.decode('utf-8')

	temp_file.write(content)
	temp_file.close()

	return Path(temp_file.name)


def create_temp_xml_file(content):
	temp_file = tempfile.NamedTemporaryFile(
		encoding='utf-8',
		suffix=".xml",
		delete=False,
		mode='w'
	)
	temp_file.write(content)
	temp_file.close()
	return Path(temp_file.name)
