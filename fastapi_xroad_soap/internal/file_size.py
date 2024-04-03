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
import operator
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

	@property
	@abstractmethod
	def _multiplier(self) -> int: ...

	@property
	def value(self) -> int:
		return self.size * self._multiplier

	def __int__(self) -> int:
		return self.value

	def _compare(self, other: t.Any, op: t.Callable[..., t.Any]) -> bool:
		if isinstance(other, self.__class__):
			return op(self.value, other.value)
		elif isinstance(other, (int, float)):
			return op(self.value, other)
		return False

	def __eq__(self, other):
		return self._compare(other, operator.eq)

	def __ne__(self, other):
		return self._compare(other, operator.ne)

	def __lt__(self, other):
		return self._compare(other, operator.lt)

	def __le__(self, other):
		return self._compare(other, operator.le)

	def __gt__(self, other):
		return self._compare(other, operator.gt)

	def __ge__(self, other):
		return self._compare(other, operator.ge)


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
