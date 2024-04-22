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
import typing as t
from pydantic_xml import element
from fastapi_xroad_soap.internal.envelope import EnvelopeFactory
from fastapi_xroad_soap.internal.base import MessageBody
from .conftest import (
	CustomModelInternal,
	CustomModelObject,
	GoodCustomBody,
	BadInstantiationCustomBody,
	BadDeserializationCustomBody
)


__all__ = [
	"test_message_body_subclass",
	"test_custom_bodies",
	"test_nested_models",
	"test_nested_models_errors"
]


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


def test_nested_models():
	class ParentModel(MessageBody):
		nested_model = GoodCustomBody.Element()
		not_body: t.List[str] = element()

	models = ParentModel.nested_models()
	assert CustomModelInternal in models
	assert GoodCustomBody in models
	assert ParentModel in models


def test_nested_models_errors():
	class ParentModel(MessageBody):
		bad_a8n: t.Union[int, str] = element()

	with pytest.raises(ValueError):
		ParentModel.nested_models()
