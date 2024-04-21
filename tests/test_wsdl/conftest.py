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
from enum import Enum
from pydantic import AnyUrl
from datetime import date, time, datetime
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.elements.models import (
	Boolean, Integer, Float, String, Date, Time, DateTime, NetRes, SwaRef
)


__all__ = ["IncomingRequest", "OutgoingResponse"]


class TextChoice(str, Enum):
	FIRST = "first"
	SECOND = "second"
	THIRD = "third"


class DefaultModel(MessageBody):
	e1 = Boolean(tag="BooleanElem")
	e2 = Integer(tag="IntElem")
	e3 = Float(tag="FloatElem")
	e4 = String(tag="StringElem")
	e5 = Date(tag="DateElem")
	e6 = Time(tag="TimeElem")
	e7 = DateTime(tag="DateTimeElem")
	e8 = NetRes(tag="NetResElem")
	e9 = SwaRef.Element(tag="SwaRefElem")


class RestrictedModel(MessageBody):
	bool_elem: t.List[bool] = Boolean(min_occurs=1, max_occurs=2)
	int_elem: t.List[int] = Integer(total_digits=5)
	float_elem: t.List[float] = Float(pattern=r'^[0-4.]+$')
	str_elem: t.List[str] = String(enumerations=TextChoice)
	date_elem: t.List[date] = Date(min_value=date(2024, 2, 13))
	time_elem: t.List[time] = Time(min_value=time(17, 33, 57))
	date_time_elem: t.List[datetime] = DateTime(min_occurs=3, max_occurs=4)
	net_res_elem: t.Optional[AnyUrl] = NetRes(length=20)
	swa_res_elem: t.Optional[SwaRef.File] = SwaRef.Element()


class IncomingRequest(MessageBody):
	default_model = DefaultModel.Element()


class OutgoingResponse(MessageBody):
	restricted_model = RestrictedModel.Element()
