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
import typing
import pytest
from fastapi_xroad_soap.utils import FileSize
from fastapi_xroad_soap.internal.file_size import (
	FileSizeKB, FileSizeMB, FileSizeGB
)


def test_attributes():
	assert hasattr(FileSize, "KB")
	assert hasattr(FileSize, "MB")
	assert hasattr(FileSize, "GB")

	assert getattr(FileSize, "KB") == FileSizeKB
	assert getattr(FileSize, "MB") == FileSizeMB
	assert getattr(FileSize, "GB") == FileSizeGB

	assert hasattr(FileSize, "bytes_to_iec_str")
	assert hasattr(FileSize, "value")


def test_inheritance():
	assert issubclass(FileSizeKB, FileSize)
	assert issubclass(FileSizeMB, FileSize)
	assert issubclass(FileSizeGB, FileSize)


def test_multipliers():
	assert FileSizeKB._multiplier() == 1_024
	assert FileSizeMB._multiplier() == 1_048_576
	assert FileSizeGB._multiplier() == 1_073_741_824


def test_size_and_value():
	assert FileSizeKB(2).value == 2_048
	assert FileSizeMB(2).value == 2_097_152
	assert FileSizeGB(2).value == 2_147_483_648

	for cls in [FileSizeKB, FileSizeMB, FileSizeGB]:
		assert cls(123).size == 123


def test_invalid_size():
	for cls in [FileSizeKB, FileSizeMB, FileSizeGB]:
		with pytest.raises(ValueError):
			cls(-1)
		with pytest.raises(TypeError):
			cls(typing.cast(int, 1.0))


def test_class_str_method():
	assert str(FileSizeKB(1)) == "1KB"
	assert str(FileSizeKB(999)) == "999KB"

	assert str(FileSizeMB(1)) == "1MB"
	assert str(FileSizeMB(999)) == "999MB"

	assert str(FileSizeGB(1)) == "1GB"
	assert str(FileSizeGB(999)) == "999GB"


def test_bytes_to_iec_str():
	assert FileSize.bytes_to_iec_str(1023) == "1023B"
	assert FileSize.bytes_to_iec_str(1024) == "1KB"

	assert FileSize.bytes_to_iec_str(1048575) == "1023KB"
	assert FileSize.bytes_to_iec_str(1048576) == "1MB"

	assert FileSize.bytes_to_iec_str(1073741823) == "1023MB"
	assert FileSize.bytes_to_iec_str(1073741824) == "1GB"
