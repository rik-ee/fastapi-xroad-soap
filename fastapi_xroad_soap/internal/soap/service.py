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
from lxml.etree import LxmlError
from pydantic import ValidationError
from fastapi import FastAPI, Request, Response
from fastapi.types import DecoratedCallable
from starlette.types import Lifespan
from fastapi_xroad_soap.internal import utils
from fastapi_xroad_soap.internal.soap import faults as f
from fastapi_xroad_soap.internal.soap.action import SoapAction
from fastapi_xroad_soap.internal.multipart.errors import BaseMPError

try:
	from fastapi_xroad_soap.internal import wsdl
except ImportError:
	wsdl = utils.LazyImport("fastapi_xroad_soap.internal.wsdl")


__all__ = ["SoapService"]


class SoapService(FastAPI):
	def __init__(
			self,
			*,
			name: str = "SoapService",
			path: str = "/service",
			this_namespace: str = "https://example.org",
			wsdl_override: t.Optional[t.Union[str, Path]] = None,
			lifespan: t.Optional[Lifespan[FastAPI]] = None
	) -> None:
		self._wsdl = None
		self._name = name
		self._tns = this_namespace
		self._wsdl_override = wsdl_override
		if wsdl_override is not None:
			self._wsdl = utils.read_cached_xml_file(wsdl_override)
		self._actions: dict[str, SoapAction] = dict()

		super().__init__(
			root_path=path,
			lifespan=lifespan,
			openapi_url=None,
			redoc_url=None,
			docs_url=None,
		)

		@self.middleware('http')
		async def soap_middleware(http_request: Request, _: t.Callable) -> Response:
			try:
				if "wsdl" in http_request.query_params:
					if self._wsdl is None:
						self.regenerate_wsdl()
					return Response(self._wsdl)
				elif http_request.method != "POST":
					raise f.InvalidMethodFault(http_request.method)

				action_name = http_request.headers.get("soapaction", '').strip('"')
				if not action_name or action_name not in self._actions.keys():
					raise f.InvalidActionFault(action_name)

				body = await http_request.body()
				action = self._actions[action_name]
				content_type = http_request.headers.get("content-type")

				args = action.arguments_from(body, content_type)
				if inspect.iscoroutinefunction(action.handler):
					ret_obj = await action.handler(*args)
				else:
					ret_obj = action.handler(*args)
				return action.response_from(ret_obj)
			except f.SoapFault as ex:
				return ex.response
			except (BaseMPError, LxmlError, ValidationError) as ex:
				return f.ClientFault(ex).response
			except Exception as ex:
				return f.ServerFault(ex).response

	def action(self, name: str) -> t.Callable[[DecoratedCallable], DecoratedCallable]:
		if name in self._actions.keys():
			raise ValueError(f"Cannot add duplicate SOAP action '{name}'.")

		def closure(func: DecoratedCallable) -> DecoratedCallable:
			anno = utils.validate_annotations(name, func)
			pos = utils.extract_parameter_positions(anno)
			self._actions[name] = SoapAction(
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

	def regenerate_wsdl(self, *, force: bool = False) -> None:
		if self._wsdl_override is not None and not force:
			raise RuntimeError(
				"WSDL regeneration must be explicitly forced when "
				"SoapService has wsdl_override argument set."
			)
		self._wsdl = wsdl.generate(
			self._actions,
			self._name,
			self._tns
		)
