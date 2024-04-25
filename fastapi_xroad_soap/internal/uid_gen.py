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
		"""
		Initialize a UIDGenerator instance with a specific operational mode.
		This class generates unique identifiers (UIDs) based on the selected mode,
		either 'cid' or 'key'. The 'cid' mode generates content identifiers with
		a hexadecimal format, while the 'key' mode produces more complex keys
		encoded in a modified base64 format.

		:param mode: Determines the type of UID to generate. "cid" mode generates
			UIDs prefixed with 'cid:' and uses a shorter token length. "key" mode
			generates UIDs modified from base64 encoding, with specific character
			replacements and a longer token length.
		"""
		self.tokens = list()
		self._mode = mode
		self._max_len = 14 if mode == "cid" else 18
		self._token_len = 10 if mode == "cid" else 12
		self._increment = 1 if mode == "cid" else 3
		self._compute_token = (
			self._compute_cid_token
			if mode == "cid" else
			self._compute_key_token
		)

	def generate(self, from_bytes: t.Optional[bytes] = None) -> str:
		"""
		Generate a unique identifier (UID) based on the previously set mode.
		This method can either generate a new UID using random bytes or transform
		provided bytes into a UID format depending on the mode.

		If 'from_bytes' is provided, the UID is directly computed from these
		bytes without generating new random bytes. If not provided, random bytes
		of a specific length are used.

		The method ensures that all generated UIDs are unique by maintaining
		a history of previously generated UIDs. If a UID collision occurs, it
		attempts to resolve this by increasing the token length and retrying
		a limited number of times.

		:param from_bytes: Optional bytes to use for generating the UID.
			If not provided, random bytes are generated.
		:return: The generated unique identifier as a string.
		:raises RuntimeError: Raised if the UID generation exceeds
			the internally hardcoded maximum token length limit.
		"""
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
