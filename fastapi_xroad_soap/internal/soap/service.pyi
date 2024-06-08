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
from pydantic import Field, validate_call
from fastapi.types import DecoratedCallable
from starlette.types import Scope, Receive, Send, Lifespan
from fastapi import Request, Response, FastAPI as ASGIApp
from ..storage import GlobalWeakStorage
from .action import SoapAction


FuncOrCoro = t.Union[t.Callable[..., t.Any], t.Awaitable[t.Any]]
FaultCallback = t.Callable[[Request, Exception], t.Union[None, t.Coroutine[t.Any, t.Any, None]]]


class FastAPI:
	def __call__(self, scope: Scope, receive: Receive, send: Send) -> t.Awaitable[None]: ...


class SoapService(FastAPI):
	_name: str
	_path: str
	_version: int
	_tns: str
	_wsdl_response: t.Union[Response, None]
	_wsdl_override: t.Optional[t.Union[str, Path]]
	_fault_callback: t.Optional[FaultCallback] = None
	_hide_ise_cause: bool = False
	_storage: GlobalWeakStorage
	_actions: dict[str, SoapAction]

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
			hide_ise_cause: bool = False
	) -> None: ...

	async def _soap_middleware(self, http_request: Request, _: t.Callable) -> t.Optional[Response]: ...

	def _determine_action(self, http_request: Request) -> SoapAction: ...

	@staticmethod
	async def _await_or_call(func: FuncOrCoro, *args, **kwargs) -> t.Any: ...

	def add_action(
			self,
			name: str,
			handler: t.Callable[..., t.Any],
			description: t.Optional[str] = None
	) -> None: ...

	def action(
			self,
			name: str,
			description: t.Optional[str] = None
	) -> t.Callable[[DecoratedCallable], DecoratedCallable]: ...

	def regenerate_wsdl(self, *, force: bool = False) -> None: ...
