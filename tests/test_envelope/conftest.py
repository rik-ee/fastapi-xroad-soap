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
from fastapi_xroad_soap.internal.envelope import (
	XroadService, XroadClient, XroadHeader
)


__all__ = ["fixture_header"]


@pytest.fixture(name="header", scope="function")
def fixture_header():
	service = XroadService(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code",
		service_code="service_code",
		service_version="service_version"
	)
	client = XroadClient(
		xroad_instance="xroad_instance",
		member_class="member_class",
		member_code="member_code",
		subsystem_code="subsystem_code"
	)
	return XroadHeader(
		user_id="user_id",
		proto_ver="proto_ver",
		id="id",
		service=service,
		client=client
	)
