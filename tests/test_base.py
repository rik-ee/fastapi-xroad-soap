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
from fastapi_xroad_soap.internal import base as b
from .conftest import (
	CustomElement,
	CustomElementSpec,
	CustomElementInternal,
	GoodCustomBody,
	BadCustomBody
)


def test_a8ntype_enum():
	assert issubclass(b.A8nType, Enum)

	assert hasattr(b.A8nType, "LIST")
	assert hasattr(b.A8nType, "OPT")
	assert hasattr(b.A8nType, "MAND")
	assert hasattr(b.A8nType, "ABSENT")

	assert b.A8nType.LIST.value == "list"
	assert b.A8nType.OPT.value == "optional"
	assert b.A8nType.MAND.value == "mandatory"
	assert b.A8nType.ABSENT.value == "absent"


def test_base_element_spec():
	assert issubclass(b.BaseElementSpec, ABC)

	assert hasattr(b.BaseElementSpec, "get_a8n")
	assert hasattr(b.BaseElementSpec, "get_element")
	assert hasattr(b.BaseElementSpec, "store_user_defined_a8n")

	assert hasattr(b.BaseElementSpec.get_a8n, "__isabstractmethod__")
	assert not hasattr(b.BaseElementSpec.get_element, "__isabstractmethod__")
	assert not hasattr(b.BaseElementSpec.store_user_defined_a8n, "__isabstractmethod__")


def test_base_element_spec_subclass():
	spec = CustomElementSpec(raise_error=False)

	assert spec.element_type == CustomElement
	assert spec.raise_error is False

	arg = t.get_args(spec.get_a8n())[0]
	assert issubclass(arg, CustomElementInternal)

	el = spec.get_element("fastapi_xroad_soap")
	assert isinstance(el, model.XmlEntityInfo)
	assert el.path == "FastapiXroadSoap"
	assert el.ns == ''
	assert el.nsmap == dict()
	assert el.default_factory == list

	store_a8n = functools.partial(
		spec.store_user_defined_a8n,
		attr='attr', name='Test'
	)
	store_a8n(b.A8nType.ABSENT)
	assert spec.a8n_type == b.A8nType.MAND

	store_a8n(CustomElement)
	assert spec.a8n_type == b.A8nType.MAND

	for a8n in [t.Optional, t.Union, t.List, list]:
		with pytest.raises(TypeError):
			store_a8n(a8n)
		with pytest.raises(TypeError):
			store_a8n(a8n[object])
		with pytest.raises(TypeError):
			store_a8n(a8n[object, None])

	store_a8n(t.Optional[CustomElement])
	assert spec.a8n_type == b.A8nType.OPT

	store_a8n(t.Union[CustomElement, None])
	assert spec.a8n_type == b.A8nType.OPT

	store_a8n(t.List[CustomElement])
	assert spec.a8n_type == b.A8nType.LIST

	with pytest.raises(TypeError):
		store_a8n(t.Iterable[CustomElement])


def test_element_spec_meta_subclass():
	spec = CustomElementSpec(raise_error=False)

	class TestBody(metaclass=b.ElementSpecMeta):
		_element_specs: t.Dict[str, t.Any] = dict()
		text: CustomElement = spec

	assert "_element_specs" in TestBody.__annotations__
	assert t.get_origin(TestBody.__annotations__["text"]) == list
	assert isinstance(TestBody.text, model.XmlEntityInfo)
	assert hasattr(TestBody, "_element_specs")
	assert TestBody._element_specs["text"] == spec


def test_message_body_subclass():
	class TestBody(b.MessageBody):
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
