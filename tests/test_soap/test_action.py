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
from pydantic_xml import element
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import (
	GenericEnvelope, AnyBody, XroadHeader
)
from fastapi_xroad_soap.internal.soap import (
	SoapAction, SoapResponse, faults as f
)


__all__ = [
	"test_soap_action_name",
	"test_arguments_from_empty_envelope",
	"test_arguments_from_full_envelope",
	"test_response_from"
]


def test_soap_action_name(create_action):
	for name_len in [4, 31]:
		with pytest.raises(ValueError):
			create_action(
				name='x' * name_len,
				body_type=None
			)
	for name_len in [5, 30]:
		create_action(
			name='x' * name_len,
			body_type=None
		)


def test_arguments_from_empty_envelope(create_action, xroad_header):
	typed_envelope = GenericEnvelope[AnyBody]
	action: SoapAction = create_action(
		body_type=None, header_type=None
	)
	obj: GenericEnvelope = typed_envelope(
		body=AnyBody(), header=xroad_header
	)
	args = action.arguments_from(obj)
	assert len(args) == 0


def test_arguments_from_full_envelope(create_action, xroad_header):
	typed_envelope = GenericEnvelope[AnyBody]
	action: SoapAction = create_action(
		body_type=AnyBody, header_type=XroadHeader
	)
	obj: GenericEnvelope = typed_envelope(
		body=AnyBody(), header=xroad_header
	)
	args = action.arguments_from(obj)
	assert len(args) == 2
	assert isinstance(args[0], MessageBody)
	assert isinstance(args[1], XroadHeader)

	with pytest.raises(f.MissingBodyFault):
		obj: GenericEnvelope = typed_envelope(
			body=None, header=xroad_header
		)
		action.arguments_from(obj)

	with pytest.raises(f.MissingHeaderFault):
		obj: GenericEnvelope = typed_envelope(
			body=AnyBody(), header=None
		)
		action.arguments_from(obj)


def test_response_from(create_action):
	class Response(MessageBody, tag="Response"):
		text: str = element(tag="Text")

	action: SoapAction = create_action()
	resp = action.response_from()
	assert resp.body == b''
	assert resp.media_type is None
	assert resp.raw_headers == [(b'content-length', b'0')]

	action: SoapAction = create_action(return_type=Response)
	resp = action.response_from(Response(text="asdfg"))
	assert isinstance(resp, SoapResponse)

	expected_substr = b"<Response><Text>asdfg</Text></Response>"
	assert expected_substr in resp.body

	with pytest.raises(TypeError):
		action.response_from(AnyBody())
