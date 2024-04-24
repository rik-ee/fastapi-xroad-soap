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
import typing as t
from pydantic_xml import element
from fastapi_xroad_soap.internal import utils, constants as const
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import (
	EnvelopeFactory, GenericFault, GenericBody, AnyBody
)


def test_factory_attributes():
	assert hasattr(EnvelopeFactory, "serialize")
	assert hasattr(EnvelopeFactory, "deserialize")
	assert issubclass(EnvelopeFactory, t.Generic)

	name = EnvelopeFactory[MessageBody].__name__
	assert name == "EnvelopeFactory[MessageBody]"


def test_factory_class_args():
	class CustomBody(MessageBody, tag="CustomBody", nsmap={"abc": "qwerty"}):
		pass

	factory = EnvelopeFactory[CustomBody]
	tag = getattr(factory, "_type").__xml_tag__
	assert tag == "CustomBody"

	factory = getattr(factory(), "_factory")
	nsmap = factory.__xml_nsmap__
	for k, v in const.HEADER_NSMAP.items():
		assert k in nsmap
		assert v == nsmap[k]

	assert "abc" in nsmap
	assert "qwerty" == nsmap["abc"]


def test_factory_fault():
	class CustomFault(GenericFault):
		pass

	factory = EnvelopeFactory[CustomFault]
	factory = getattr(factory(), "_factory")
	nsmap = factory.__xml_nsmap__
	for k, v in nsmap.items():
		assert k in const.ENV_NSMAP
		assert v == const.ENV_NSMAP[k]


def test_factory_ser_without_header():
	class CustomBody(MessageBody, tag="CustomBody"):
		text: str = element(tag="CustomText")

	class AltBody(MessageBody):
		pass

	factory = EnvelopeFactory[CustomBody]
	envelope = factory(exclude_xroad_nsmap=True)

	with pytest.raises(TypeError):
		envelope.serialize(content=AltBody())

	xml_str = envelope.serialize(
		content=CustomBody(text="qwerty"),
		pretty_print=False
	).replace(b'\n', b'')

	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='yes'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<CustomBody>
					<CustomText>qwerty</CustomText>
				</CustomBody>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert xml_str == expected

	for content in [xml_str, xml_str.decode()]:
		obj = envelope.deserialize(content)
		assert hasattr(obj, "header")
		assert hasattr(obj, "body")
		assert isinstance(obj.body, GenericBody)
		assert hasattr(obj.body, "content")
		assert isinstance(obj.body.content, CustomBody)
		assert hasattr(obj.body.content, "text")
		assert obj.body.content.text == "qwerty"
		assert obj.header is None

		envelope2 = EnvelopeFactory()
		obj = envelope2.deserialize(content)
		assert hasattr(obj, "header")
		assert hasattr(obj, "body")
		assert isinstance(obj.body, AnyBody)
		assert hasattr(obj.body, "content")
		assert isinstance(obj.body.content, MessageBody)
		assert obj.header is None


def test_factory_ser_with_header(xroad_header):
	class CustomBody(MessageBody, tag="CustomBody"):
		text: str = element(tag="CustomText")

	factory = EnvelopeFactory[CustomBody]
	envelope = factory(exclude_xroad_nsmap=False)

	xml_str = envelope.serialize(
		content=CustomBody(text="qwerty"),
		header=xroad_header,
		pretty_print=False
	).replace(b'\n', b'')

	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope 
			xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
			xmlns:xro="http://x-road.eu/xsd/xroad.xsd" 
			xmlns:iden="http://x-road.eu/xsd/identifiers">
			<soapenv:Header>
				<xro:userId>user_id</xro:userId>
				<xro:protocolVersion>proto_ver</xro:protocolVersion>
				<xro:id>id</xro:id>
				<xro:service iden:objectType="SERVICE">
					<iden:xRoadInstance>xroad_instance</iden:xRoadInstance>
					<iden:memberClass>member_class</iden:memberClass>
					<iden:memberCode>member_code</iden:memberCode>
					<iden:subsystemCode>subsystem_code</iden:subsystemCode>
					<iden:serviceCode>service_code</iden:serviceCode>
					<iden:serviceVersion>service_version</iden:serviceVersion>
				</xro:service>
				<xro:client iden:objectType="SUBSYSTEM">
					<iden:xRoadInstance>xroad_instance</iden:xRoadInstance>
					<iden:memberClass>member_class</iden:memberClass>
					<iden:memberCode>member_code</iden:memberCode>
					<iden:subsystemCode>subsystem_code</iden:subsystemCode>
				</xro:client>
			</soapenv:Header>
			<soapenv:Body>
				<CustomBody>
					<CustomText>qwerty</CustomText>
				</CustomBody>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	for char in [b'\t', b'\n']:
		expected = expected.replace(char, b'')
	assert xml_str == expected
