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
import functools
from fastapi_xroad_soap.internal.base import BaseElementSpec
from fastapi_xroad_soap.internal.elements.models import SwaRefFile
from fastapi_xroad_soap.internal.constants import A8nType


@pytest.fixture(name="nsmap", scope="package")
def fixture_nsmap() -> t.Dict[str, str]:
	return {"pytest": "http://fastapi-xroad-soap.pytest"}


@pytest.fixture(name="a8n_type_tester", scope="function")
def fixture_a8n_type_tester() -> t.Callable[[BaseElementSpec], None]:
	def closure(spec: BaseElementSpec) -> None:
		spec_et = spec.element_type
		set_a8n = functools.partial(
			spec.set_a8n_type_from, attr='', cls_name=''
		)
		wrapper_types = [
			t.Optional, t.Union, t.List, t.Dict, t.Set, t.Tuple
		]
		base_types = [
			bool, str, int, float, list, dict, set, tuple, SwaRefFile
		]
		base_types.remove(spec_et)

		assert spec.a8n_type is None
		for wt in wrapper_types:
			with pytest.raises(TypeError):
				set_a8n(wt)
			with pytest.raises(TypeError):
				set_a8n(wt[None])
			for bt in base_types:
				with pytest.raises(TypeError):
					set_a8n(wt[spec_et, bt])
				with pytest.raises(TypeError):
					set_a8n(wt[bt])

		set_a8n(spec_et)
		assert spec.a8n_type == A8nType.MAND

		set_a8n(t.Optional[spec_et])
		assert spec.a8n_type == A8nType.OPT

		set_a8n(t.List[spec_et])
		assert spec.a8n_type == A8nType.LIST

		set_a8n(t.Union[spec_et, None])
		assert spec.a8n_type == A8nType.OPT

	return closure
