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
from enum import Enum
from fastapi_xroad_soap.internal.constants import A8nType


__all__ = ["test_a8n_type_enum"]


def test_a8n_type_enum():
	assert issubclass(A8nType, Enum)

	assert hasattr(A8nType, "LIST")
	assert hasattr(A8nType, "OPT")
	assert hasattr(A8nType, "MAND")
	assert hasattr(A8nType, "ABSENT")

	assert A8nType.LIST.value == "list"
	assert A8nType.OPT.value == "optional"
	assert A8nType.MAND.value == "mandatory"
	assert A8nType.ABSENT.value == "absent"
