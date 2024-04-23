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
from fastapi_xroad_soap.internal import wsdl
from fastapi_xroad_soap.internal.soap import SoapAction
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.envelope import XroadHeader


__all__ = ["fixture_wsdl_generator"]


@pytest.fixture(name="wsdl_generator", scope="package")
def fixture_wsdl_generator() -> t.Callable:
	def closure(body_type: t.Union[t.Type[MessageBody], None]) -> bytes:
		return wsdl.generate(
			name="SoapService",
			tns="https://example.org",
			actions=dict(
				pytestAction=SoapAction(
					name="pytestAction",
					description=None,
					handler=lambda: None,
					body_type=body_type,
					body_index=0,
					header_type=XroadHeader,
					header_index=1,
					return_type=None,
					storage=GlobalWeakStorage()
				)
			)
		).strip()
	return closure
