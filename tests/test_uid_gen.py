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
import hashlib
import typing as t
from unittest.mock import patch
from fastapi_xroad_soap.internal.uid_gen import UIDGenerator


__all__ = [
	"test_cid_token_generation",
	"test_key_token_generation",
	"test_token_uniqueness",
	"test_cid_length_increase",
	"test_key_length_increase",
	"test_out_of_bounds_collisions",
	"test_deterministic_generation"
]


def test_cid_token_generation():
	def validate(_token: str):
		assert _token.startswith("cid:")
		assert len(_token) - 4 == 20
		assert _token.split(':')[-1].isalnum()

	cid = UIDGenerator(mode="cid")
	validate(cid.generate())

	digest = hashlib.shake_128().digest(10)
	validate(cid.generate(digest))


def test_key_token_generation():
	def validate(_token: str):
		assert _token.count('-') == 3
		parts = _token.split('-')
		assert len(parts) == 4
		for part in parts:
			assert len(part) == 4
			assert part.isalnum()

	key = UIDGenerator(mode="key")
	validate(key.generate())

	digest = hashlib.shake_128().digest(10)
	validate(key.generate(digest))


def test_token_uniqueness():
	for mode in ["cid", "key"]:
		gen = UIDGenerator(mode=t.cast(t.Literal, mode))
		tokens = {gen.generate() for _ in range(10)}
		assert len(tokens) == 10


def test_cid_length_increase():
	cid = UIDGenerator(mode="cid")
	for _ in range(5):
		tkn_len = cid._token_len * 2 + 4
		assert len(cid.generate()) == tkn_len
		cid._token_len += 1
	cid._token_len += 1
	with pytest.raises(RuntimeError):
		_ = cid.generate()


def test_key_length_increase():
	key = UIDGenerator(mode="key")
	for _ in range(2):
		tkn_len = key._token_len * 2 - 1
		assert len(key.generate()) == tkn_len
		key._token_len += 5
	key._token_len += 5
	with pytest.raises(RuntimeError):
		_ = key.generate()


def test_out_of_bounds_collisions():
	for mode in ["cid", "key"]:
		gen = UIDGenerator(mode=t.cast(t.Literal, mode))
		target = 'fastapi_xroad_soap.internal.uid_gen.secrets.token_bytes'
		predef_token = b'\x8eK\x1fO\xc2\xa0\xd3\xecP\xd2'

		with patch(target=target, return_value=predef_token):
			_ = gen.generate()
			with pytest.raises(RuntimeError):
				_ = gen.generate()
		assert gen._token_len > 15


def test_deterministic_generation():
	for mode in ["cid", "key"]:
		gen = UIDGenerator(mode=t.cast(t.Literal, mode))
		digest = hashlib.sha512().digest()
		ids = []
		for i in range(10):
			uid = gen.generate(digest)
			ids.append(uid)
			assert ids.count(uid) == i + 1
