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
from pydantic_xml import element
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import (
	GenericEnvelope,
	GenericFault,
	GenericBody,
	AnyBody
)


def test_generic_envelope():
	assert issubclass(GenericEnvelope, t.Generic)

	class CustomBody(MessageBody):
		text: str = element(tag="CustomText")

	typed_envelope = GenericEnvelope[CustomBody]
	obj = typed_envelope(body=CustomBody(text="asdfg"))

	output = obj.to_xml(pretty_print=False)
	expected = utils.linearize_xml("""
		<Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<Body>
				<CustomText>asdfg</CustomText>
			</Body>
		</Envelope>
	""")
	assert output == expected


def test_generic_fault():
	assert issubclass(GenericFault, t.Generic)

	class CustomDetail(MessageBody):
		text: str = element(tag="CustomText")

	typed_fault = GenericFault[CustomDetail]
	obj = typed_fault(
		faultcode="ClientError",
		faultstring="Custom Error Message",
		faultactor="soap/service/subcomponent",
		detail=CustomDetail(
			text="asdfg"
		)
	)  # type: MessageBody

	output = obj.to_xml(pretty_print=False)
	expected = utils.linearize_xml("""
		<soapenv:Fault xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<faultcode>ClientError</faultcode>
			<faultstring>Custom Error Message</faultstring>
			<faultactor>soap/service/subcomponent</faultactor>
			<detail>
				<CustomText>asdfg</CustomText>
			</detail>
		</soapenv:Fault>
	""")
	assert output == expected


def test_generic_body():
	assert issubclass(GenericBody, t.Generic)

	class CustomContent(MessageBody, tag="CustomContent"):
		text: str = element("CustomText")

	typed_body = GenericBody[CustomContent]
	obj = typed_body(content=CustomContent(text="asdfg"))

	output = obj.to_xml(pretty_print=False)
	expected = utils.linearize_xml("""
		<Body xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<CustomContent>
				<CustomText>asdfg</CustomText>
			</CustomContent>
		</Body>
	""")
	assert output == expected


def test_any_body():
	assert issubclass(AnyBody, MessageBody)
	output = AnyBody().to_xml(pretty_print=False)
	expected = b'<Body xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"/>'
	assert output == expected
