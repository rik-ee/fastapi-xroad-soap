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
import inspect
import typing as t
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.types import DecoratedCallable
from starlette.types import Lifespan
from .utils.import_utils import LazyImport
from .envelope import EnvelopeFactory
from .actionspec import ActionSpec
from . import utils
try:
	from src.wsdl import generator as wsdl
except ImportError:
	wsdl = LazyImport("src.wsdl.generator")


__all__ = ["SoapService"]


class SoapService(FastAPI):
	def __init__(
			self,
			name: str = "SoapService",
			path: str = "/service",
			lifespan: t.Optional[Lifespan[FastAPI]] = None,
			wsdl_override: t.Optional[t.Union[str, Path]] = None
	) -> None:
		super().__init__(
			root_path=path,
			lifespan=lifespan,
			openapi_url=None,
			redoc_url=None,
			docs_url=None,
		)
		self._name: str = name
		self._actions: dict[str, ActionSpec] = dict()
		self._wsdl_override = None
		if wsdl_override is not None:
			self._wsdl_override = utils.read_cached_xml_file(wsdl_override)

		@self.middleware('http')
		async def soap_middleware(request: Request, _: t.Callable) -> Response:
			if "wsdl" in request.query_params:
				if self._wsdl_override is not None:
					return Response(self._wsdl_override)
				return Response("dynamically generated wsdl")
			elif request.method != "POST":
				return Response("Not POST", status_code=400)

			action = request.headers.get("soapaction", '').strip('"')
			if not action:
				return Response("No soapaction", status_code=400)
			elif action not in self._actions.keys():
				return Response("Invalid action", status_code=400)
			try:
				# body = await request.body()
				# body = body.lstrip(b'\r\n')
				# print(self._is_multipart(request.headers))
				# return Response(f"asdfg")
				# ct1 = request.headers['Content-Type']
				# decoder = MultipartDecoder(body, ct1)
				# for part in decoder.parts:
				# 	cte = part.headers.get(b"Content-Transfer-Encoding", b"")
				# 	print(f"CTE: {cte}")
				#
				# 	ct2 = part.headers[b'Content-Type']
				# 	if b"multipart/mixed" in ct2:
				# 		print("--- NESTED BEGIN ---")
				# 		decoder2 = MultipartDecoder(part.content, ct2.decode())
				# 		for part2 in decoder2.parts:
				# 			cte = part2.headers.get(b"Content-Transfer-Encoding", b"")
				# 			print(f"CTE: {cte}")
				# 		print("--- NESTED END ---")
				# 	else:
				# 		print(part.headers)
				# 		print(part.content)
				# file_bytes = hlp.process_submitted_file(file_data)
				# print(body)
				# print(self._is_multipart(request.headers))

				spec = self._actions[action]
				envelope = EnvelopeFactory[route["body"]]()
				message = envelope.deserialize(body)
				args = spec.arguments_from(message)
				if inspect.iscoroutinefunction(spec.handler):
					ret = await spec.handler(*args)
				else:
					ret = spec.handler(*args)
				return spec.response_from(ret)
			except Exception as ex:
				return Response(f"ERROR: {str(ex)}", status_code=500)

	def action(self, name: str) -> t.Callable[[DecoratedCallable], DecoratedCallable]:
		if name in self._actions.keys():
			raise ValueError(f"Cannot add duplicate SOAP action name '{name}'.")

		def closure(func: DecoratedCallable) -> DecoratedCallable:
			anno = utils.validate_annotations(name, func)
			pos = utils.extract_parameter_positions(anno)
			self._actions[name] = ActionSpec(
				name=name,
				handler=func,
				body_type=anno.get("body"),
				body_index=pos.get("body"),
				header_type=anno.get("header"),
				header_index=pos.get("header"),
				return_type=anno.get("return")
			)
			return func
		return closure
