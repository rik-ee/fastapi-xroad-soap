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
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.soap import SoapAction
from fastapi_xroad_soap.internal.envelope import (
	XroadHeader, XroadService, XroadClient
)

__all__ = [
	"fixture_storage",
	"fixture_create_action",
	"fixture_xroad_header"
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
