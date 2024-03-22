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
from typing import Callable, Optional, Any
from fastapi import FastAPI, Request, Response
from fastapi.types import DecoratedCallable
from pydantic_xml import BaseXmlModel
from starlette.types import Lifespan
from src.utils.import_utils import LazyImport
from src.envelope.header import XroadHeader
from src.envelope.parts import MessageBody
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
			lifespan: Optional[Lifespan[FastAPI]] = None
	) -> None:
		super().__init__(
			root_path=path,
			lifespan=lifespan,
			openapi_url=None,
			redoc_url=None,
			docs_url=None,
		)
		self._name: str = name
		self._actions: dict[str, dict] = dict()

		@self.middleware('http')
		async def soap_middleware(request: Request, _: Callable) -> Response:
			if "wsdl" in request.query_params:
				return Response(wsdl.generate(self))
			elif request.method != "POST":
				return Response("Not POST", status_code=400)

			action = request.headers.get("soapaction", '').strip('"')
			if not action:
				return Response("No soapaction", status_code=400)
			elif action not in self._actions.keys():
				return Response("Invalid action", status_code=400)
			try:
				envelope = ENVELOPE  # TODO: Parse from request

				route = self._actions[action]
				handler, ret_type = route["handler"], route["return"]
				args = self._prepare_args(envelope, route)
				if inspect.iscoroutinefunction(handler):
					ret = await handler(*args)
				else:
					ret = handler(*args)

				return self._create_response(ret, ret_type)

			except Exception as ex:
				return Response(f"ERROR: {str(ex)}", status_code=500)

	@staticmethod
	def _prepare_args(envelope, route) -> list[BaseXmlModel]:
		args = list()
		for key, idx in route["params"].items():
			if idx is None:
				continue
			elif key == "body":
				args.insert(idx, envelope.body.content)
			elif key == "header":
				args.insert(idx, envelope.header)
		return args

	@staticmethod
	def _create_response(ret_obj: Any, ret_type: Any) -> Response:
		err_msg = f"Unexpected return type: {ret_type}"
		if ret_obj is not None:
			if ret_type is None or not isinstance(ret_obj, MessageBody):
				return Response(err_msg)
			return Response(ret_obj.to_xml(
				skip_empty=True,
				pretty_print=True,
				standalone=False,
				encoding="utf-8"
			).decode("utf-8"))
		elif ret_type is None:
			return Response()
		return Response(err_msg)

	@staticmethod
	def _get_annotations(func: Any, key: str = "__annotations__") -> dict:
		atd = getattr(func, key, None)
		if atd is None and hasattr(func, "__dict__"):
			atd = func.__dict__.get(key, None)
		return atd or dict()

	def _validate_handler_annotations(self, name: str, func: DecoratedCallable) -> dict:
		if name in self._actions.keys():
			raise ValueError(f"Cannot add duplicate SOAP action name '{name}'.")
		atd = self._get_annotations(func)
		for key, value in atd.items():
			if key not in ["body", "header", "return"]:
				raise ValueError(
					f"Parameter name '{key}' not allowed in SOAP action '{name}'."
					"\nOnly names 'body' and 'header' can be used for parameters."
				)
			elif key == "return":
				if value is not None and not issubclass(value, MessageBody):
					raise TypeError(
						f"Return type annotation must be either "
						"'None' or a subclass of 'MessageBody'."
					)
			elif key == "body":
				if value is None or not issubclass(value, MessageBody):
					raise TypeError(
						f"The annotation of the '{key}' parameter in the '{name}' "
						f"SOAP action must be a subclass of 'MessageBody'."
					)
			elif value != XroadHeader:
				raise ValueError(
					f"The annotation of the 'headers' parameter in the '{name}' "
					f"SOAP action must be the 'XroadHeaders' class."
				)
		return atd

	def action(self, name: str) -> Callable[[DecoratedCallable], DecoratedCallable]:
		def closure(func: DecoratedCallable) -> DecoratedCallable:
			atd = self._validate_handler_annotations(name, func)
			keys = list(atd.keys())
			params = dict()
			for key in ["body", "header"]:
				params[key] = keys.index(key) if key in keys else None
			self._actions[name] = dict(
				**atd,
				handler=func,
				params=params
			)
			return func
		return closure
