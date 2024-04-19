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
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Integer, IntegerSpec


__all__ = [
	"test_integer_spec",
	"test_integer_spec_data_init",
	"test_integer_spec_enum_restriction",
	"test_integer_spec_pattern_restriction",
	"test_integer_spec_min_max_restriction",
	"test_integer_spec_total_digits_restriction"
]


def test_integer_spec(spec_tester):
	spec_tester(
		spec_creator=Integer,
		spec_type=IntegerSpec,
		spec_base_type=NumericTypeSpec,
		element_type=int,
		wsdl_type_name="integer",
		default_wsdl_type_name="integer"
	)


def test_integer_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=Integer,
		good_values=[1, 2, 3],
		bad_values=[None, "asdfg", 1.2345, {}, []]
	)


def test_integer_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=Integer,
		enum_values=(1111, 2222, 3333),
		non_enum_value=4444,
		bad_type_values=["asdfg", 1.23, None]
	)


def test_integer_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=Integer,
		good_values=[1234, 1120, 2230, 4440],
		bad_values=[50, 60, 70, 80, 90],
		pattern=r'^[0-4]+$'
	)


def test_integer_spec_min_max_restriction(min_max_value_tester):
	min_max_value_tester(
		spec_creator=Integer,
		min_value=1234,
		max_value=6789,
		less_value=1233,
		more_value=6790
	)


def test_integer_spec_total_digits_restriction(total_digits_tester):
	total_digits_tester(
		spec_creator=Integer,
		good_values=[1, 23, 456, 7890],
		bad_values=[12_345, 67_890],
		total_digits=4
	)
