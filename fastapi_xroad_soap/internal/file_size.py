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
from abc import ABC, abstractmethod


__all__ = [
	"FileSize",
	"FileSizeKB",
	"FileSizeMB",
	"FileSizeGB"
]


class FileSize(ABC):
	def __init__(self, size: int = 1) -> None:
		if size < 0:
			raise ValueError("File size cannot be a negative number")
		elif not isinstance(size, int):
			raise TypeError("File size must be an integer")
		self.size = size

	@property
	@abstractmethod
	def _multiplier(self) -> int: ...

	@property
	def value(self) -> int:
		return self.size * self._multiplier

	def __int__(self) -> int:
		return self.value


class FileSizeKB(FileSize):
	@property
	def _multiplier(self) -> int:
		return 1024


class FileSizeMB(FileSize):
	@property
	def _multiplier(self) -> int:
		return 1024 ** 2


class FileSizeGB(FileSize):
	@property
	def _multiplier(self) -> int:
		return 1024 ** 3


FileSize.KB = FileSizeKB
FileSize.MB = FileSizeMB
FileSize.GB = FileSizeGB
