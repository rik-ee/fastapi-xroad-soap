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
from pathlib import Path
from fastapi.types import DecoratedCallable
from starlette.types import Scope, Receive, Send, Lifespan
from fastapi import Request, Response, FastAPI as ASGIApp
from ..storage import GlobalWeakStorage
from .action import SoapAction


FuncOrCoro = t.Union[t.Callable[..., t.Any], t.Awaitable[t.Any]]


class FastAPI:
	def __call__(self, scope: Scope, receive: Receive, send: Send) -> t.Awaitable[None]: ...


class SoapService(FastAPI):
	_name: str
	_tns: str
	_wsdl_response: t.Union[Response, None]
	_wsdl_override: t.Optional[t.Union[str, Path]]
	_fault_callback: t.Optional[t.Callable[[Request, Exception], None]] = None
	_hide_ise_cause: bool = False
	_storage: GlobalWeakStorage
	_actions: dict[str, SoapAction]

	def __init__(
			self,
			*,
			name: str = "SoapService",
			path: str = "/service",
			this_namespace: str = "https://example.org",
			wsdl_override: t.Optional[t.Union[str, Path]] = None,
			lifespan: t.Optional[Lifespan[FastAPI]] = None,
			fault_callback: t.Optional[t.Callable[[Request, Exception], None]] = None,
			hide_ise_cause: bool = False
	) -> None: ...

	def _as_fastapi(self) -> ASGIApp: ...

	async def _soap_middleware(self, http_request: Request, _: t.Callable) -> t.Optional[Response]: ...

	@staticmethod
	async def _await_or_call(func: FuncOrCoro, *args, **kwargs) -> t.Any: ...

	def add_action(self, name: str, handler: t.Callable[..., t.Any]) -> None: ...

	def action(self, name: str) -> t.Callable[[DecoratedCallable], DecoratedCallable]: ...

	def regenerate_wsdl(self, *, force: bool = False) -> None: ...
