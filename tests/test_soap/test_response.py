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
from fastapi_xroad_soap.internal.soap import SoapResponse
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.multipart import MultipartDecoder
from fastapi_xroad_soap.internal.elements.models import SwaRef, String
from fastapi_xroad_soap.internal import utils


__all__ = [
	"test_soap_response_simple",
	"test_soap_response_with_one_file",
	"test_soap_response_with_two_files"
]


def test_soap_response_simple():
	class SimpleResponse(MessageBody, tag="SimpleResponse"):
		text = String(tag="Text")

	obj = SimpleResponse(text="asdfg")
	resp = SoapResponse(obj)
	ct = resp.headers.get("content-type")
	assert ct.split(';')[0] == "text/xml"

	normalized = resp.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='yes'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<SimpleResponse>
					<Text>asdfg</Text>
				</SimpleResponse>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert normalized == expected


def test_soap_response_with_one_file():
	class FileResponse(MessageBody, tag="FileResponse"):
		file = SwaRef.Element(tag="File")

	obj = FileResponse(file=SwaRef.File(
		name="asdfg.txt",
		content=b"qwerty"
	))
	resp = SoapResponse(obj)
	ct = resp.headers.get("content-type")
	assert ct.split(';')[0] == "multipart/related"

	decoder = MultipartDecoder(resp.body, ct)
	envelope, file = decoder.parts

	content_ids, modified_xml = utils.extract_content_ids(
		envelope.content.decode(), remove_from_xml=True
	)
	assert len(content_ids) == 1
	assert content_ids[0] == file.content_id

	normalized = modified_xml.encode().replace(b'\r\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='yes'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<FileResponse>
					<File>cid:</File>
				</FileResponse>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert normalized == expected


def test_soap_response_with_two_files():
	class FilesResponse(MessageBody, tag="FilesResponse"):
		files: t.List[SwaRef.File] = SwaRef.Element(tag="Files")

	obj = FilesResponse(files=[
		SwaRef.File(name="asdfg.txt", content=b"qwerty"),
		SwaRef.File(name="zxcvb.zip", content=b"tyuiop")
	])
	resp = SoapResponse(obj)
	ct = resp.headers.get("content-type")
	assert ct.split(';')[0] == "multipart/related"

	decoder = MultipartDecoder(resp.body, ct)
	envelope, sub_parts = decoder.parts

	assert sub_parts.is_mixed_multipart is True
	nested_ct = sub_parts.headers.get("content-type")
	nested_decoder = MultipartDecoder(sub_parts.content, nested_ct)

	content_ids, modified_xml = utils.extract_content_ids(
		envelope.content.decode(), remove_from_xml=True
	)
	assert len(content_ids) == 2
	for part in nested_decoder.parts:
		assert part.is_mixed_multipart is False
		assert part.content_id in content_ids

	normalized = modified_xml.encode().replace(b'\r\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='yes'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<FilesResponse>
					<Files>cid:</Files>
					<Files>cid:</Files>
				</FilesResponse>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert normalized == expected
