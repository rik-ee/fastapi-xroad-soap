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
from fastapi_xroad_soap.internal import utils


def test_with_annotations():
	class TestClass:
		def method(self, arg: int) -> None:
			pass  # Shut Up SonarCloud

	def func(a: int, b: str) -> float:
		pass  # Shut Up SonarCloud

	annotations = utils.get_annotations(TestClass.method)
	assert annotations == {'arg': int, 'return': None}

	annotations = utils.get_annotations(func)
	assert annotations == {'a': int, 'b': str, 'return': float}


def test_without_annotations():
	class TestClass:
		pass  # Shut Up SonarCloud

	def func(a, b):
		pass  # Shut Up SonarCloud

	obj = TestClass()
	assert utils.get_annotations(obj) == {}
	assert utils.get_annotations(func) == {}
	assert utils.get_annotations(len) == {}
	assert utils.get_annotations(lambda x: x) == {}
	assert utils.get_annotations([].append) == {}


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
