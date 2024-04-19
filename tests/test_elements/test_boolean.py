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
from fastapi_xroad_soap.internal.base import BaseElementSpec
from fastapi_xroad_soap.internal.elements.models import Boolean, BooleanSpec


__all__ = [
	"test_boolean_spec",
	"test_boolean_spec_data_init"
]


def test_boolean_spec(spec_tester):
	spec_tester(
		spec_creator=Boolean,
		spec_type=BooleanSpec,
		spec_base_type=BaseElementSpec,
		element_type=bool,
		wsdl_type_name="boolean",
		default_wsdl_type_name=None
	)


def test_boolean_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=Boolean,
		good_values=[True, False],
		bad_values=[None, "asdfg", 1.2345, {}, []]
	)
