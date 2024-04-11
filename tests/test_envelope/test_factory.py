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
import textwrap
from pydantic_xml import element
from fastapi_xroad_soap.internal import constants as const
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import (
	EnvelopeFactory,
	XroadService,
	XroadClient,
	XroadHeader,
	GenericFault,
	GenericBody,
	AnyBody
)


@pytest.fixture(name="header", scope="function")
def fixture_header():
	service = XroadService(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code",
		service_code="service_code",
		service_version="service_version"
	)
	client = XroadClient(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code"
	)
	return XroadHeader(
		user_id="user_id",
		proto_ver="proto_ver",
		id="id",
		service=service,
		client=client
	)


def test_factory_1():
	assert hasattr(EnvelopeFactory, "serialize")
	assert hasattr(EnvelopeFactory, "deserialize")
	assert issubclass(EnvelopeFactory, t.Generic)

	name = EnvelopeFactory[MessageBody].__name__
	assert name == "EnvelopeFactory[MessageBody]"


def test_factory_2():
	class CustomBody(MessageBody, tag="CustomBody"):
		pass

	factory = EnvelopeFactory[CustomBody]
	tag = getattr(factory, "_type").__xml_tag__
	assert tag == "CustomBody"

	factory = getattr(factory(), "_factory")
	nsmap = factory.__xml_nsmap__
	for k, v in const.HEADER_NSMAP.items():
		assert k in nsmap
		assert v == nsmap[k]


def test_factory_3():
	class CustomBody(MessageBody, nsmap={"abc": "qwerty"}):
		pass

	factory = EnvelopeFactory[CustomBody]
	tag = getattr(factory, "_type").__xml_tag__
	assert tag == "MessageBody"

	factory = getattr(factory(), "_factory")
	nsmap = factory.__xml_nsmap__
	for k, v in const.HEADER_NSMAP.items():
		assert k in nsmap
		assert v == nsmap[k]
	assert "abc" in nsmap
	assert "qwerty" == nsmap["abc"]


def test_factory_4():
	class CustomFault(GenericFault):
		pass

	factory = EnvelopeFactory[CustomFault]
	factory = getattr(factory(), "_factory")
	nsmap = factory.__xml_nsmap__
	for k, v in nsmap.items():
		assert k in const.ENV_NSMAP
		assert v == const.ENV_NSMAP[k]


def test_factory_5():
	class CustomBody(MessageBody, tag="CustomBody"):
		text: str = element(tag="CustomText")

	class AltBody(MessageBody):
		pass

	envelope = EnvelopeFactory[CustomBody]()
	with pytest.raises(TypeError):
		envelope.serialize(content=AltBody())

	xml_str = envelope.serialize(
		content=CustomBody(text="qwerty"), pretty_print=True
	).replace(b'  ', b'\t').strip()

	expected = textwrap.dedent("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers">
			<soapenv:Body>
				<CustomBody>
					<CustomText>qwerty</CustomText>
				</CustomBody>
			</soapenv:Body>
		</soapenv:Envelope>
	""").encode().strip()
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

		envelope2 = EnvelopeFactory()
		obj = envelope2.deserialize(content)
		assert hasattr(obj, "header")
		assert hasattr(obj, "body")
		assert isinstance(obj.body, AnyBody)
		assert hasattr(obj.body, "content")
		assert isinstance(obj.body.content, MessageBody)


def test_factory_6(header: XroadHeader):
	class CustomBody(MessageBody, tag="CustomBody"):
		text: str = element(tag="CustomText")

	envelope = EnvelopeFactory[CustomBody]()
	xml_str = envelope.serialize(
		content=CustomBody(text="qwerty"),
		header=header,
		pretty_print=True
	).replace(b'  ', b'\t').strip()

	expected = textwrap.dedent("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers">
			<soapenv:Header>
				<xro:userId>user_id</xro:userId>
				<xro:protocolVersion>proto_ver</xro:protocolVersion>
				<xro:id>id</xro:id>
				<xro:service iden:object_type="SERVICE">
					<iden:xRoadInstance>xroad_instance</iden:xRoadInstance>
					<iden:memberClass>member_class</iden:memberClass>
					<iden:memberCode>member_code</iden:memberCode>
					<iden:subsystemCode>subsystem_code</iden:subsystemCode>
					<iden:serviceCode>service_code</iden:serviceCode>
					<iden:serviceVersion>service_version</iden:serviceVersion>
				</xro:service>
				<xro:client iden:object_type="SUBSYSTEM">
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
	""").encode().strip()
	assert xml_str == expected
