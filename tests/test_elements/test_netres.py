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
from pydantic import AnyUrl
from fastapi_xroad_soap.internal.elements import StringTypeSpec
from fastapi_xroad_soap.internal.elements.models import NetRes, NetResSpec


__all__ = [
	"test_net_res_spec",
	"test_net_res_spec_data_init",
	"test_net_res_spec_enum_restriction",
	"test_string_spec_pattern_restriction",
	"test_string_spec_min_max_restriction",
	"test_string_spec_length_restriction"
]


def test_net_res_spec(spec_tester):
	spec_tester(
		spec_creator=NetRes,
		spec_type=NetResSpec,
		spec_base_type=StringTypeSpec,
		element_type=AnyUrl,
		wsdl_type_name="anyURI",
		default_wsdl_type_name="anyURI"
	)


def test_net_res_spec_data_init(data_init_tester):
	data_init_tester(
		spec_creator=NetRes,
		good_values=[AnyUrl(url="https://www.example.org")],
		bad_values=[None, True, 12345, 1.2345, {}, []]
	)


def test_net_res_spec_enum_restriction(enum_tester):
	enum_tester(
		spec_creator=NetRes,
		enum_values=(
			AnyUrl(url="https://www.first.com"),
			AnyUrl(url="https://www.second.org"),
			AnyUrl(url="https://www.third.net")
		),
		non_enum_value=AnyUrl(url="https://www.fourth.io"),
		bad_type_values=["asdfg", 123, 1.23, True, None]
	)


def test_string_spec_pattern_restriction(pattern_tester):
	pattern_tester(
		spec_creator=NetRes,
		good_values=[AnyUrl(url="https://www.example.org/subpath")],
		bad_values=[AnyUrl(url="https://www.example.com/subpath")],
		pattern=r'^https?://www\.example\.org[^ \n]*$'
	)


def test_string_spec_min_max_restriction(min_max_length_tester):
	min_url_str = "https://www.example.org/"
	max_url_str = "https://www.example.org/subpath"
	min_max_length_tester(
		spec_creator=NetRes,
		good_values=[
			AnyUrl(min_url_str),
			AnyUrl(max_url_str)
		],
		bad_values=[
			AnyUrl(min_url_str[:-2]),
			AnyUrl(max_url_str + 's')
		],
		min_length=len(min_url_str),
		max_length=len(max_url_str)
	)


def test_string_spec_length_restriction(length_tester):
	url = "https://www.example.org/asdfg"
	shorter, longer = url[:-1], url + 'h'
	length_tester(
		spec_creator=NetRes,
		good_values=[AnyUrl(url=url)],
		bad_values=[AnyUrl(url=shorter), AnyUrl(url=longer)],
		length=len(url)
	)
