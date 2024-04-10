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
import textwrap
import typing as t
from pydantic_xml import element
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
	obj = typed_envelope(body=CustomBody(text="asdfg"))  # type: MessageBody

	out_raw = obj.to_xml(pretty_print=True).decode()
	out_fmt = out_raw.replace('  ', '\t').strip()
	expected = textwrap.dedent("""
		<Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<Body>
				<CustomText>asdfg</CustomText>
			</Body>
		</Envelope>
	""").strip()
	assert out_fmt == expected


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

	out_raw = obj.to_xml(pretty_print=True).decode()
	out_fmt = out_raw.replace('  ', '\t').strip()
	expected = textwrap.dedent("""
		<soapenv:Fault xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<faultcode>ClientError</faultcode>
			<faultstring>Custom Error Message</faultstring>
			<faultactor>soap/service/subcomponent</faultactor>
			<detail>
				<CustomText>asdfg</CustomText>
			</detail>
		</soapenv:Fault>
	""").strip()
	assert out_fmt == expected


def test_generic_body():
	assert issubclass(GenericBody, t.Generic)

	class CustomContent(MessageBody, tag="CustomContent"):
		text: str = element("CustomText")

	typed_body = GenericBody[CustomContent]
	obj = typed_body(content=CustomContent(text="asdfg"))

	out_raw = obj.to_xml(pretty_print=True).decode()
	out_fmt = out_raw.replace('  ', '\t').strip()
	expected = textwrap.dedent("""
		<Body xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<CustomContent>
				<CustomText>asdfg</CustomText>
			</CustomContent>
		</Body>
	""").strip()
	assert out_fmt == expected


def test_any_body():
	assert issubclass(AnyBody, MessageBody)
	out_raw = AnyBody().to_xml(pretty_print=True).decode()
	expected = '<Body xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"/>'
	assert out_raw.strip() == expected.strip()
