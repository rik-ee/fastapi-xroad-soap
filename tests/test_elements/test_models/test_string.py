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
import string
import typing as t
from enum import Enum
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import StringTypeSpec
from fastapi_xroad_soap.internal.elements.models import String, StringSpec


__all__ = [
	"test_string_spec",
	"test_string_spec_pattern_restriction",
	"test_string_spec_length_restriction",
	"test_string_spec_min_max_restriction",
	"test_string_spec_enum_restriction"
]


def test_string_spec(nsmap, a8n_type_tester):
	spec = t.cast(StringSpec, String(
		tag="TestString",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, StringSpec)
	assert issubclass(StringSpec, StringTypeSpec)

	assert spec.tag == "TestString"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == str
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data(['a', 'b', 'c']) == ['a', 'b', 'c']
		for bad_data in [None, 12345, 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "string"
	assert spec.default_wsdl_type_name == "string"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[str]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestString"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_string_spec_pattern_restriction():
	spec = t.cast(StringSpec, String(pattern=r'^[a-z]+$'))
	assert spec.pattern == r'^[a-z]+$'

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data(["abcxyz"]) == ["abcxyz"]

		for bad_char in string.ascii_uppercase:
			with pytest.raises(ValueError):
				bad_value = f"abcxyz{bad_char}"
				init_data([bad_value])


def test_string_spec_length_restriction():
	spec = t.cast(StringSpec, String(length=5))
	assert spec.length == 5

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data(["abcde", "qwert"]) == ["abcde", "qwert"]

		for bad_value in ["abcd", "abcdef"]:
			with pytest.raises(ValueError):
				init_data([bad_value])


def test_string_spec_min_max_restriction():
	spec = t.cast(StringSpec, String(
		min_length=5, max_length=10
	))
	assert spec.min_length == 5
	assert spec.max_length == 10

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data(["abcde", "abcdeABCDE"]) == ["abcde", "abcdeABCDE"]

		for bad_value in ["abcd", "abcdeABCDEF"]:
			with pytest.raises(ValueError):
				init_data([bad_value])


def test_string_spec_enum_restriction():
	class Choice(Enum):
		FIRST = "qwerty"
		SECOND = "asdfg"
		THIRD = "zxcvb"

	spec = t.cast(StringSpec, String(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)

		for choice in ["qwerty", "asdfg", "zxcvb"]:
			assert init_data([choice]) == [choice]
		with pytest.raises(ValueError):
			init_data(["tyuio"])
