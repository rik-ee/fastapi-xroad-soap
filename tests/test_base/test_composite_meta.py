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
import typing as t
from pydantic_xml import model
from fastapi_xroad_soap.internal.base import ElementSpecMeta
from .conftest import CustomModelObject, CustomModelSpec


__all__ = ["test_element_spec_meta_subclass"]


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
