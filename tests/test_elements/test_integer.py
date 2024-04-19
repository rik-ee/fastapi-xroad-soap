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
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import NumericTypeSpec
from fastapi_xroad_soap.internal.elements.models import Integer, IntegerSpec


__all__ = [
	"test_integer_spec",
	"test_integer_spec_pattern_restriction",
	"test_integer_spec_total_digits_restriction",
	"test_integer_spec_min_max_restriction",
	"test_integer_spec_enum_restriction"
]


def test_integer_spec(nsmap, a8n_type_tester):
	spec = t.cast(IntegerSpec, Integer(
		tag="TestInteger",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, IntegerSpec)
	assert issubclass(IntegerSpec, NumericTypeSpec)

	assert spec.tag == "TestInteger"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == int
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([1, 2, 3]) == [1, 2, 3]
		for bad_data in [None, "asdfg", 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "integer"
	assert spec.default_wsdl_type_name == "integer"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[int]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestInteger"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_integer_spec_pattern_restriction():
	spec = t.cast(IntegerSpec, Integer(pattern=r'^[0-4]+$'))
	assert spec.pattern == r'^[0-4]+$'

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([12340]) == [12340]

		for bad_int in [5, 6, 7, 8, 9]:
			with pytest.raises(ValueError):
				bad_value = int(f"12340{bad_int}")
				init_data([bad_value])


def test_integer_spec_total_digits_restriction():
	spec = t.cast(IntegerSpec, Integer(total_digits=4))
	assert spec.total_digits == 4

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([9999]) == [9999]

		with pytest.raises(ValueError):
			init_data([10_000])


def test_integer_spec_min_max_restriction():
	spec = t.cast(IntegerSpec, Integer(
		min_value=1234, max_value=6789
	))
	assert spec.min_value == 1234
	assert spec.max_value == 6789

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([1234, 6789]) == [1234, 6789]

		for bad_value in [1233, 6790]:
			with pytest.raises(ValueError):
				init_data([bad_value])


def test_integer_spec_enum_restriction():
	class Choice(Enum):
		FIRST = 1111
		SECOND = 2222
		THIRD = 3333

	spec = t.cast(IntegerSpec, Integer(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)

		for choice in [1111, 2222, 3333]:
			assert init_data([choice]) == [choice]
		with pytest.raises(ValueError):
			init_data([44444])
