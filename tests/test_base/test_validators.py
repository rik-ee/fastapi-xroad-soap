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
import functools
import typing as t
from fastapi_xroad_soap.internal.base import validators as vld
from fastapi_xroad_soap.internal.constants import A8nType
from .conftest import CustomModelObject, CustomModelSpec


__all__ = ["test_validate_opt_mand_a8n"]


def test_validate_opt_mand_a8n():
	func = functools.partial(vld.validate_opt_mand_a8n, "attr")
	spec = CustomModelSpec()

	spec.a8n_type = A8nType.LIST
	func([], spec)

	for a8n_type in [A8nType.MAND, A8nType.OPT]:
		spec.a8n_type = a8n_type
		with pytest.raises(ValueError):
			func([1, 2], spec)

	spec.a8n_type = A8nType.MAND
	with pytest.raises(ValueError):
		func([], spec)


def test_validate_list_items():
	func = functools.partial(vld.validate_list_items, "attr")
	spec = CustomModelSpec()

	with pytest.raises(ValueError):
		func(t.cast(list, str), spec)

	spec.min_occurs = 1
	with pytest.raises(ValueError):
		func([], spec)

	spec.max_occurs = 2
	with pytest.raises(ValueError):
		func([1, 2, 3], spec)

	with pytest.raises(ValueError):
		func([1, 2], spec)

	obj = CustomModelObject(text="asdfg")
	func([obj], spec)


def test_validate_a8n_args():
	func = functools.partial(
		vld.validate_a8n_args,
		cls_name="cls_name",
		attr="attr"
	)
	for a8n in [t.Optional, t.Union, t.List, list]:
		with pytest.raises(TypeError):
			func(a8n=a8n, expected_type=str)

	for a8n in [t.Optional[int], t.Union[int, None], t.List[int]]:
		with pytest.raises(TypeError):
			func(a8n=a8n, expected_type=str)

	for a8n in [t.Optional[str], t.Union[str, None], t.List[str]]:
		func(a8n=a8n, expected_type=str)
