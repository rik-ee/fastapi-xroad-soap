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
import base64
import secrets
import typing as t


__all__ = ["UIDGenerator"]


class UIDGenerator:
	def __init__(self, mode: t.Literal["cid", "key"]):
		self.tokens = list()
		self._mode = mode
		if mode == "cid":
			self._max_len = 30
			self._token_len = 20
			self._increment = 2
			self._compute_token = self._compute_cid_token
		else:
			self._max_len = 15
			self._token_len = 10
			self._increment = 5
			self._compute_token = self._compute_key_token

	def generate(self) -> str:
		exists_counter = 0
		while True:
			if self._token_len > self._max_len:
				raise RuntimeError("UIDGenerator out of bounds")
			token = self._compute_token()
			if token not in self.tokens:
				self.tokens.append(token)
				return token
			elif exists_counter < 10:
				exists_counter += 1
			else:
				self._token_len += self._increment
				exists_counter = 0

	def _compute_cid_token(self) -> str:
		size = self._token_len // 2
		token = secrets.token_hex(size)
		return f"cid:{token}"

	def _compute_key_token(self) -> str:
		tkn_bytes = secrets.token_bytes(self._token_len)
		tkn_b32hex = base64.b32hexencode(tkn_bytes).decode()
		tkn_len = len(tkn_b32hex)
		return '-'.join([
			tkn_b32hex[i:i + 4]
			for i in range(0, tkn_len, 4)
		])
