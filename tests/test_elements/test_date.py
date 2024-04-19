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
from datetime import date
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Date, DateSpec


__all__ = [
	"test_date_spec",
	"test_date_spec_data_init",
	"test_date_spec_enum_restriction",
	"test_date_spec_pattern_restriction",
	"test_date_spec_min_max_restriction"
]


def test_date_spec(spec_tester):
	spec_tester(
		spec_creator=Date,
		spec_type=DateSpec,
		spec_base_type=NumericTypeSpec,
		element_type=date,
		wsdl_type_name="date",
		default_wsdl_type_name="date"
	)


def test_date_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=Date,
		good_values=[date(year=2024, month=2, day=13)],
		bad_values=[None, "asdfg", 12345, 1.2345, {}, []]
	)


def test_date_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=Date,
		enum_values=(
			date(year=2024, month=2, day=13),
			date(year=2025, month=3, day=14),
			date(year=2026, month=4, day=15)
		),
		non_enum_value=date(year=2023, month=1, day=12),
		bad_type_values=["asdfg", 123, 1.23, True, None]
	)


def test_date_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=Date,
		good_values=[date(year=2024, month=2, day=13)],
		bad_values=[date(year=2023, month=2, day=13)],
		pattern=r'^2024-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
	)


def test_date_spec_min_max_restriction(min_max_value_tester):
	min_max_value_tester(
		spec_creator=Date,
		min_value=date(year=2024, month=2, day=13),
		max_value=date(year=2025, month=6, day=28),
		less_value=date(year=2024, month=2, day=12),
		more_value=date(year=2025, month=6, day=29)
	)
