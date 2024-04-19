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
from datetime import time
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Time, TimeSpec


__all__ = [
	"test_time_spec",
	"test_time_spec_data_init",
	"test_time_spec_pattern_restriction",
	"test_time_spec_min_max_restriction",
	"test_time_spec_enum_restriction"
]


def test_time_spec(nsmap, a8n_type_tester):
	spec = t.cast(TimeSpec, Time(
		tag="TestTime",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, TimeSpec)
	assert issubclass(TimeSpec, NumericTypeSpec)

	assert spec.tag == "TestTime"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == time
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "time"
	assert spec.default_wsdl_type_name == "time"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[time]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestTime"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_time_spec_data_init():
	spec = t.cast(TimeSpec, Time())
	_time = time(hour=11, minute=34, second=56)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([_time]) == [_time]
		for bad_data in [None, "asdfg", 12345, 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])


def test_time_spec_pattern_restriction():
	pat = r'^11:[0-5][0-9]:[0-5][0-9]$'
	spec = t.cast(TimeSpec, Time(pattern=pat))
	assert spec.pattern == pat

	good_time = time(hour=11, minute=34, second=56)
	bad_time = time(hour=10, minute=34, second=56)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([good_time]) == [good_time]

		with pytest.raises(ValueError):
			init_data([bad_time])


def test_time_spec_min_max_restriction():
	min_time = time(hour=11, minute=34, second=56)
	max_time = time(hour=12, minute=34, second=56)
	spec = t.cast(TimeSpec, Time(
		min_value=min_time,
		max_value=max_time
	))
	assert spec.min_value == min_time
	assert spec.max_value == max_time

	less_time = time(hour=11, minute=34, second=55)
	more_time = time(hour=12, minute=34, second=57)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		times = [min_time, max_time]
		assert init_data(times) == times

		for bad_time in [less_time, more_time]:
			with pytest.raises(ValueError):
				init_data([bad_time])


def test_time_spec_enum_restriction():
	class Choice(Enum):
		FIRST = time(hour=10, minute=10, second=10)
		SECOND = time(hour=11, minute=11, second=11)
		THIRD = time(hour=12, minute=12, second=12)

	spec = t.cast(TimeSpec, Time(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		choices = [c.value for c in Choice]
		assert init_data(choices) == choices

		with pytest.raises(ValueError):
			init_data([time(hour=9, minute=9, second=9)])


def test_time_spec_invalid_enum_value_type():
	for bad_value in ["asdfg", 123, 1.23, True, None]:
		class BadChoice(Enum):
			CHOICE = bad_value

		with pytest.raises(TypeError):
			Time(enumerations=BadChoice)
