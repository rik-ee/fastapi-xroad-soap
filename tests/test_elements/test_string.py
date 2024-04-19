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
import string
from fastapi_xroad_soap.internal.elements import StringTypeSpec
from fastapi_xroad_soap.internal.elements.models import String, StringSpec


__all__ = [
	"test_string_spec",
	"test_string_spec_data_init",
	"test_string_spec_enum_restriction",
	"test_string_spec_pattern_restriction",
	"test_string_spec_min_max_restriction",
	"test_string_spec_length_restriction",
	"test_string_process_whitespace"
]


def test_string_spec(spec_tester):
	spec_tester(
		spec_creator=String,
		spec_type=StringSpec,
		spec_base_type=StringTypeSpec,
		element_type=str,
		wsdl_type_name="string",
		default_wsdl_type_name="string"
	)


def test_string_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=String,
		good_values=["abc", "def", "ghi"],
		bad_values=[None, True, 12345, 1.2345, {}, []]
	)


def test_string_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=String,
		enum_values=("abc", "def", "ghi"),
		non_enum_value="qwe",
		bad_type_values=[123, 1.23, True, None]
	)


def test_string_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=String,
		good_values=["abc", "def", "ghi"],
		bad_values=[f"qwe{c}" for c in string.ascii_uppercase],
		pattern=r'^[a-z]+$'
	)


def test_string_spec_min_max_restriction(min_max_length_tester):
	min_max_length_tester(
		spec_creator=String,
		good_values=['x' * i for i in range(5, 11)],
		bad_values=['x' * 4, 'x' * 11],
		min_length=5,
		max_length=10
	)


def test_string_spec_length_restriction(length_tester):
	length_tester(
		spec_creator=String,
		good_values=["qwerty"],
		bad_values=["qwert", "qwertyu"],
		length=6
	)


def test_string_process_whitespace(whitespace_tester):
	whitespace_tester(
		spec_creator=String,
		raw_string="asdfg  \t  qwerty",
		replace_string="asdfg     qwerty",
		collapse_string="asdfg qwerty"
	)
