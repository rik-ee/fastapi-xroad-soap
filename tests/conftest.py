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
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.envelope import (
	XroadHeader, XroadService, XroadClient
)


__all__ = [
	"fixture_read_wsdl_file",
	"fixture_xroad_header",
	"fixture_multipart_data",
	"fixture_mixed_multipart_data"
]


@pytest.fixture(name="read_wsdl_file", scope="session")
def fixture_read_wsdl_file() -> t.Callable:
	def closure(file_name: str) -> bytes:
		full_path = "wsdl_files/" + file_name
		path = utils.search_upwards(full_path, __file__)
		file_data: bytes = utils.read_cached_file(path, binary=True)
		return file_data.replace(b'\r\n', b'\n').strip()
	return closure


@pytest.fixture(name="xroad_header", scope="function")
def fixture_xroad_header() -> XroadHeader:
	return XroadHeader(
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


@pytest.fixture(name="multipart_data", scope="session")
def fixture_multipart_data() -> t.Tuple[bytes, str]:
	content_type = '; '.join([
		'multipart/related',
		'type="text/xml"',
		'start="<rootpart@soapui.org>"',
		'boundary="----=_Part_29_1072688887.1713872993708"'
	])
	content = b''.join([
		b'\r\n------=_Part_29_1072688887.1713872993708',
		b'\r\nContent-Type: text/xml; charset=UTF-8',
		b'\r\nContent-Transfer-Encoding: 8bit',
		b'\r\nContent-ID: <rootpart@soapui.org>',
		b'\r\n\r\n',
		b'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">',
		b'\t<soapenv:Body>',
		b'\t\t<Request>',
		b'\t\t\t<File>cid:783266853352</File>',
		b'\t\t</Request>',
		b'\t</soapenv:Body>',
		b'</soapenv:Envelope>',
		b'\r\n------=_Part_29_1072688887.1713872993708',
		b'\r\nContent-Type: text/plain; charset=us-ascii; name=test.txt',
		b'\r\nContent-Transfer-Encoding: 7bit',
		b'\r\nContent-ID: <783266853352>',
		b'\r\nContent-Disposition: attachment; name="test.txt"; filename="test.txt"',
		b'\r\n\r\n',
		b'lorem ipsum dolor sit amet',
		b'\r\n------=_Part_29_1072688887.1713872993708--\r\n'
	])
	return content, content_type


@pytest.fixture(name="mixed_multipart_data", scope="session")
def fixture_mixed_multipart_data() -> t.Tuple[bytes, str]:
	content_type = '; '.join([
		'multipart/related',
		'type="text/xml"',
		'start="<rootpart@soapui.org>"',
		'boundary="----=_Part_36_146605718.1713895882267"'
	])
	content = b''.join([
		b'\r\n------=_Part_36_146605718.1713895882267',
		b'\r\nContent-Type: text/xml; charset=UTF-8',
		b'\r\nContent-Transfer-Encoding: 8bit',
		b'\r\nContent-ID: <rootpart@soapui.org>,'
		b'\r\n\r\n',
		b'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">',
		b'\t<soapenv:Body>',
		b'\t\t<Request>',
		b'\t\t\t<File>cid:109236228251</File>',
		b'\t\t\t<File>cid:219236228251</File>',
		b'\t\t\t<File>cid:329236228251</File>',
		b'\t\t</Request>',
		b'\t</soapenv:Body>'
		b'</soapenv:Envelope>',
		b'\r\n------=_Part_36_146605718.1713895882267',
		b'\r\nContent-Type: multipart/mixed; ',
		b'\r\n\tboundary="----=_Part_37_1983365806.1713895882270"; name=test.txt',
		b'\r\nContent-Transfer-Encoding: binary',
		b'\r\nContent-ID: <109236228251>',
		b'\r\nContent-Disposition: attachment; name="test.txt"; filename="test.txt"',
		b'\r\n\r\n------=_Part_37_1983365806.1713895882270',
		b'\r\nContent-ID: <109236228251>',
		b'\r\nContent-Disposition: attachment; name="test.txt"; filename="test.txt"',
		b'\r\n\r\nlorem ipsum dolor sit amet',
		b'\r\n------=_Part_37_1983365806.1713895882270',
		b'\r\nContent-ID: <219236228251>',
		b'\r\nContent-Disposition: attachment; name="test.xml"; filename="test.xml"',
		b'\r\n\r\n<test>lorem ipsum dolor sit amet</test>',
		b'\r\n------=_Part_37_1983365806.1713895882270',
		b'\r\nContent-ID: <329236228251>',
		b'\r\nContent-Disposition: attachment; name="test.zip"; filename="test.zip"',
		b'\r\n\r\nPK\x03\x04\n\x00\x00\x00\x00\x00o\xa6\x82X^\xab\x8f\xd8\'\x00\x00\x00\'',
		b'\x00\x00\x00\x08\x00\x00\x00test.xml<test>lorem ipsum dolor sit amet</test>PK',
		b'\x01\x02?\x00\n\x00\x00\x00\x00\x00o\xa6\x82X^\xab\x8f\xd8\'\x00\x00\x00\'\x00',
		b'\x00\x00\x08\x00$\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00test.xml',
		b'\n\x00 \x00\x00\x00\x00\x00\x01\x00\x18\x00P\xd2ec&\x85\xda\x01\x00\x00\x00\x00',
		b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00PK\x05\x06\x00\x00\x00\x00\x01',
		b'\x00\x01\x00Z\x00\x00\x00M\x00\x00\x00\x00\x00',
		b'\r\n------=_Part_37_1983365806.1713895882270--',
		b'\r\n\r\n------=_Part_36_146605718.1713895882267--\r\n'
	])
	return content, content_type
