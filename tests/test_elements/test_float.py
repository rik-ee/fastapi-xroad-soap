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
import math
import pytest
import typing as t
from enum import Enum
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Float, FloatSpec


__all__ = [
	"test_float_spec",
	"test_float_spec_data_init",
	"test_float_spec_pattern_restriction",
	"test_float_spec_min_max_restriction",
	"test_float_spec_enum_restriction",
	"test_float_spec_invalid_enum_value_type"
]


def test_float_spec(nsmap, a8n_type_tester):
	spec = t.cast(FloatSpec, Float(
		tag="TestFloat",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, FloatSpec)
	assert issubclass(FloatSpec, NumericTypeSpec)

	assert spec.tag == "TestFloat"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == float
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "float"
	assert spec.default_wsdl_type_name == "float"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[float]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestFloat"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_float_spec_data_init():
	spec = t.cast(FloatSpec, Float())

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([1.1, 2.2, 3.3]) == [1.1, 2.2, 3.3]
		for bad_data in [None, "asdfg", 12345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])


def test_float_spec_pattern_restriction():
	spec = t.cast(FloatSpec, Float(pattern=r'^[0-4\.]+$'))
	assert spec.pattern == r'^[0-4\.]+$'

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([0.1234]) == [0.1234]

		for bad_int in [5, 6, 7, 8, 9]:
			with pytest.raises(ValueError):
				bad_value = float(f"0.1234{bad_int}")
				init_data([bad_value])


def test_float_spec_min_max_restriction():
	spec = t.cast(FloatSpec, Float(
		min_value=1.234, max_value=6.789
	))
	assert math.isclose(spec.min_value, 1.234)
	assert math.isclose(spec.max_value, 6.789)

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([1.234, 6.789]) == [1.234, 6.789]

		for bad_value in [1.233, 6.790]:
			with pytest.raises(ValueError):
				init_data([bad_value])


def test_float_spec_enum_restriction():
	class Choice(Enum):
		FIRST = 1.111
		SECOND = 2.222
		THIRD = 3.333

	spec = t.cast(FloatSpec, Float(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)

		for choice in [1.111, 2.222, 3.333]:
			assert init_data([choice]) == [choice]
		with pytest.raises(ValueError):
			init_data([4.4444])


def test_float_spec_invalid_enum_value_type():
	for bad_value in ["asdfg", 123, True, None]:
		class BadChoice(Enum):
			CHOICE = bad_value

		with pytest.raises(TypeError):
			Float(enumerations=BadChoice)
