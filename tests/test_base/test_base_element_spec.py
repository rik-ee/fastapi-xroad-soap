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
from abc import ABC
from pydantic_xml import model
from fastapi_xroad_soap.internal.constants import A8nType
from fastapi_xroad_soap.internal.base import BaseElementSpec
from .conftest import (
	CustomModelObject,
	CustomModelInternal,
	CustomModelSpec
)


__all__ = [
	"test_base_element_spec",
	"test_base_element_spec_subclass",
	"test_base_element_spec_a8n"
]


def test_base_element_spec():
	assert issubclass(BaseElementSpec, ABC)

	assert hasattr(BaseElementSpec, "get_element")
	assert hasattr(BaseElementSpec, "get_element_a8n")
	assert hasattr(BaseElementSpec, "set_a8n_type_from")

	assert not hasattr(BaseElementSpec.get_element, "__isabstractmethod__")
	assert not hasattr(BaseElementSpec.get_element_a8n, "__isabstractmethod__")
	assert not hasattr(BaseElementSpec.set_a8n_type_from, "__isabstractmethod__")

	assert hasattr(BaseElementSpec.init_instantiated_data, "__isabstractmethod__")
	assert hasattr(BaseElementSpec.init_deserialized_data, "__isabstractmethod__")


def test_base_element_spec_subclass():
	spec = CustomModelSpec()

	assert spec.element_type == CustomModelObject
	assert spec.raise_error_on_instantiation is False
	assert spec.raise_error_on_deserialization is False

	arg = t.get_args(spec.get_element_a8n())[0]
	assert issubclass(arg, CustomModelInternal)

	el = spec.get_element("fastapi_xroad_soap")
	assert isinstance(el, model.XmlEntityInfo)
	assert el.path == "FastapiXroadSoap"
	assert el.ns == ''
	assert el.nsmap == dict()
	assert el.default_factory == list

	a8n = spec.get_element_a8n()
	assert t.get_origin(a8n) == list
	args = t.get_args(a8n)
	assert len(args) == 1


def test_base_element_spec_a8n():
	def create_spec_set_a8n(_a8n):
		_spec = CustomModelSpec()
		_spec.set_a8n_type_from(_a8n, attr='attr', cls_name='Test')
		return _spec

	for a8n in [A8nType.ABSENT, CustomModelObject]:
		spec = create_spec_set_a8n(a8n)
		assert spec.a8n_type == A8nType.MAND

	for a8n in [t.Optional[CustomModelObject], t.Union[CustomModelObject, None]]:
		spec = create_spec_set_a8n(a8n)
		assert spec.a8n_type == A8nType.OPT

	spec = create_spec_set_a8n(t.List[CustomModelObject])
	assert spec.a8n_type == A8nType.LIST

	for a8n in [t.Optional, t.Union, t.List, list]:
		with pytest.raises(TypeError):
			create_spec_set_a8n(a8n)
		with pytest.raises(TypeError):
			create_spec_set_a8n(a8n[object])
		with pytest.raises(TypeError):
			create_spec_set_a8n(a8n[object, None])

	with pytest.raises(TypeError):
		create_spec_set_a8n(t.Iterable[CustomModelObject])
