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
from fastapi_xroad_soap.internal.multipart import MultipartDecoder
from fastapi_xroad_soap.internal.multipart import errors


__all__ = [
	"test_multipart_decoder",
	"test_multipart_decoder_mixed",
	"test_multipart_decoder_error"
]


def test_multipart_decoder(multipart_data):
	content, content_type = multipart_data()
	decoder = MultipartDecoder(content, content_type)
	envelope, file = decoder.parts

	decoded = utils.linearize_xml(envelope.content.decode()).strip()
	expected = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">    
			<soapenv:Body>          
				<Request>                     
					<File>cid:783266853352</File>         
				</Request>    
			</soapenv:Body>
		</soapenv:Envelope>
	""").strip()
	assert decoded == expected
	assert file.content == b'lorem ipsum dolor sit amet'


def test_multipart_decoder_mixed(mixed_multipart_data):
	content, content_type = mixed_multipart_data
	decoder = MultipartDecoder(content, content_type)
	envelope, mixed_parts = decoder.parts

	decoded = utils.linearize_xml(envelope.content.decode()).strip()
	expected = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">    
			<soapenv:Body>          
				<Request>                     
					<File>cid:109236228251</File>
					<File>cid:219236228251</File>
					<File>cid:329236228251</File>
				</Request>    
			</soapenv:Body>
		</soapenv:Envelope>
	""").strip()
	assert decoded == expected

	assert mixed_parts.is_mixed_multipart is True
	content_type = mixed_parts.headers.get('content-type')
	mixed_decoder = MultipartDecoder(mixed_parts.content, content_type)

	content_ids = ["cid:109236228251", "cid:219236228251", "cid:329236228251"]
	for part in mixed_decoder.parts:
		assert part.content_id in content_ids


def test_multipart_decoder_error(multipart_data):
	with pytest.raises(errors.MultipartBoundaryError):
		MultipartDecoder(b"content", "text/plain")

	content, content_type = multipart_data()
	with pytest.raises(errors.InvalidSeparatorError):
		bad_content = content.replace(b'\r\n\r\n', b'')
		MultipartDecoder(bad_content, content_type)

	with pytest.raises(errors.MissingContentIDError):
		bad_content = content.replace(b'\r\nContent-ID: <783266853352>', b'')
		MultipartDecoder(bad_content, content_type)
