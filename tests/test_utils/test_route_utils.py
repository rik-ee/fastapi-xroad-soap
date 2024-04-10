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
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import XroadHeader
from fastapi_xroad_soap.internal.utils import route_utils as utils


def test_with_annotations():
	class TestClass:
		def method(self, arg: int) -> None:
			pass

	def func(a: int, b: str) -> float:
		pass

	annotations = utils.get_annotations(TestClass.method)
	assert annotations == {'arg': int, 'return': None}

	annotations = utils.get_annotations(func)
	assert annotations == {'a': int, 'b': str, 'return': float}


def test_without_annotations():
	class TestClass:
		pass

	def func(a, b):
		pass

	obj = TestClass()
	assert utils.get_annotations(obj) == {}
	assert utils.get_annotations(func) == {}
	assert utils.get_annotations(len) == {}
	assert utils.get_annotations(lambda x: x) == {}
	assert utils.get_annotations([].append) == {}


class CustomMessageBody(MessageBody):
	pass


def correct_function(body: CustomMessageBody, header: XroadHeader) -> CustomMessageBody:
	pass


def correct_function_reversed_args(header: XroadHeader, body: CustomMessageBody) -> CustomMessageBody:
	pass


def correct_function_no_return(header: XroadHeader, body: CustomMessageBody) -> None:
	pass


def incorrect_body_annotation(body: XroadHeader, header: XroadHeader) -> CustomMessageBody:
	pass


def incorrect_body_annotation2(body: CustomMessageBody(), header: XroadHeader) -> CustomMessageBody:
	pass


def incorrect_header_annotation(body: CustomMessageBody, header: CustomMessageBody) -> CustomMessageBody:
	pass


def incorrect_return_annotation(body: CustomMessageBody, header: XroadHeader) -> int:
	pass


def unallowed_parameter_name(body: CustomMessageBody, header: XroadHeader, footer: XroadHeader) -> CustomMessageBody:
	pass


def test_validate_annotations_correct():
	expected = {
		"body": CustomMessageBody,
		"header": XroadHeader,
		"return": CustomMessageBody
	}
	annotations1 = utils.validate_annotations('', correct_function)
	assert annotations1 == expected
	annotations2 = utils.validate_annotations('', correct_function_reversed_args)
	assert annotations2 == expected
	annotations3 = utils.validate_annotations('', correct_function_no_return)
	assert annotations3 == {**expected, "return": None}


def test_validate_annotations_incorrect_body():
	with pytest.raises(TypeError):
		utils.validate_annotations('', incorrect_body_annotation)
	with pytest.raises(TypeError):
		utils.validate_annotations('', incorrect_body_annotation2)


def test_validate_annotations_incorrect_header():
	with pytest.raises(ValueError):
		utils.validate_annotations('', incorrect_header_annotation)


def test_validate_annotations_incorrect_return():
	with pytest.raises(TypeError):
		utils.validate_annotations('', incorrect_return_annotation)


def test_validate_annotations_unallowed_parameter_name():
	with pytest.raises(ValueError):
		utils.validate_annotations('', unallowed_parameter_name)


@pytest.mark.parametrize("anno,expected_positions", [
	({"body": int, "header": str}, {"body": 0, "header": 1}),
	({"header": str, "body": int}, {"body": 1, "header": 0}),
	({"body": int}, {"body": 0, "header": None}),
	({"header": str}, {"body": None, "header": 0}),
	({}, {"body": None, "header": None})
])
def test_extract_parameter_positions(anno, expected_positions):
	positions = utils.extract_parameter_positions(anno)
	assert positions == expected_positions
