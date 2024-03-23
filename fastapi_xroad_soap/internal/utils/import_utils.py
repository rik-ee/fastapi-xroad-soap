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
import typing as t
from importlib import import_module


__all__ = ["LazyImport"]


class LazyImport:
	def __init__(self, module_name: str):
		self.module_name = module_name
		self.module = None

	def __getattr__(self, name: str) -> t.Any:
		if self.module is None:
			self.module = import_module(self.module_name)
		return getattr(self.module, name)
