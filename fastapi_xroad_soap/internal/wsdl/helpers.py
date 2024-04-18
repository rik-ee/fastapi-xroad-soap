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
import typing as t
from ..soap.action import SoapAction
from ..elements import NumericTypeSpec
from ..elements import StringTypeSpec
from ..base import NestedModels, BaseElementSpec
from . import models as mod


__all__ = ["gather_all_types"]


AllTypes = t.Tuple[t.List[mod.ComplexType], t.List[mod.SimpleType]]


def gather_all_types(actions: t.Dict[str, SoapAction]) -> AllTypes:
	simple_types: t.Dict[str, mod.SimpleType] = {}
	complex_types: t.List[mod.ComplexType] = []
	models = _gather_models(actions)

	for model, children in models:
		elements = []
		for child in children:
			elements.append(mod.Element(
				name=child.__name__,
				type=f"tns:{child.__name__}"
			))
		for spec in model.model_specs().values():
			_add_simple_type(spec, simple_types)
			elements.append(mod.Element(
				name=spec.tag,
				type=spec.wsdl_type_name(with_tns=True)
			))
		complex_types.append(mod.ComplexType(
			name=model.__name__,
			sequence=mod.Sequence(
				elements=elements
			)
		))
	return complex_types, list(simple_types.values())


def _gather_models(actions: t.Dict[str, SoapAction]) -> NestedModels:
	models = []
	for action in actions.values():
		for model in [action.body_type, action.return_type]:
			nested = model.nested_models()
			models.extend(nested)
	return models


def _add_simple_type(spec: BaseElementSpec, simple_types: t.Dict[str, mod.SimpleType]) -> None:
	if spec.has_constraints:
		func = (
			_create_string_simple_type if
			isinstance(spec, StringTypeSpec)
			else _create_numeric_simple_type
		)
		st: mod.SimpleType = func(spec)
		if st.name not in simple_types:
			simple_types[st.name] = st


def _create_string_simple_type(spec: StringTypeSpec) -> mod.SimpleType:
	return mod.SimpleType(
		name=spec.wsdl_type_name(),
		restriction=mod.StringTypeRestriction(
			base=spec.default_wsdl_type_name,
			length=(
				None if spec.length is None else
				mod.Length(value=str(spec.length))
			),
			min_length=(
				None if spec.min_length is None or spec.length is not None else
				mod.MinLength(value=str(spec.min_length))
			),
			max_length=(
				None if spec.max_length is None or spec.length is not None else
				mod.MaxLength(value=str(spec.max_length))
			),
			whitespace=(
				None if spec.whitespace == "preserve" else
				mod.WhiteSpace(value=spec.whitespace)
			),
			pattern=(
				None if spec.pattern is None else
				mod.RegexPattern(value=spec.pattern)
			),
			enumerations=(
				None if spec.enumerations is None else [
					mod.Enumeration(value=str(e.value))
					for e in spec.enumerations
				]
			)
		)
	)


def _create_numeric_simple_type(spec: NumericTypeSpec) -> mod.SimpleType:
	return mod.SimpleType(
		name=spec.wsdl_type_name(),
		restriction=mod.NumericTypeRestriction(
			base=spec.default_wsdl_type_name,
			min_inclusive=(
				None if spec.min_value is None else
				mod.MinInclusive(value=str(spec.min_value))
			),
			max_inclusive=(
				None if spec.max_value is None else
				mod.MaxInclusive(value=str(spec.max_value))
			),
			total_digits=(
				None if spec.total_digits is None else
				mod.TotalDigits(value=str(spec.total_digits))
			),
			pattern=(
				None if spec.pattern is None else
				mod.RegexPattern(value=spec.pattern)
			),
			enumerations=(
				None if spec.enumerations is None else [
					mod.Enumeration(value=str(e.value))
					for e in spec.enumerations
				]
			)
		)
	)