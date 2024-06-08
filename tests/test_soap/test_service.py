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
from fastapi import Request, Response
from pydantic import ValidationError
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.soap import SoapService
from fastapi.testclient import TestClient


__all__ = [
	"test_soap_service_attributes",
	"test_soap_service_invalid_action",
	"test_soap_service_simple_request",
	"test_soap_service_multipart_request",
	"test_soap_service_request_errors",
	"test_soap_service_request_validation_error",
	"test_soap_service_garbage_content",
	"test_soap_service_invalid_multipart",
	"test_soap_service_fault_callback",
	"test_soap_service_wsdl",
	"test_soap_service_wsdl_gen",
	"test_soap_service_wsdl_override"
]


def test_soap_service_attributes():
	soap = SoapService()
	assert hasattr(soap, "add_action")
	assert hasattr(soap, "action")
	assert hasattr(soap, "regenerate_wsdl")

	assert callable(soap.add_action)
	assert callable(soap.action)
	assert callable(soap.regenerate_wsdl)


def test_soap_service_invalid_action():
	soap = SoapService()

	for bad_len in [4, 31]:
		name = 'x' * bad_len
		decorator = soap.action(name)
		with pytest.raises(ValidationError):
			decorator(lambda: None)
		with pytest.raises(ValidationError):
			soap.add_action(name, lambda: None)

	soap.add_action("asdfg", lambda: None)
	with pytest.raises(ValueError):
		soap.add_action("asdfg", lambda: None)


def test_soap_service_simple_request(create_client):
	client: TestClient = create_client()

	request_content = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:extra="extra">
			<soapenv:Body>
				<extra:Request>
					<Number>1234</Number>
				</extra:Request>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	expected_response = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='yes'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<Response>
					<Number>1234</Number>
				</Response>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	url = "https://example.com/service"
	action_variants = [
		"PytestSync",
		f"{url}/PytestSync",
		f"{url}#PytestSync",
		"PytestAsync",
		f"{url}/PytestAsync",
		f"{url}#PytestAsync"
	]
	for action in action_variants:
		headers = {"SOAPAction": action, "Content-Type": "text/xml"}
		resp = client.post(url="/service", content=request_content, headers=headers)

		assert resp.status_code == 200
		response_content = resp.content.replace(b'\n', b'')
		assert response_content == expected_response


def test_soap_service_multipart_request(create_multipart_client, multipart_data):
	client: TestClient = create_multipart_client()

	for transfer_encoding in ["base64", "quoted-printable", "binary", "7bit"]:
		content, content_type = multipart_data(transfer_encoding)

		headers = {"SOAPAction": "MultipartPytest", "Content-Type": content_type}
		resp = client.post(url="/service", content=content, headers=headers)

		assert resp.status_code == 200
		assert "multipart/related" in resp.headers["Content-Type"]


def test_soap_service_mixed_multipart_request(create_mixed_multipart_client, mixed_multipart_data):
	client: TestClient = create_mixed_multipart_client()
	content, content_type = mixed_multipart_data

	headers = {"SOAPAction": "MixedMultipartPytest", "Content-Type": content_type}
	resp = client.post(url="/service", content=content, headers=headers)

	assert resp.status_code == 200
	assert "multipart/related" in resp.headers["Content-Type"]


def test_soap_multipart_errors(create_mixed_multipart_client, mixed_multipart_data):
	client: TestClient = create_mixed_multipart_client()
	content, content_type = mixed_multipart_data
	headers = {"SOAPAction": "MixedMultipartPytest", "Content-Type": content_type}

	bad_content = content.replace(b'<329236228251>', b'<219236228251>')
	resp = client.post(url="/service", content=bad_content, headers=headers)

	assert resp.status_code == 400
	err_msg = b"Duplicate Content-ID not allowed: 219236228251"
	assert err_msg in resp.content

	bad_content = content.replace(b'cid:329236228251', b'cid:219236228251')
	resp = client.post(url="/service", content=bad_content, headers=headers)

	assert resp.status_code == 400
	err_msg = b"Duplicate Content-ID not allowed: 219236228251"
	assert err_msg in resp.content

	bad_content = content.replace(b'cid:329236228251', b'cid:00000000000')
	resp = client.post(url="/service", content=bad_content, headers=headers)

	assert resp.status_code == 400
	err_msg = b"Content-ID missing from envelope: cid:329236228251"
	assert err_msg in resp.content


def test_soap_service_request_errors(create_client):
	client: TestClient = create_client()

	resp = client.put(url="/service")
	assert resp.status_code == 400
	err_msg = b"Service does not support PUT method for SOAP action requests"
	assert err_msg in resp.content

	resp = client.post(url="/service")
	assert resp.status_code == 400
	err_msg = b"SOAPAction HTTP header is missing"
	assert err_msg in resp.content

	resp = client.post(url="/service", headers={"SOAPAction": "KABOOM"})
	assert resp.status_code == 400
	err_msg = b"Service does not support SOAP action: KABOOM"
	assert err_msg in resp.content

	resp = client.post(url="/service", headers={"SOAPAction": "PytestSync"})
	assert resp.status_code == 400
	err_msg = b"Invalid content type: None"
	assert err_msg in resp.content

	resp = client.post(url="/service", headers={
		"SOAPAction": "PytestSync",
		"Content-Type": "text/kaboom"
	})
	assert resp.status_code == 400
	err_msg = b"Invalid content type: text/kaboom"
	assert err_msg in resp.content


def test_soap_service_request_validation_error(create_client):
	client: TestClient = create_client()
	request_content = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<Request>
					<Number>asdfg</Number>
				</Request>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	resp = client.post(
		url="/service",
		content=request_content,
		headers={
			"SOAPAction": "PytestSync",
			"Content-Type": "text/xml"
		}
	)
	assert resp.status_code == 400
	err_msg = b"Input should be a valid integer, unable to parse string as an integer"
	assert err_msg in resp.content


def test_soap_service_invalid_nsmap(create_client):
	client: TestClient = create_client()
	request_content = utils.linearize_xml("""
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:extra="extra">
			<soapenv:Body>
				<Request>
					<Number>1234</Number>
				</Request>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	resp = client.post(
		url="/service",
		content=request_content,
		headers={
			"SOAPAction": "PytestSync",
			"Content-Type": "text/xml"
		}
	)
	assert resp.status_code == 400
	err_msg = b"<location>Body.content</location><reason>Field required</reason>"
	assert err_msg in resp.content


def test_soap_service_garbage_content(create_client):
	client: TestClient = create_client()

	resp = client.post(
		url="/service",
		content=b"garbage",
		headers={
			"SOAPAction": "PytestSync",
			"Content-Type": "text/xml"
		}
	)
	assert resp.status_code == 400
	err_msg = b"Unexpected envelope structure"
	assert err_msg in resp.content


def test_soap_service_invalid_multipart(create_client):
	client: TestClient = create_client()

	resp = client.post(
		url="/service",
		content=b"garbage",
		headers={
			"SOAPAction": "PytestSync",
			"Content-Type": "multipart/related"
		}
	)
	assert resp.status_code == 400
	err_msg = b"Unable to locate multipart boundary in Content-Type header"
	assert err_msg in resp.content


def test_soap_service_fault_callback(create_client):
	container = []

	def fault_callback(body: bytes, headers: dict, ex: Exception):
		assert isinstance(body, bytes) and len(body) == 0
		assert headers.get("SOAPAction") == "KABOOM"
		assert isinstance(ex, Exception)
		container.append(True)

	client: TestClient = create_client(fault_callback)
	client.post(url="/service", headers={"SOAPAction": "KABOOM"})
	assert len(container) == 1 and True in container


def test_soap_service_wsdl(read_wsdl_file):
	soap = SoapService()
	wsdl_resp = getattr(soap, "_wsdl_response")
	assert wsdl_resp is None

	client = TestClient(soap)
	response = client.get("/service?wsdl")
	assert response.status_code == 200

	wsdl_resp = getattr(soap, "_wsdl_response")
	assert isinstance(wsdl_resp, Response)

	file_data = read_wsdl_file("without_actions.wsdl")
	assert response.content.strip() == file_data
	soap.regenerate_wsdl(force=False)


def test_soap_service_wsdl_gen(read_wsdl_file):
	soap = SoapService()
	soap.regenerate_wsdl(force=False)

	wsdl_resp = getattr(soap, "_wsdl_response")
	assert isinstance(wsdl_resp, Response)

	client = TestClient(soap)
	response = client.get("/service?wsdl")
	assert response.status_code == 200

	file_data = read_wsdl_file("without_actions.wsdl")
	assert response.content.strip() == file_data


def test_soap_service_wsdl_override():
	path_str = "wsdl_files/without_actions.wsdl"
	wsdl_path = utils.search_upwards(path_str, __file__)

	soap = SoapService(wsdl_override=wsdl_path)
	wsdl_resp = getattr(soap, "_wsdl_response")
	assert isinstance(wsdl_resp, Response)

	with pytest.raises(RuntimeError):
		soap.regenerate_wsdl(force=False)
	soap.regenerate_wsdl(force=True)


def test_soap_service_not_found():
	soap = SoapService(path="/service")
	client = TestClient(soap)
	response = client.get("/service_not_found?wsdl")
	assert response.status_code == 404
