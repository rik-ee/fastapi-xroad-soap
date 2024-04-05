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
from __future__ import annotations
import typing as t
from abc import ABC, abstractmethod


__all__ = [
	"FileSize",
	"FileSizeKB",
	"FileSizeMB",
	"FileSizeGB"
]


class FileSize(ABC):
	KB: t.Type[FileSizeKB]
	MB: t.Type[FileSizeMB]
	GB: t.Type[FileSizeGB]

	def __new__(cls, size: int = 1) -> int:
		if size < 0:
			raise ValueError("File size cannot be a negative number")
		elif not isinstance(size, int):
			raise TypeError("File size must be an integer")
		return cls._multiplier() * size

	@classmethod
	@abstractmethod
	def _multiplier(cls) -> int: ...


class FileSizeKB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024


class FileSizeMB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024 ** 2


class FileSizeGB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024 ** 3


FileSize.KB = FileSizeKB
FileSize.MB = FileSizeMB
FileSize.GB = FileSizeGB
