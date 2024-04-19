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
from pydantic_xml import model
from fastapi_xroad_soap.internal.base import BaseElementSpec
from fastapi_xroad_soap.internal.elements.models import Boolean, BooleanSpec


__all__ = [
	"test_boolean_spec",
	"test_boolean_spec_data_init"
]


def test_boolean_spec(nsmap, a8n_type_tester):
	spec = t.cast(BooleanSpec, Boolean(
		tag="TestBoolean",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, BooleanSpec)
	assert issubclass(BooleanSpec, BaseElementSpec)

	assert spec.tag == "TestBoolean"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == bool
	assert spec.internal_type is None
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "boolean"
	with pytest.raises(NotImplementedError):
		_ = spec.default_wsdl_type_name

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[bool]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestBoolean"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_boolean_spec_data_init():
	spec = t.cast(BooleanSpec, Boolean())

	for func in [spec.init_instantiated_data, spec.init_deserialized_data]:
		init_data = t.cast(t.Callable, func)
		assert init_data([True, False]) == [True, False]
		for bad_data in [None, "asdfg", 1.2345, {}, []]:
			with pytest.raises(TypeError):
				init_data([bad_data])
