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
from fastapi_xroad_soap.internal.soap.validators import validate_annotations
from fastapi_xroad_soap.internal.envelope import XroadHeader
from fastapi_xroad_soap.internal.base import MessageBody


class CustomMessageBody(MessageBody):
	pass  # Shut Up SonarCloud


def correct_function(body: CustomMessageBody, header: XroadHeader) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def correct_function_reversed_args(header: XroadHeader, body: CustomMessageBody) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def correct_function_no_return(header: XroadHeader, body: CustomMessageBody) -> None:
	pass  # Shut Up SonarCloud


def incorrect_body_annotation(body: XroadHeader, header: XroadHeader) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def incorrect_body_annotation2(body: CustomMessageBody(), header: XroadHeader) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def incorrect_header_annotation(body: CustomMessageBody, header: CustomMessageBody) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def incorrect_return_annotation(body: CustomMessageBody, header: XroadHeader) -> int:
	pass  # Shut Up SonarCloud


def unallowed_parameter_name(body: CustomMessageBody, header: XroadHeader, footer: XroadHeader) -> CustomMessageBody:
	pass  # Shut Up SonarCloud


def test_validate_annotations_correct():
	expected = {
		"body": CustomMessageBody,
		"header": XroadHeader,
		"return": CustomMessageBody
	}
	annotations1 = validate_annotations('', correct_function)
	assert annotations1 == expected
	annotations2 = validate_annotations('', correct_function_reversed_args)
	assert annotations2 == expected
	annotations3 = validate_annotations('', correct_function_no_return)
	assert annotations3 == {**expected, "return": None}


def test_validate_annotations_incorrect_body():
	with pytest.raises(TypeError):
		validate_annotations('', incorrect_body_annotation)
	with pytest.raises(TypeError):
		validate_annotations('', incorrect_body_annotation2)


def test_validate_annotations_incorrect_header():
	with pytest.raises(ValueError):
		validate_annotations('', incorrect_header_annotation)


def test_validate_annotations_incorrect_return():
	with pytest.raises(TypeError):
		validate_annotations('', incorrect_return_annotation)


def test_validate_annotations_unallowed_parameter_name():
	with pytest.raises(ValueError):
		validate_annotations('', unallowed_parameter_name)
