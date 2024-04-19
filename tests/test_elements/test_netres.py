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
from pydantic import AnyUrl
from pydantic_xml import model
from fastapi_xroad_soap.internal.elements import StringTypeSpec
from fastapi_xroad_soap.internal.elements.models import NetRes, NetResSpec


__all__ = [
	"test_string_spec",
	# "test_string_spec_data_init",
	# "test_string_spec_pattern_restriction",
	# "test_string_spec_length_restriction",
	# "test_string_spec_min_max_restriction",
	# "test_string_spec_enum_restriction",
	# "test_string_spec_invalid_enum_value_type",
	# "test_string_process_whitespace"
]


def test_string_spec(nsmap, a8n_type_tester):
	spec = t.cast(NetResSpec, NetRes(
		tag="TestNetRes",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, NetResSpec)
	assert issubclass(NetResSpec, StringTypeSpec)

	assert spec.tag == "TestNetRes"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == AnyUrl
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "anyURI"
	assert spec.default_wsdl_type_name == "anyURI"

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[AnyUrl]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestNetRes"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_string_spec_data_init():
	spec = t.cast(NetResSpec, NetRes())

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		url = AnyUrl(url="https://www.example.org/subpath?param=value#fragment")
		assert init_data([url]) == [url]
		for bad_data in [None, 12345, 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])


def test_string_spec_pattern_restriction():
	pat = r'^https?://www\.example\.org[^ \n]*$'
	spec = t.cast(NetResSpec, NetRes(pattern=pat))
	assert spec.pattern == pat

	url_1 = AnyUrl(url="https://www.example.org/subpath?param=value#fragment")
	url_2 = AnyUrl(url="https://www.example.com/subpath?param=value#fragment")

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([url_1]) == [url_1]

		with pytest.raises(ValueError):
			init_data([url_2])


def test_string_spec_length_restriction():
	url_str = "https://www.example.org/subpath?param=value"
	spec = t.cast(NetResSpec, NetRes(length=len(url_str)))
	assert spec.length == len(url_str)

	url_1 = AnyUrl(url=url_str)
	url_2 = AnyUrl(url=url_str + "#fragment")

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([url_1]) == [url_1]

		with pytest.raises(ValueError):
			init_data([url_2])


def test_string_spec_min_max_restriction():
	min_url_str = "https://www.example.org/subpath?param=value"
	max_url_str = "https://www.example.org/subpath?param=value#fragment"

	spec = t.cast(NetResSpec, NetRes(
		min_length=len(min_url_str),
		max_length=len(max_url_str)
	))
	assert spec.min_length == len(min_url_str)
	assert spec.max_length == len(max_url_str)

	shorter_url = AnyUrl(url="https://www.example.org/subpath?param=valu")
	longer_url = AnyUrl(url="https://www.example.org/subpath?param=value#fragments")

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		min_url = AnyUrl(url=min_url_str)
		max_url = AnyUrl(url=max_url_str)
		assert init_data([min_url, max_url]) == [min_url, max_url]

		for bad_value in [shorter_url, longer_url]:
			with pytest.raises(ValueError):
				init_data([bad_value])


def test_string_spec_enum_restriction():
	class Choice(Enum):
		FIRST = AnyUrl(url="https://www.first.com")
		SECOND = AnyUrl(url="https://www.second.org")
		THIRD = AnyUrl(url="https://www.third.net")

	spec = t.cast(NetResSpec, NetRes(enumerations=Choice))
	assert spec.enumerations == Choice

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)

		choices = [c.value for c in Choice]
		assert init_data(choices) == choices

		with pytest.raises(ValueError):
			init_data([AnyUrl(url="https://www.fourth.io")])


def test_string_spec_invalid_enum_value_type():
	for bad_value in [123, 1.23, True, None]:
		class BadChoice(Enum):
			CHOICE = bad_value

		with pytest.raises(TypeError):
			NetRes(enumerations=BadChoice)
