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
from fastapi_xroad_soap.internal.file_size import (
	FileSize, FileSizeKB, FileSizeMB, FileSizeGB
)


def test_attributes():
	assert hasattr(FileSize, "KB")
	assert hasattr(FileSize, "MB")
	assert hasattr(FileSize, "GB")

	assert getattr(FileSize, "KB") == FileSizeKB
	assert getattr(FileSize, "MB") == FileSizeMB
	assert getattr(FileSize, "GB") == FileSizeGB


def test_inheritance():
	assert issubclass(FileSizeKB, FileSize)
	assert issubclass(FileSizeMB, FileSize)
	assert issubclass(FileSizeGB, FileSize)


def test_multipliers():
	assert FileSizeKB._multiplier() == 1_024
	assert FileSizeMB._multiplier() == 1_048_576
	assert FileSizeGB._multiplier() == 1_073_741_824


def test_values():
	assert FileSizeKB(2) == 2_048
	assert FileSizeMB(2) == 2_097_152
	assert FileSizeGB(2) == 2_147_483_648


def test_invalid_size():
	with pytest.raises(ValueError):
		FileSizeKB(-1)

	with pytest.raises(ValueError):
		FileSizeMB(-1)

	with pytest.raises(ValueError):
		FileSizeGB(-1)


def test_comparison():
	for cls in [FileSizeKB, FileSizeMB, FileSizeGB]:
		assert cls(15) == cls(15)
		assert cls(15) != cls(20)
		assert cls(15) <= cls(16)
		assert cls(15) <= cls(15)
		assert cls(15) >= cls(15)
		assert cls(15) >= cls(14)
		assert cls(15) < cls(16)
		assert cls(15) > cls(14)
