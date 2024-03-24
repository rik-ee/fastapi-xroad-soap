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
from fastapi import Response
from dataclasses import dataclass
from .envelope import XroadHeader, MessageBody


__all__ = ["ActionSpec"]


@dataclass(frozen=True)
class ActionSpec:
	name: str
	handler: t.Callable[..., t.Optional[MessageBody]]
	body_type: t.Type[MessageBody]
	body_index: t.Optional[int]
	header_type: t.Type[XroadHeader]
	header_index: t.Optional[int]
	return_type: t.Optional[t.Type[MessageBody]]

	def arguments_from(self, obj: MessageBody) -> t.List[t.Union[MessageBody, XroadHeader]]:
		args = list()
		if self.body_type is not None:
			args.insert(self.body_index, obj.body.content)
		if self.header_type is not None:
			args.insert(self.header_index, obj.header)
		return args

	def response_from(self, obj: t.Optional[MessageBody]) -> Response:
		error = f"Unexpected return type: {obj}"
		if self.return_type is None:
			if obj is None:
				return Response()
			return Response(error)
		elif isinstance(obj, MessageBody):
			return Response(obj.to_xml(
				skip_empty=True,
				pretty_print=False,
				standalone=False,
				encoding="utf-8"
			).decode("utf-8"))
		return Response(error)
