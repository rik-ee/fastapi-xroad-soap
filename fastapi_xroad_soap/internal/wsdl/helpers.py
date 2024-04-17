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
from .models import *


__all__ = [
	"gather_all_types",
	"create_string_simple_type",
	"create_numeric_simple_type"
]


def _gather_models(actions: t.Dict[str, SoapAction]) -> NestedModels:
	models = []
	for action in actions.values():
		for model in [action.body_type, action.return_type]:
			nested = model.nested_models()
			models.extend(nested)
	return models


def _add_simple_type(spec: BaseElementSpec, simple_types: t.Dict[str, SimpleType]) -> None:
	if spec.has_constraints:
		func = (
			create_string_simple_type if
			isinstance(spec, StringTypeSpec)
			else create_numeric_simple_type
		)
		st: SimpleType = func(spec)
		if st.name not in simple_types:
			simple_types[st.name] = st


def gather_all_types(actions: t.Dict[str, SoapAction]) -> t.Tuple[t.List[ComplexType], t.List[SimpleType]]:
	simple_types: t.Dict[str, SimpleType] = {}
	complex_types: t.List[ComplexType] = []
	models = _gather_models(actions)

	for model, children in models:
		elements = []
		for child in children:
			elements.append(Element(
				name=child.__name__,
				type=f"tns:{child.__name__}"
			))
		for spec in model.model_specs().values():
			_add_simple_type(spec, simple_types)
			elements.append(Element(
				name=spec.tag,
				type=spec.wsdl_type_name
			))
		complex_types.append(ComplexType(
			name=model.__name__,
			sequence=Sequence(
				elements=elements
			)
		))
	return complex_types, list(simple_types.values())


def create_string_simple_type(spec: StringTypeSpec) -> SimpleType:
	return SimpleType(
		name=spec.wsdl_type_name,
		restriction=StringTypeRestriction(
			base=spec.default_wsdl_type_name,
			length=(
				None if spec.length is None else
				Length(value=str(spec.length))
			),
			min_length=(
				None if spec.min_length is None or spec.length is not None else
				MinLength(value=str(spec.min_length))
			),
			max_length=(
				None if spec.max_length is None or spec.length is not None else
				MaxLength(value=str(spec.max_length))
			),
			whitespace=(
				None if spec.whitespace == "preserve" else
				WhiteSpace(value=spec.whitespace)
			),
			pattern=(
				None if spec.pattern is None else
				RegexPattern(value=spec.pattern)
			),
			enumerations=(
				None if spec.enumerations is None else [
					Enumeration(value=str(e.value))
					for e in spec.enumerations
				]
			)
		)
	)


def create_numeric_simple_type(spec: NumericTypeSpec) -> SimpleType:
	return SimpleType(
		name=spec.wsdl_type_name,
		restriction=NumericTypeRestriction(
			base=spec.default_wsdl_type_name,
			min_inclusive=(
				None if spec.min_value is None else
				MinInclusive(value=str(spec.min_value))
			),
			max_inclusive=(
				None if spec.max_value is None else
				MaxInclusive(value=str(spec.max_value))
			),
			total_digits=(
				None if spec.total_digits is None else
				TotalDigits(value=str(spec.total_digits))
			),
			pattern=(
				None if spec.pattern is None else
				RegexPattern(value=spec.pattern)
			),
			enumerations=(
				None if spec.enumerations is None else [
					Enumeration(value=str(e.value))
					for e in spec.enumerations
				]
			)
		)
	)
