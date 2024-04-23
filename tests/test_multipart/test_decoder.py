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
from fastapi_xroad_soap.internal.multipart import (
	MultipartDecoder, NonMultipartError
)


__all__ = ["test_multipart_decoder"]


def test_multipart_decoder():
	with pytest.raises(NonMultipartError):
		MultipartDecoder(b"content", "text/plain")

	c_type = '; '.join([
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
		b'\t\t<SubmitDataRequest>',
		b'\t\t\t<DataFile>cid:783266853352</DataFile>',
		b'\t\t</SubmitDataRequest>',
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

	decoder = MultipartDecoder(content, c_type)
	envelope, file = decoder.parts

	decoded = utils.linearize_xml(envelope.content.decode()).strip()
	expected = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">    
			<soapenv:Body>          
				<SubmitDataRequest>                     
					<DataFile>cid:783266853352</DataFile>         
				</SubmitDataRequest>    
			</soapenv:Body>
		</soapenv:Envelope>
	""").strip()
	assert decoded == expected

	assert file.name == 'test.txt'
	assert file.content == b'lorem ipsum dolor sit amet'
