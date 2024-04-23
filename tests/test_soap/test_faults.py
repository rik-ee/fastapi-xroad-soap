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
from pydantic import validate_call, ValidationError
from pydantic_xml import element
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.soap import faults as f
from fastapi_xroad_soap.internal.base import MessageBody


__all__ = ["test_soap_fault"]


def test_soap_fault():
	fault = f.SoapFault()
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Bad Request</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_soap_fault_details():
	class ExtraDetail(MessageBody, tag="ExtraDetail"):
		text: str = element(tag="Text")

	fault = f.SoapFault(detail=ExtraDetail(text="asdfg"))
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Bad Request</faultstring>
					<detail>
						<Text>asdfg</Text>
					</detail>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_client_fault():
	fault = f.ClientFault("asdfg")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>asdfg</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_server_fault():
	fault = f.ServerFault("qwerty")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Server</faultcode>
					<faultstring>qwerty</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 500


def test_invalid_method_fault():
	fault = f.InvalidMethodFault("GET")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Service does not support GET method for SOAP action requests</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_invalid_action_fault():
	fault = f.InvalidActionFault("ExplodeServer")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Service does not support SOAP action: ExplodeServer</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_missing_action_fault():
	fault = f.MissingActionFault()
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>SOAP action HTTP header is missing</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_missing_body_fault():
	fault = f.MissingBodyFault("AwesomeAction")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Body element missing from envelope for SOAP action: AwesomeAction</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_missing_header_fault():
	fault = f.MissingHeaderFault("AwesomeAction")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>X-Road header element missing from envelope for SOAP action: AwesomeAction</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_missing_cid_fault():
	fault = f.MissingCIDFault("cid:123456789")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Content-ID missing from envelope: cid:123456789</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_duplicate_cid_fault():
	fault = f.DuplicateCIDFault("cid:123456789")
	body = fault.response.body.replace(b'\n', b'')
	expected = utils.linearize_xml("""
		<?xml version='1.0' encoding='utf-8' standalone='no'?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
			<soapenv:Body>
				<soapenv:Fault>
					<faultcode>Client</faultcode>
					<faultstring>Duplicate Content-ID not allowed: 123456789</faultstring>
				</soapenv:Fault>
			</soapenv:Body>
		</soapenv:Envelope>
	""")
	assert body == expected
	assert fault.response.status_code == 400


def test_validation_fault():
	@validate_call
	def inner(_: int) -> None:
		pass  # Shut Up SonarCloud

	try:
		inner(t.cast(int, "asdfg"))
	except ValidationError as ex:
		fault = f.ValidationFault(ex)
		body = fault.response.body.replace(b'\n', b'')
		expected = utils.linearize_xml("""
			<?xml version='1.0' encoding='utf-8' standalone='no'?>
			<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
				<soapenv:Body>
					<soapenv:Fault>
						<faultcode>Client</faultcode>
						<faultstring>1 validation error in SOAP envelope</faultstring>
						<detail>
							<validationError>
								<location>Unknown</location>
								<reason>Input should be a valid integer, unable to parse string as an integer</reason>
								<inputValue>Unknown</inputValue>
							</validationError>
						</detail>
					</soapenv:Fault>
				</soapenv:Body>
			</soapenv:Envelope>
		""")
		assert body == expected
		assert fault.response.status_code == 400
