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
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_xroad_soap.internal.multipart import MultipartError
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal import utils, wsdl
from .action import SoapAction
from . import faults as f


__all__ = ["SoapService"]


SoapMiddleware: t.TypeAlias = BaseHTTPMiddleware


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
		self._name = name
		self._tns = this_namespace
		self._wsdl_response = None
		self._wsdl_override = wsdl_override
		self._storage = GlobalWeakStorage()
		self._actions = dict()

		if isinstance(wsdl_override, (str, Path)):
			wsdl_file = utils.read_cached_xml_file(wsdl_override)
			self._wsdl_response = Response(
				media_type="text/xml",
				content=wsdl_file
			)
		super().__init__(
			root_path=path,
			lifespan=lifespan,
			openapi_url=None,
			redoc_url=None,
			docs_url=None,
		)
		self._as_asgi().add_middleware(
			middleware_class=SoapMiddleware,
			dispatch=self._soap_middleware
		)

	def _as_asgi(self) -> FastAPI:
		return t.cast(FastAPI, self)

	async def _soap_middleware(self, http_request: Request, _: t.Callable) -> t.Optional[Response]:
		try:
			if "wsdl" in http_request.query_params:
				if self._wsdl_response is None:
					self.regenerate_wsdl()
				return self._wsdl_response
			elif http_request.method != "POST":
				raise f.InvalidMethodFault(http_request.method)

			action_name = http_request.headers.get("soapaction", '').strip('"')
			if not action_name or action_name not in self._actions.keys():
				raise f.InvalidActionFault(action_name)

			http_body = await http_request.body()
			content_type = http_request.headers.get("content-type")

			action = self._actions[action_name]
			envelope = action.parse(http_body, content_type)
			args = action.arguments_from(envelope, action_name)

			if inspect.iscoroutinefunction(action.handler):
				ret = await action.handler(*args)
			else:
				ret = action.handler(*args)
			return action.response_from(ret, envelope.header)

		except f.SoapFault as ex:
			return ex.response
		except ValidationError as ex:
			return f.ValidationFault(ex).response
		except (MultipartError, LxmlError) as ex:
			return f.ClientFault(ex).response
		except Exception as ex:
			return f.ServerFault(ex).response

	def add_action(self, name: str, handler: t.Callable[..., t.Any]) -> None:
		if name in self._actions.keys():
			raise ValueError(f"Cannot add duplicate {name} SOAP action.")
		anno = utils.validate_annotations(name, handler)
		pos = utils.extract_parameter_positions(anno)
		self._actions[name] = SoapAction(
			name=name,
			handler=handler,
			body_type=anno.get("body"),
			body_index=pos.get("body"),
			header_type=anno.get("header"),
			header_index=pos.get("header"),
			return_type=anno.get("return"),
			storage=self._storage
		)

	def action(self, name: str) -> t.Callable[[DecoratedCallable], DecoratedCallable]:
		def closure(func: DecoratedCallable) -> DecoratedCallable:
			self.add_action(name, func)
			return func
		return closure

	def regenerate_wsdl(self, *, force: bool = False) -> None:
		if self._wsdl_override is not None and not force:
			raise RuntimeError(
				"WSDL regeneration must be explicitly forced when "
				"SoapService has wsdl_override argument set."
			)
		self._wsdl_response = Response(
			media_type="text/xml",
			content=wsdl.generate(
				self._actions,
				self._name,
				self._tns
			)
		)
