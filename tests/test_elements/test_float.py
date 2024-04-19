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
from fastapi_xroad_soap.internal.elements.models import Float, FloatSpec


__all__ = [
	"test_float_spec",
	"test_float_spec_data_init",
	"test_float_spec_enum_restriction",
	"test_float_spec_pattern_restriction",
	"test_float_spec_min_max_restriction"
]


def test_float_spec(spec_tester):
	spec_tester(
		spec_creator=Float,
		spec_type=FloatSpec,
		spec_base_type=NumericTypeSpec,
		element_type=float,
		wsdl_type_name="float",
		default_wsdl_type_name="float"
	)


def test_float_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=Float,
		good_values=[1.1, 2.2, 3.3],
		bad_values=[None, "asdfg", 12345, {}, []]
	)


def test_float_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=Float,
		enum_values=(1.111, 2.222, 3.333),
		non_enum_value=4.444,
		bad_type_values=["asdfg", 123, True, None]
	)


def test_float_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=Float,
		good_values=[1.234, 12.34, 123.4],
		bad_values=[5.0, 6.0, 7.0, 8.0, 9.0],
		pattern=r'^[0-4\.]+$'
	)


def test_float_spec_min_max_restriction(min_max_value_tester):
	min_max_value_tester(
		spec_creator=Float,
		min_value=1.234,
		max_value=6.789,
		less_value=1.233,
		more_value=6.790
	)
