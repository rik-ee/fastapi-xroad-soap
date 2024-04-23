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
	"fixture_xroad_header"
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
