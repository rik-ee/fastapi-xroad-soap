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
import typing as t
from pathlib import Path


__all__ = [
	"setup_search_upwards",
	"create_temp_file"
]


@pytest.fixture
def setup_search_upwards(tmp_path):
	def create_nested_files(root_path, nested_path, file_name):
		full_path = Path(root_path, nested_path)
		full_path.mkdir(parents=True, exist_ok=True)
		file_path = full_path / file_name
		file_path.touch()
		return file_path

	target_file_path = create_nested_files(
		root_path=tmp_path,
		nested_path="nested/dir/structure",
		file_name="target_file.txt"
	)
	unrelated_file_path = create_nested_files(
		root_path=tmp_path,
		nested_path="another/nested/dir",
		file_name="unrelated_file.txt"
	)
	yield tmp_path, target_file_path, unrelated_file_path


@pytest.fixture
def create_temp_file(tmp_path: Path):
	def closure(content: t.Union[str, bytes], file_name: str = "test.txt", binary: bool = False):
		file_path = tmp_path / file_name
		file_path.touch()

		if binary and isinstance(content, str):
			content = content.encode('utf-8')
		elif not binary and isinstance(content, bytes):
			content = content.decode('utf-8')

		mode = "wb" if binary else "w"
		encoding = "utf-8" if not binary else None

		with file_path.open(mode=mode, encoding=encoding) as fp:
			fp.write(content)

		return file_path
	return closure
