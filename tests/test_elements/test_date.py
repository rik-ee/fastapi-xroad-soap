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
from enum import Enum
from datetime import date
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Date, DateSpec


__all__ = [
	"test_date_spec",
	"test_date_spec_data_init",
	"test_date_spec_pattern_restriction",
	"test_date_spec_min_max_restriction",
	"test_date_spec_enum_restriction",
	"test_date_spec_invalid_enum_value_type"
]


def test_date_spec(nsmap, a8n_type_tester):
	spec = t.cast(DateSpec, Date(
		tag="TestDate",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, DateSpec)
	assert issubclass(DateSpec, NumericTypeSpec)

	assert spec.tag == "TestDate"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == date
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "date"
	assert spec.default_wsdl_type_name == "date"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[date]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestDate"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_date_spec_data_init():
	spec = t.cast(DateSpec, Date())
	_date = date(year=2024, month=2, day=13)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([_date]) == [_date]
		for bad_data in [None, "asdfg", 12345, 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])


def test_date_spec_pattern_restriction():
	pat = r'^2024-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
	spec = t.cast(DateSpec, Date(pattern=pat))
	assert spec.pattern == pat

	good_date = date(year=2024, month=2, day=13)
	bad_date = date(year=2023, month=2, day=13)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([good_date]) == [good_date]

		with pytest.raises(ValueError):
			init_data([bad_date])


def test_date_spec_min_max_restriction():
	min_date = date(year=2024, month=2, day=13)
	max_date = date(year=2025, month=6, day=28)
	spec = t.cast(DateSpec, Date(
		min_value=min_date,
		max_value=max_date
	))
	assert spec.min_value == min_date
	assert spec.max_value == max_date

	less_date = date(year=2024, month=2, day=12)
	more_date = date(year=2025, month=6, day=29)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		dates = [min_date, max_date]
		assert init_data(dates) == dates

		for bad_time in [less_date, more_date]:
			with pytest.raises(ValueError):
				init_data([bad_time])


def test_date_spec_enum_restriction():
	class Choice(Enum):
		FIRST = date(year=2024, month=2, day=13)
		SECOND = date(year=2025, month=3, day=14)
		THIRD = date(year=2026, month=4, day=15)

	spec = t.cast(DateSpec, Date(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		choices = [c.value for c in Choice]
		assert init_data(choices) == choices

		with pytest.raises(ValueError):
			init_data([date(year=2023, month=1, day=12)])


def test_date_spec_invalid_enum_value_type():
	for bad_value in ["asdfg", 123, 1.23, True, None]:
		class BadChoice(Enum):
			CHOICE = bad_value

		with pytest.raises(TypeError):
			Date(enumerations=BadChoice)
