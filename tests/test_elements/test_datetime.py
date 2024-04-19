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
from datetime import datetime, timedelta
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import DateTime, DateTimeSpec


__all__ = [
	"test_datetime_spec",
	"test_datetime_spec_data_init",
	"test_datetime_spec_enum_restriction",
	"test_datetime_spec_pattern_restriction",
	"test_datetime_spec_min_max_restriction"
]


def test_datetime_spec(spec_tester):
	spec_tester(
		spec_creator=DateTime,
		spec_type=DateTimeSpec,
		spec_base_type=NumericTypeSpec,
		element_type=datetime,
		wsdl_type_name="dateTime",
		default_wsdl_type_name="dateTime"
	)


def test_datetime_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=DateTime,
		good_values=[datetime(year=2024, month=2, day=13, hour=11, minute=34, second=56)],
		bad_values=[None, "asdfg", 12345, 1.2345, {}, []]
	)


def test_datetime_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=DateTime,
		enum_values=(
			datetime(year=2024, month=2, day=13, hour=11, minute=34, second=56),
			datetime(year=2025, month=3, day=14, hour=12, minute=35, second=57),
			datetime(year=2026, month=4, day=15, hour=13, minute=36, second=58)
		),
		non_enum_value=datetime(year=2023, month=1, day=12, hour=10, minute=33, second=55),
		bad_type_values=["asdfg", 123, 1.23, True, None]
	)


def test_datetime_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=DateTime,
		good_values=[datetime(year=2024, month=2, day=13, hour=11, minute=34, second=56)],
		bad_values=[datetime(year=2023, month=2, day=13, hour=11, minute=34, second=56)],
		pattern=r'^2024-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T11:[0-5][0-9]:[0-5][0-9]'
	)


def test_datetime_spec_min_max_restriction(min_max_value_tester):
	min_value = datetime(year=2024, month=2, day=13, hour=11, minute=34, second=56)
	max_value = datetime(year=2025, month=3, day=14, hour=12, minute=35, second=57)
	less_value = min_value - timedelta(seconds=1)
	more_value = max_value + timedelta(seconds=1)
	min_max_value_tester(
		spec_creator=DateTime,
		min_value=min_value,
		max_value=max_value,
		less_value=less_value,
		more_value=more_value
	)
