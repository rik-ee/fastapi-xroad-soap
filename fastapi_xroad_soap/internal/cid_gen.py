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
import secrets


__all__ = ["CIDGenerator"]


class CIDGenerator:
	def __init__(self, max_len: int = 30):
		self.items = list()
		self._max_len = max_len
		self._token_len = 20

	@property
	def token(self) -> str:
		exists_counter = 0

		while True:
			if self._token_len > self._max_len:
				raise RuntimeError("CIDGenerator out of bounds")

			size = self._token_len // 2
			token = secrets.token_hex(size)
			cid = f"cid:{token}"

			if cid not in self.items:
				self.items.append(cid)
				return cid
			elif exists_counter < 10:
				exists_counter += 1
			else:
				self._token_len += 2
				exists_counter = 0
