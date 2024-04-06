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
from fastapi_xroad_soap.internal.envelope import (
	XroadService,
	XroadClient,
	XroadHeader
)


def test_xroad_service():
	service = XroadService(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code",
		service_code="service_code",
		service_version="service_version"
	)
	output = service.to_xml(pretty_print=True).decode()
	output = output.replace("  ", "\t").strip()
	expected = textwrap.dedent("""
	<xro:service xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers" iden:object_type="SERVICE">
		<iden:xRoadInstance>xroad_instance</iden:xRoadInstance>
		<iden:memberClass>member_class</iden:memberClass>
		<iden:memberCode>member_code</iden:memberCode>
		<iden:subsystemCode>subsystem_code</iden:subsystemCode>
		<iden:serviceCode>service_code</iden:serviceCode>
		<iden:serviceVersion>service_version</iden:serviceVersion>
	</xro:service>
	""").strip()
	assert output == expected


def test_xroad_client():
	client = XroadClient(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code"
	)
	output = client.to_xml(pretty_print=True).decode()
	output = output.replace("  ", "\t").strip()
	expected = textwrap.dedent("""
	<xro:client xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers" iden:object_type="SUBSYSTEM">
		<iden:xRoadInstance>xroad_instance</iden:xRoadInstance>
		<iden:memberClass>member_class</iden:memberClass>
		<iden:memberCode>member_code</iden:memberCode>
		<iden:subsystemCode>subsystem_code</iden:subsystemCode>
	</xro:client>
	""").strip()
	assert output == expected


def test_xroad_header():
	header = XroadHeader(
		user_id="user_id",
		proto_ver="proto_ver",
		id="id",
		service=XroadService(
			xroad_instance="xroad_instance",
			member_class="member_class",
			member_code="member_code",
			subsystem_code="subsystem_code",
			service_code="service_code",
			service_version="service_version"
		),
		client=XroadClient(
			xroad_instance="xroad_instance",
			member_class="member_class",
			member_code="member_code",
			subsystem_code="subsystem_code"
		)
	)
	output = header.to_xml(pretty_print=True).decode()
	output = output.replace("  ", "\t").strip()
	expected = textwrap.dedent("""
	<soapenv:Header xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers">
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
	""").strip()
	assert output == expected
