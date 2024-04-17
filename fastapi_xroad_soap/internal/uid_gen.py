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
		self._max_len = 15
		self._token_len = 10
		self._increment = 1 if mode == "cid" else 5
		self._compute_token = (
			self._compute_cid_token
			if mode == "cid" else
			self._compute_key_token
		)

	def generate(self, from_bytes: bytes = None) -> str:
		exists_counter = 0
		while True:
			if self._token_len > self._max_len:
				raise RuntimeError("UIDGenerator out of bounds")

			token_bytes = from_bytes
			if not isinstance(from_bytes, bytes):
				token_bytes = secrets.token_bytes(self._token_len)
			token = self._compute_token(token_bytes)

			if isinstance(from_bytes, bytes):
				return token
			elif token not in self.tokens:
				self.tokens.append(token)
				return token
			elif exists_counter < 10:
				exists_counter += 1
			else:
				self._token_len += self._increment
				exists_counter = 0

	@staticmethod
	def _compute_cid_token(from_bytes: bytes = None) -> str:
		return f"cid:{from_bytes.hex()}"

	@staticmethod
	def _compute_key_token(from_bytes: bytes = None) -> str:
		token = base64.b64encode(from_bytes).decode()
		table = str.maketrans("+/=", "ABC")
		return token.translate(table)
