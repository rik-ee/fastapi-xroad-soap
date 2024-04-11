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
from unittest.mock import patch
from fastapi_xroad_soap.internal.cid_gen import CIDGenerator


__all__ = [
	"test_token_generation",
	"test_token_uniqueness",
	"test_max_length_exceeded",
	"test_length_increase",
	"test_out_of_bounds_collisions"
]


def test_token_generation():
	gen = CIDGenerator()
	cid = gen.token
	assert cid.startswith("cid:") and len(cid) - 4 == 20


def test_token_uniqueness():
	gen = CIDGenerator()
	tokens = {gen.token for _ in range(10)}
	assert len(tokens) == 10


def test_max_length_exceeded():
	gen = CIDGenerator(max_len=5)
	with pytest.raises(RuntimeError):
		_ = gen.token


def test_length_increase():
	gen = CIDGenerator()
	for _ in range(6):
		cid_len = gen._token_len + 4
		assert len(gen.token) == cid_len
		gen._token_len += 2
	gen._token_len += 2
	with pytest.raises(RuntimeError):
		_ = gen.token


def test_out_of_bounds_collisions():
	gen = CIDGenerator()
	target = 'fastapi_xroad_soap.internal.cid_gen.secrets.token_hex'
	predef_token = f"cid:{'x' * 20}"

	with patch(target=target, return_value=predef_token):
		_ = gen.token
		with pytest.raises(RuntimeError):
			_ = gen.token
	assert gen._token_len > 30
