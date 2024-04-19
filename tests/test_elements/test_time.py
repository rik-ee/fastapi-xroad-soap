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
from datetime import time
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Time, TimeSpec


__all__ = [
	"test_time_spec",
	"test_time_spec_data_init",
	"test_time_spec_enum_restriction",
	"test_time_spec_pattern_restriction",
	"test_time_spec_min_max_restriction"
]


def test_time_spec(spec_tester):
	spec_tester(
		spec_creator=Time,
		spec_type=TimeSpec,
		spec_base_type=NumericTypeSpec,
		element_type=time,
		wsdl_type_name="time",
		default_wsdl_type_name="time"
	)


def test_time_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=Time,
		good_values=[time(hour=11, minute=34, second=56)],
		bad_values=[None, True, "asdfg", 12345, 1.2345, {}, []]
	)


def test_time_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=Time,
		enum_values=(
			time(hour=10, minute=10, second=10),
			time(hour=11, minute=11, second=11),
			time(hour=12, minute=12, second=12)
		),
		non_enum_value=time(hour=9, minute=9, second=9),
		bad_type_values=["asdfg", 123, 1.23, True, None]
	)


def test_time_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=Time,
		good_values=[time(hour=11, minute=34, second=56)],
		bad_values=[time(hour=10, minute=34, second=56)],
		pattern=r'^11:[0-5][0-9]:[0-5][0-9]$'
	)


def test_time_spec_min_max_restriction(min_max_value_tester):
	min_max_value_tester(
		spec_creator=Time,
		min_value=time(hour=11, minute=34, second=56),
		max_value=time(hour=12, minute=34, second=56),
		less_value=time(hour=11, minute=34, second=55),
		more_value=time(hour=12, minute=34, second=57)
	)
