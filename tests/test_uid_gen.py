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
import typing as t
from unittest.mock import patch
from fastapi_xroad_soap.internal.uid_gen import UIDGenerator


__all__ = [
	"test_cid_token_generation",
	"test_key_token_generation",
	"test_token_uniqueness",
	"test_cid_length_increase",
	"test_key_length_increase",
	"test_cid_out_of_bounds_collisions",
	"test_key_out_of_bounds_collisions"
]


def test_cid_token_generation():
	cid = UIDGenerator(mode="cid")
	token = cid.generate()
	assert token.startswith("cid:")
	assert len(token) - 4 == 20


def test_key_token_generation():
	key = UIDGenerator(mode="key")
	token = key.generate()
	assert token.count('-') == 3
	parts = token.split('-')
	assert len(parts) == 4
	for part in parts:
		assert len(part) == 4
		assert part.isalnum()


def test_token_uniqueness():
	for mode in ["cid", "key"]:
		gen = UIDGenerator(mode=t.cast(t.Literal, mode))
		tokens = {gen.generate() for _ in range(10)}
		assert len(tokens) == 10


def test_cid_length_increase():
	cid = UIDGenerator(mode="cid")
	for _ in range(6):
		tkn_len = cid._token_len + 4
		assert len(cid.generate()) == tkn_len
		cid._token_len += 2
	cid._token_len += 2
	with pytest.raises(RuntimeError):
		_ = cid.generate()


def test_key_length_increase():
	key = UIDGenerator(mode="key")
	for i in range(2, 3):
		tkn_len = key._token_len - 1 + (i * 5)
		assert len(key.generate()) == tkn_len
		key._token_len += 5
	key._token_len += 5
	with pytest.raises(RuntimeError):
		_ = key.generate()


def test_cid_out_of_bounds_collisions():
	cid = UIDGenerator(mode="cid")
	target = 'fastapi_xroad_soap.internal.uid_gen.secrets.token_hex'
	predef_token = f"cid:{'x' * 20}"

	with patch(target=target, return_value=predef_token):
		_ = cid.generate()
		with pytest.raises(RuntimeError):
			_ = cid.generate()
	assert cid._token_len > 30


def test_key_out_of_bounds_collisions():
	key = UIDGenerator(mode="key")
	target = 'fastapi_xroad_soap.internal.uid_gen.secrets.token_bytes'
	predef_token = b'\x8eK\x1fO\xc2\xa0\xd3\xecP\xd2'

	with patch(target=target, return_value=predef_token):
		_ = key.generate()
		with pytest.raises(RuntimeError):
			_ = key.generate()
	assert key._token_len > 15
