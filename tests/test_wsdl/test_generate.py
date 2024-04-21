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
from fastapi_xroad_soap.internal import utils, wsdl
from fastapi_xroad_soap.internal.soap import SoapAction
from fastapi_xroad_soap.internal.envelope import XroadHeader
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage


__all__ = ["test_basic_wsdl_generation"]


def test_basic_wsdl_generation():
	path = utils.search_upwards(
		for_path="without_action_types.wsdl",
		from_path=__file__
	)
	file_data: bytes = utils.read_cached_file(path, binary=True)
	file_data = file_data.replace(b'\r\n', b'\n').strip()
	wsdl_data = wsdl.generate(
		name="SoapService",
		tns="https://example.org",
		actions=dict(
			pytestAction=SoapAction(
				name="pytestAction",
				description=None,
				handler=lambda: None,
				body_type=None,
				body_index=0,
				header_type=XroadHeader,
				header_index=1,
				return_type=None,
				storage=GlobalWeakStorage()
			)
		)
	).strip()
	assert file_data == wsdl_data
