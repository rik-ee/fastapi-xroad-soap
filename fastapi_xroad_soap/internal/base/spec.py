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
import inflection
from abc import ABC, abstractmethod
from pydantic_xml import model, element
from ..constants import A8nType
from . import validators as vld

try:
	from .body import MessageBody
except ImportError:  # pragma: no cover
	MessageBody: t.TypeAlias = t.Any


__all__ = ["BaseElementSpec"]


class BaseElementSpec(ABC):
	tag: t.Optional[str]
	ns: t.Optional[str]
	nsmap: t.Optional[t.Dict[str, str]]
	min_occurs: int
	max_occurs: t.Union[int, t.Literal["unbounded"]]
	element_type: t.Type[MessageBody]
	internal_type: t.Optional[t.Type[MessageBody]]
	a8n_type: t.Union[A8nType, None]

	def __init__(
			self,
			element_type: t.Type[MessageBody],
			internal_type: t.Optional[t.Type[MessageBody]] = None,
			**kwargs
	) -> None:
		self.tag = kwargs.get("tag")
		self.ns = kwargs.get("ns")
		self.nsmap = kwargs.get("nsmap")
		self.min_occurs = kwargs.get("min_occurs") or 0
		self.max_occurs = kwargs.get("max_occurs") or "unbounded"
		self.element_type = element_type
		self.internal_type = internal_type
		self.a8n_type = None

	@abstractmethod
	def init_instantiated_data(self, data: t.List[t.Any]) -> t.List[t.Any]: ...

	@abstractmethod
	def init_deserialized_data(self, data: t.List[t.Any]) -> t.List[t.Any]: ...

	@property
	@abstractmethod
	def has_constraints(self) -> bool: ...

	@abstractmethod
	def wsdl_type_name(self, *, with_tns: bool = False) -> str: ...

	@property
	def default_wsdl_type_name(self) -> str:
		raise NotImplementedError

	def assemble_wsdl_type_name(self, signature: str, with_tns: bool) -> str:
		if not self.has_constraints:
			return self.default_wsdl_type_name
		ns = "tns:" if with_tns else ''
		cap_name = self.default_wsdl_type_name.capitalize()
		return f"{ns}Custom{cap_name}__{signature}"

	def get_element_a8n(self) -> t.Type[t.List[t.Any]]:
		return t.List[self.internal_type or self.element_type]

	def get_element(self, attr: str) -> model.XmlEntityInfo:
		return element(
			tag=self.tag or inflection.camelize(attr),
			ns=self.ns or '',
			nsmap=self.nsmap or dict(),
			default_factory=list
		)

	def set_a8n_type_from(self, a8n: t.Any, attr: str, cls_name: str) -> None:
		vld.validate_a8n_args(a8n, attr, cls_name, self.element_type)
		if a8n in [A8nType.ABSENT, self.element_type]:
			self.a8n_type = A8nType.MAND
			return
		if origin := t.get_origin(a8n):
			if origin == list:
				self.a8n_type = A8nType.LIST
				return
			elif "Union" in origin.__name__:
				self.a8n_type = A8nType.OPT
				return
		raise TypeError(
			f"Unsupported annotation '{a8n}' for "
			f"class '{cls_name}' attribute '{attr}'."
		)
