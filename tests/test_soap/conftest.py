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
from fastapi.testclient import TestClient
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.soap import SoapAction
from fastapi_xroad_soap.internal.soap import SoapService
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.envelope import XroadHeader
from fastapi_xroad_soap.internal.elements.models import Integer, SwaRef


__all__ = [
	"fixture_storage",
	"fixture_create_action",
	"fixture_create_client",
	"fixture_create_multipart_client",
	"fixture_create_mixed_multipart_client"
]


@pytest.fixture(name="gws", scope="function")
def fixture_storage():
	return GlobalWeakStorage.new_subclass()


@pytest.fixture(name="create_action", scope="function")
def fixture_create_action(gws) -> t.Callable:
	def closure(
			name: str = "pytestAction",
			body_type: t.Type[MessageBody] = None,
			header_type: t.Type[XroadHeader] = None,
			return_type: t.Type[MessageBody] = None
	) -> SoapAction:
		return SoapAction(
			name=name,
			description=None,
			handler=lambda: None,
			body_type=body_type,
			body_index=None if body_type is None else 0,
			header_type=header_type,
			header_index=None if header_type is None else 1,
			return_type=return_type,
			storage=gws()
		)

	return closure


@pytest.fixture(name="create_client", scope="function")
def fixture_create_client() -> t.Callable:
	def closure(fault_callback: t.Callable = None) -> TestClient:
		soap = SoapService(fault_callback=fault_callback)

		class PytestRequest(MessageBody, tag="Request"):
			number = Integer(tag="Number")

		class PytestResponse(MessageBody, tag="Response"):
			number = Integer(tag="Number")

		@soap.action("PytestSync")
		def handler(body: PytestRequest) -> PytestResponse:
			return PytestResponse(number=body.number)

		@soap.action("PytestAsync")
		async def handler(body: PytestRequest) -> PytestResponse:
			return PytestResponse(number=body.number)

		return TestClient(soap)

	return closure


@pytest.fixture(name="create_multipart_client", scope="function")
def fixture_create_multipart_client() -> t.Callable:
	def closure() -> TestClient:
		soap = SoapService()

		class MultipartModel(MessageBody, tag="Request"):
			file: SwaRef.File = SwaRef.Element(tag="File")

		@soap.action("MultipartPytest")
		def handler(body: MultipartModel) -> MultipartModel:
			assert isinstance(body.file, SwaRef.File)
			return MultipartModel(file=body.file)

		return TestClient(soap)
	return closure


@pytest.fixture(name="create_mixed_multipart_client", scope="function")
def fixture_create_mixed_multipart_client() -> t.Callable:
	def closure() -> TestClient:
		soap = SoapService()

		class MixedMultipartModel(MessageBody, tag="Request"):
			files: t.List[SwaRef.File] = SwaRef.Element(tag="File")

		@soap.action("MixedMultipartPytest")
		def handler(body: MixedMultipartModel) -> MixedMultipartModel:
			assert isinstance(body.files, list)
			for item in body.files:
				assert isinstance(item, SwaRef.File)
			return MixedMultipartModel(files=body.files)

		return TestClient(soap)
	return closure
