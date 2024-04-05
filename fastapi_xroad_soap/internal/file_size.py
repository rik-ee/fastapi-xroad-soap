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

	def __init__(self, size: int = 1) -> None:
		if size < 0:
			raise ValueError("File size cannot be a negative number")
		elif not isinstance(size, int):
			raise TypeError("File size must be an integer")
		self.size = size

	@staticmethod
	def bytes_to_iec_str(byte_count: int) -> str:
		kib, mib, gib = 1024, 1024 ** 2, 1024 ** 3
		if byte_count >= gib:
			return f"{int(byte_count // gib)}GB"
		elif byte_count >= mib:
			return f"{int(byte_count // mib)}MB"
		elif byte_count >= kib:
			return f"{int(byte_count // kib)}KB"
		return f"{byte_count}B"

	@classmethod
	@abstractmethod
	def _multiplier(cls) -> int: ...

	@abstractmethod
	def __str__(self) -> str: ...

	def __int__(self) -> int:
		return self.size * self._multiplier()

	@property
	def value(self) -> int:
		return self.__int__()


class FileSizeKB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024

	def __str__(self) -> str:
		return f"{self.size}KB"


class FileSizeMB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024 ** 2

	def __str__(self) -> str:
		return f"{self.size}MB"


class FileSizeGB(FileSize):
	@classmethod
	def _multiplier(cls) -> int:
		return 1024 ** 3

	def __str__(self) -> str:
		return f"{self.size}GB"


FileSize.KB = FileSizeKB
FileSize.MB = FileSizeMB
FileSize.GB = FileSizeGB
