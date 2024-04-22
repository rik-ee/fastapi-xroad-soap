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
from fastapi_xroad_soap.internal.base import dynamic_spec, BaseElementSpec
from .conftest import CustomModelObject


__all__ = ['test_dynamic_spec']


def test_dynamic_spec():
	spec = dynamic_spec(CustomModelObject)
	assert isinstance(spec, BaseElementSpec)

	assert spec.element_type == CustomModelObject
	assert spec.has_constraints is False

	assert spec.init_instantiated_data([123]) == [123]
	assert spec.init_deserialized_data([123]) == [123]

	assert spec.wsdl_type_name(with_tns=True) == "tns:CustomModelObject"
	assert spec.wsdl_type_name(with_tns=False) == "CustomModelObject"
