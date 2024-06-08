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
from pydantic import Field, ValidationError, validate_call
from fastapi import FastAPI, Request, Response
from fastapi.types import DecoratedCallable
from starlette.types import Lifespan
from starlette.middleware.base import BaseHTTPMiddleware
from ..multipart import MultipartError
from ..storage import GlobalWeakStorage
from .. import utils, wsdl
from .validators import validate_annotations
from .action import SoapAction
from . import faults as f


__all__ = ["SoapService"]


SoapMiddleware: t.TypeAlias = BaseHTTPMiddleware
FuncOrCoro = t.Union[t.Callable[..., t.Any], t.Awaitable[t.Any]]
FaultCallback = t.Callable[[Request, Exception], t.Union[None, t.Coroutine[t.Any, t.Any, None]]]
ActionType = t.Callable[[DecoratedCallable], DecoratedCallable]


class SoapService(FastAPI):
	@validate_call
	def __init__(
			self,
			*,
			name: t.Annotated[str, Field(min_length=5)] = "SoapService",
			path: t.Annotated[str, Field(min_length=1)] = "/service",
			version: t.Annotated[int, Field(ge=1, le=99)] = 1,
			this_namespace: t.Annotated[str, Field(min_length=5)] = "https://example.org",
			wsdl_override: t.Optional[t.Union[str, Path]] = None,
			lifespan: t.Optional[Lifespan[FastAPI]] = None,
			fault_callback: t.Optional[FaultCallback] = None,
			hide_ise_cause: bool = False,
			debug: bool = False
	) -> None:
		self._name = name
		self._path = path
		self._version = version
		self._tns = this_namespace
		self._wsdl_response = None
		self._wsdl_override = wsdl_override
		self._fault_callback = fault_callback
		self._hide_ise_cause = hide_ise_cause
		self._storage = GlobalWeakStorage()
		self._actions = dict()

		if isinstance(wsdl_override, (str, Path)):
			wsdl_file = utils.read_cached_xml_file(wsdl_override)
			self._wsdl_response = Response(
				media_type="text/xml",
				content=wsdl_file
			)
		super().__init__(
			debug=debug,
			root_path=path,
			lifespan=lifespan,
			openapi_url=None,
			redoc_url=None,
			docs_url=None,
		)
		app = t.cast(FastAPI, self)
		app.add_middleware(
			middleware_class=SoapMiddleware,
			dispatch=self._soap_middleware
		)

	async def _soap_middleware(self, http_request: Request, _: t.Callable) -> t.Optional[Response]:
		http_body = await http_request.body()
		try:
			if self._path != '/' and http_request.url.path != self._path:
				return Response(status_code=404)
			elif "wsdl" in http_request.query_params:
				if self._wsdl_response is None:
					self.regenerate_wsdl()
				return self._wsdl_response
			elif http_request.method != "POST":
				raise f.InvalidMethodFault(http_request.method)

			action = self._determine_action(http_request)
			content_type = http_request.headers.get("content-type")
			envelope = await action.parse(http_body, content_type)

			args = action.arguments_from(envelope)
			ret = await self._await_or_call(action.handler, *args)
			return action.response_from(ret, envelope.header)

		except f.SoapFault as ex:
			err, resp = ex, ex.response
		except ValidationError as ex:
			err, resp = ex, f.ValidationFault(ex).response
		except (MultipartError, LxmlError) as ex:
			err, resp = ex, f.ClientFault(ex).response
		except Exception as ex:  # pragma: no cover
			err, resp = ex, f.ServerFault(
				"Internal Server Error" if
				self._hide_ise_cause else ex
			).response

		if self._fault_callback is not None:
			args = [http_body, http_request.headers, err]
			await self._await_or_call(self._fault_callback, *args)
		return resp

	def _determine_action(self, http_request: Request) -> SoapAction:
		name = http_request.headers.get("soapaction", '').strip('"')
		if not name:
			raise f.MissingActionFault()
		valid_names = self._actions.keys()
		if name in valid_names:
			return self._actions[name]
		sep = '#' if '#' in name else '/'
		fragment: str = name.split(sep)[-1]
		for vn in valid_names:
			if vn == fragment:
				return self._actions[fragment]
		raise f.InvalidActionFault(name)

	@staticmethod
	async def _await_or_call(func: FuncOrCoro, *args, **kwargs) -> t.Any:
		if inspect.iscoroutinefunction(func):
			return await func(*args, **kwargs)
		return func(*args, **kwargs)

	def add_action(self, name: str, handler: t.Callable[..., t.Any], description: t.Optional[str] = None) -> None:
		if name in self._actions.keys():
			raise ValueError(f"Cannot add duplicate {name} SOAP action.")
		anno = validate_annotations(name, handler)
		pos = utils.extract_parameter_positions(anno)
		self._actions[name] = SoapAction(
			name=name,
			handler=handler,
			description=description,
			body_type=anno.get("body"),
			body_index=pos.get("body"),
			header_type=anno.get("header"),
			header_index=pos.get("header"),
			return_type=anno.get("return"),
			storage=self._storage
		)

	def action(self, name: str, description: t.Optional[str] = None) -> ActionType:
		def closure(func: DecoratedCallable) -> DecoratedCallable:
			self.add_action(name, func, description)
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
				self._tns,
				self._version
			)
		)
