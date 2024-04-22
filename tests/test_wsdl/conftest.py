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
from fastapi_xroad_soap.internal import utils, wsdl
from fastapi_xroad_soap.internal.soap import SoapAction
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.envelope import XroadHeader


__all__ = [
	"fixture_wsdl_generator",
	"fixture_ref_wsdl_file"
]


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


@pytest.fixture(name="ref_wsdl_file", scope="package")
def fixture_ref_wsdl_file() -> t.Callable:
	def closure(file_name: str) -> bytes:
		path = utils.search_upwards(file_name, __file__)
		file_data: bytes = utils.read_cached_file(path, binary=True)
		return file_data.replace(b'\r\n', b'\n').strip()
	return closure
