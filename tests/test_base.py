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
import textwrap
import functools
import typing as t
from abc import ABC
from enum import Enum
from pydantic_xml import model, element
from fastapi_xroad_soap.internal.envelope import EnvelopeFactory
from fastapi_xroad_soap.internal.constants import A8nType
from fastapi_xroad_soap.internal.base import (
	BaseElementSpec,
	ElementSpecMeta,
	MessageBody
)
from .conftest import (
	CustomModelObject,
	CustomModelInternal,
	CustomModelSpec,
	GoodCustomBody,
	BadInstantiationCustomBody,
	BadDeserializationCustomBody
)


def test_a8ntype_enum():
	assert issubclass(A8nType, Enum)

	assert hasattr(A8nType, "LIST")
	assert hasattr(A8nType, "OPT")
	assert hasattr(A8nType, "MAND")
	assert hasattr(A8nType, "ABSENT")

	assert A8nType.LIST.value == "list"
	assert A8nType.OPT.value == "optional"
	assert A8nType.MAND.value == "mandatory"
	assert A8nType.ABSENT.value == "absent"


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

	store_a8n = functools.partial(
		spec.set_a8n_type_from,
		attr='attr', name='Test'
	)
	store_a8n(A8nType.ABSENT)
	assert spec.a8n_type == A8nType.MAND

	store_a8n(CustomModelObject)
	assert spec.a8n_type == A8nType.MAND

	for a8n in [t.Optional, t.Union, t.List, list]:
		with pytest.raises(TypeError):
			store_a8n(a8n)
		with pytest.raises(TypeError):
			store_a8n(a8n[object])
		with pytest.raises(TypeError):
			store_a8n(a8n[object, None])

	store_a8n(t.Optional[CustomModelObject])
	assert spec.a8n_type == A8nType.OPT

	store_a8n(t.Union[CustomModelObject, None])
	assert spec.a8n_type == A8nType.OPT

	store_a8n(t.List[CustomModelObject])
	assert spec.a8n_type == A8nType.LIST

	with pytest.raises(TypeError):
		store_a8n(t.Iterable[CustomModelObject])


def test_element_spec_meta_subclass():
	spec = CustomModelSpec()

	class TestBody(metaclass=ElementSpecMeta):
		_element_specs: t.Dict[str, t.Any] = dict()
		text: CustomModelObject = spec

	assert "_element_specs" in TestBody.__annotations__
	assert t.get_origin(TestBody.__annotations__["text"]) == list
	assert isinstance(TestBody.text, model.XmlEntityInfo)
	assert hasattr(TestBody, "_element_specs")
	assert TestBody._element_specs["text"] == spec


def test_message_body_subclass():
	class TestBody(MessageBody):
		text: str = element()
		number: int = element()

	body = TestBody(text="asdfg", number=123)
	output = body.to_xml(pretty_print=True).decode()
	output = output.replace("  ", "\t").strip()
	expected = textwrap.dedent("""
		<TestBody>
			<text>asdfg</text>
			<number>123</number>
		</TestBody>
	""").strip()
	assert output == expected


def test_custom_bodies():
	body = GoodCustomBody(cust_elem=CustomModelObject(text="asdfg"))
	factory = EnvelopeFactory[GoodCustomBody]()
	envelope = factory.serialize(content=body)
	factory.deserialize(envelope)

	with pytest.raises(ValueError, match="init_instantiated_data_value_error"):
		BadInstantiationCustomBody(cust_elem=CustomModelObject(text="asdfg"))

	body = BadDeserializationCustomBody(cust_elem=CustomModelObject(text="asdfg"))
	factory = EnvelopeFactory[BadDeserializationCustomBody]()
	envelope = factory.serialize(content=body)
	with pytest.raises(ValueError, match="init_deserialized_data_value_error"):
		factory.deserialize(envelope)
