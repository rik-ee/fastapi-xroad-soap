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
import re
import typing as t
import inflection
from ..soap.action import SoapAction
from ..constants import A8nType
from ..elements import NumericTypeSpec
from ..elements import StringTypeSpec
from ..base import (
	MessageBody,
	CompositeMeta,
	BaseElementSpec
)
from . import models as mod


__all__ = [
	"format_wsdl_definitions",
	"gather_all_types"
]


_AllTypes = t.Tuple[
	t.List[mod.ComplexType],
	t.List[mod.SimpleType]
]


def format_wsdl_definitions(wsdl_string: str) -> bytes:
	return re.sub(
		pattern=r'(<wsdl:definitions[^>]*>)',
		repl=lambda match: match.group(1).replace(' ', '\n  '),
		string=wsdl_string,
		count=1
	).encode()


def gather_all_types(actions: t.Dict[str, SoapAction]) -> _AllTypes:
	simple_types: t.Dict[str, mod.SimpleType] = {}
	complex_types: t.List[mod.ComplexType] = []

	for model in _gather_models(actions):
		elements = []
		for name, spec in model.model_specs().items():
			if type(spec.element_type) is not CompositeMeta:
				_add_simple_type(spec, simple_types)
			elements.append(mod.Element(
				name=spec.tag or inflection.camelize(name),
				type=spec.wsdl_type_name(with_tns=True),
				max_occurs=(
					None if
					spec.a8n_type != A8nType.LIST
					else str(spec.max_occurs)
				),
				min_occurs={
					A8nType.MAND: None,
					A8nType.LIST: str(spec.min_occurs),
					A8nType.OPT: "0"
				}[spec.a8n_type]
			))
		complex_types.append(mod.ComplexType(
			name=model.__name__,
			sequence=mod.Sequence(
				elements=elements
			)
		))
	return complex_types, list(simple_types.values())


def _gather_models(actions: t.Dict[str, SoapAction]) -> t.List[t.Type["MessageBody"]]:
	models = []
	for action in actions.values():
		for model in [action.body_type, action.return_type]:
			nested = model.nested_models()
			models.extend(nested)
	return list(set(models))


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
