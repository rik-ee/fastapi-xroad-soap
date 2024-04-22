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
from enum import Enum
from pydantic import AnyUrl
from pydantic_xml import model
from datetime import date, time, datetime
from fastapi_xroad_soap.utils import GlobalWeakStorage
from fastapi_xroad_soap.internal.base import BaseElementSpec
from fastapi_xroad_soap.internal.constants import A8nType
from fastapi_xroad_soap.internal.elements import NumericTypeSpec, StringTypeSpec
from fastapi_xroad_soap.internal.elements.models import (
	SwaRefFile, SwaRefInternal, SwaRefSpec
)


__all__ = [
	"fixture_storage",
	"fixture_spec_tester",
	"fixture_wsdl_type_name_tester",
	"fixture_a8n_type_tester",
	"fixture_process_data_init",
	"fixture_data_init_tester",
	"fixture_pattern_tester",
	"fixture_min_max_value_tester",
	"fixture_total_digits_tester",
	"fixture_min_max_length_tester",
	"fixture_length_tester",
	"fixture_whitespace_tester",
	"fixture_enum_tester"
]


_BaseSpec = t.Type[BaseElementSpec]
_SpecType = t.Union[_BaseSpec, t.Type[NumericTypeSpec], t.Type[StringTypeSpec]]
_Spec = t.Union[BaseElementSpec, NumericTypeSpec, StringTypeSpec]


@pytest.fixture(name="gws", scope="function")
def fixture_storage():
	return GlobalWeakStorage.new_subclass()


@pytest.fixture(name="spec_tester", scope="package")
def fixture_spec_tester(wsdl_type_name_tester, a8n_type_tester) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			spec_type: _SpecType,
			spec_base_type: _BaseSpec,
			element_type: t.Type[t.Any],
			wsdl_type_name: str,
			default_wsdl_type_name: t.Union[str, None]
	) -> None:
		ns, tag = "pytest", "PytestElement"
		nsmap = {"pytest": "http://fastapi-xroad-soap.pytest"}
		spec: _Spec = spec_creator(
			tag=tag,
			ns=ns,
			nsmap=nsmap,
			min_occurs=123,
			max_occurs=456
		)
		assert isinstance(spec, spec_type)
		assert issubclass(spec_type, spec_base_type)

		assert spec.tag == tag
		assert spec.ns == ns
		assert spec.nsmap == nsmap
		assert spec.min_occurs == 123
		assert spec.max_occurs == 456
		assert spec.element_type == element_type
		if isinstance(spec, SwaRefSpec):
			assert spec.internal_type == SwaRefInternal
		else:
			assert spec.internal_type is None
		assert spec.has_constraints is False

		wsdl_type_name_tester(spec, wsdl_type_name)
		if isinstance(spec, (NumericTypeSpec, StringTypeSpec)):
			assert spec.default_wsdl_type_name == default_wsdl_type_name
		else:
			with pytest.raises(NotImplementedError):
				_ = spec.default_wsdl_type_name

		element = spec.get_element('')
		arg_type = spec.internal_type or element_type
		assert spec.get_element_a8n() == t.List[arg_type]
		assert isinstance(element, model.XmlEntityInfo)
		assert element.path == tag
		assert element.ns == ns
		assert element.nsmap == nsmap
		assert element.default_factory == list

		a8n_type_tester(spec)

	return closure


@pytest.fixture(name="wsdl_type_name_tester", scope="package")
def fixture_wsdl_type_name_tester() -> t.Callable:
	def closure(spec: BaseElementSpec, wsdl_type_name: t.Optional[str] = None) -> None:
		if not spec.has_constraints:
			for value in [True, False]:
				assert spec.wsdl_type_name(with_tns=value) == wsdl_type_name
		else:
			cap_name = spec.default_wsdl_type_name.capitalize()
			partial_name = f"Custom{cap_name}"

			name = spec.wsdl_type_name(with_tns=True)
			assert name.startswith("tns:" + partial_name)

			name = spec.wsdl_type_name(with_tns=False)
			assert name.startswith(partial_name)

	return closure


@pytest.fixture(name="a8n_type_tester", scope="package")
def fixture_a8n_type_tester() -> t.Callable:
	def closure(spec: BaseElementSpec) -> None:
		set_a8n = functools.partial(
			spec.set_a8n_type_from, attr='', cls_name=''
		)
		wrapper_types = [
			t.Optional, t.Union, t.List, t.Dict, t.Set, t.Tuple
		]
		base_types = [
			bool, str, int, float, list, dict, set, tuple,
			date, time, datetime, SwaRefFile, AnyUrl
		]
		spec_et = spec.element_type
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


@pytest.fixture(name="process_data_init", scope="package")
def fixture_process_data_init(wsdl_type_name_tester) -> t.Callable:
	def closure(
			spec: _Spec,
			good_values: t.List[t.Any],
			bad_values: t.List[t.Any]
	) -> None:
		errors = t.cast(t.Type[Exception], (TypeError, ValueError))
		for gv in good_values:
			assert spec.init_instantiated_data([gv]) == [gv]
			assert spec.init_deserialized_data([gv]) == [gv]
		for bv in bad_values:
			with pytest.raises(errors):
				spec.init_instantiated_data([bv])
			with pytest.raises(errors):
				spec.init_deserialized_data([bv])
		if spec.has_constraints:
			wsdl_type_name_tester(spec)

	return closure


@pytest.fixture(name="data_init_tester", scope="package")
def fixture_data_init_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			good_values: t.List[t.Any],
			bad_values: t.List[t.Any]
	) -> None:
		spec: _Spec = spec_creator()
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="pattern_tester", scope="package")
def fixture_pattern_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			good_values: t.List[t.Any],
			bad_values: t.List[t.Any],
			pattern: str
	) -> None:
		spec: _Spec = spec_creator(pattern=pattern)
		assert spec.pattern == pattern
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="min_max_value_tester", scope="package")
def fixture_min_max_value_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			min_value: t.Any,
			max_value: t.Any,
			less_value: t.Any,
			more_value: t.Any
	) -> None:
		spec: _Spec = spec_creator(
			min_value=min_value,
			max_value=max_value
		)
		assert spec.min_value == min_value
		assert spec.max_value == max_value

		good_values = [min_value, max_value]
		bad_values = [less_value, more_value]
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="total_digits_tester", scope="package")
def fixture_total_digits_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			good_values: t.List[t.Any],
			bad_values: t.List[t.Any],
			total_digits: str
	) -> None:
		spec: _Spec = spec_creator(total_digits=total_digits)
		assert spec.total_digits == total_digits
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="min_max_length_tester", scope="package")
def fixture_min_max_length_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			good_values: t.List[t.Any],
			bad_values: t.List[t],
			min_length: int,
			max_length: int
	) -> None:
		spec: _Spec = spec_creator(
			min_length=min_length,
			max_length=max_length
		)
		assert spec.min_length == min_length
		assert spec.max_length == max_length
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="length_tester", scope="package")
def fixture_length_tester(process_data_init) -> t.Callable:
	def closure(
			spec_creator: t.Type,
			good_values: t.List[t.Any],
			bad_values: t.List[t],
			length: int
	) -> None:
		spec: _Spec = spec_creator(length=length)
		assert spec.length == length
		process_data_init(spec, good_values, bad_values)

	return closure


@pytest.fixture(name="whitespace_tester", scope="package")
def fixture_whitespace_tester() -> t.Callable:
	def closure(
			spec_creator: t.Type,
			raw_string: str,
			replace_string: str,
			collapse_string: str
	) -> None:
		spec: _Spec = spec_creator(whitespace="replace")
		assert spec.whitespace == "replace"

		assert spec.init_instantiated_data([raw_string]) == [replace_string]
		assert spec.init_deserialized_data([raw_string]) == [replace_string]

		spec: _Spec = spec_creator(whitespace="collapse")
		assert spec.whitespace == "collapse"

		assert spec.init_instantiated_data([raw_string]) == [collapse_string]
		assert spec.init_deserialized_data([raw_string]) == [collapse_string]

	return closure


@pytest.fixture(name="enum_tester", scope="package")
def fixture_enum_tester() -> t.Callable:
	def closure(
			spec_creator: t.Type,
			enum_values: t.Tuple[t.Any, t.Any, t.Any],
			non_enum_value: t.Any,
			bad_type_values: t.List
	) -> None:
		class GoodChoice(Enum):
			FIRST = enum_values[0]
			SECOND = enum_values[1]
			THIRD = enum_values[2]

		spec: _Spec = spec_creator(enumerations=GoodChoice)
		assert spec.enumerations == GoodChoice

		choices = [c.value for c in GoodChoice]
		assert spec.init_instantiated_data(choices) == choices
		assert spec.init_deserialized_data(choices) == choices

		with pytest.raises(ValueError):
			spec.init_instantiated_data([non_enum_value])
		with pytest.raises(ValueError):
			spec.init_deserialized_data([non_enum_value])

		for bad_value in bad_type_values:
			class BadChoice(Enum):
				CHOICE = bad_value

			with pytest.raises(TypeError):
				spec_creator(enumerations=BadChoice)

	return closure
