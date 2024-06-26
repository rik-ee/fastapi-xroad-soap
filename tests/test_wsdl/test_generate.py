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


__all__ = [
	"test_wsdl_gen_without_types",
	"test_wsdl_gen_swa_ref_type",
	"test_wsdl_gen_basic_types",
	"test_wsdl_gen_restricted_types",
	"test_wsdl_gen_single_type"
]


def test_wsdl_gen_without_types(wsdl_generator, read_wsdl_file):
	wsdl_data: bytes = wsdl_generator(None)
	file_data: bytes = read_wsdl_file("without_action_types.wsdl")
	assert file_data == wsdl_data


def test_wsdl_gen_swa_ref_type(wsdl_generator, read_wsdl_file):
	class Request(MessageBody, tag="Request"):
		files: t.List[SwaRef.File] = SwaRef.Element()

	wsdl_data: bytes = wsdl_generator(body_type=Request)
	file_data: bytes = read_wsdl_file("with_swa_ref_element.wsdl")
	assert file_data == wsdl_data


def test_wsdl_gen_basic_types(wsdl_generator, read_wsdl_file):
	class Request(MessageBody, tag="Request"):
		e1 = Boolean(tag="BooleanElement")
		e2 = Integer(tag="IntElement")
		e3 = Float(tag="FloatElement")
		e4 = String(tag="StringElement")
		e5 = Date(tag="DateElement")
		e6 = Time(tag="TimeElement")
		e7 = DateTime(tag="DateTimeElement")
		e8 = NetRes(tag="NetResElement")

	wsdl_data: bytes = wsdl_generator(body_type=Request)
	file_data: bytes = read_wsdl_file("with_basic_elements.wsdl")
	assert file_data == wsdl_data


def test_wsdl_gen_restricted_types(wsdl_generator, read_wsdl_file):
	class TextChoice(str, Enum):
		FIRST = "first"
		SECOND = "second"
		THIRD = "third"

	class Request(MessageBody, tag="Request"):
		bool_element: t.List[bool] = Boolean(min_occurs=1, max_occurs=2)
		int_element: t.List[int] = Integer(total_digits=5)
		float_element: t.List[float] = Float(pattern=r'^[0-4.]+$')
		str_element: t.List[str] = String(enumerations=TextChoice)
		other_str_element: t.List[str] = String(enumerations=TextChoice)
		date_element: t.List[date] = Date(min_value=date(2024, 2, 13))
		time_element: t.List[time] = Time(min_value=time(17, 33, 57))
		date_time_element: t.List[datetime] = DateTime(min_occurs=3, max_occurs=4)
		net_res_element: t.Optional[AnyUrl] = NetRes(length=20)

	wsdl_data: bytes = wsdl_generator(body_type=Request)
	file_data: bytes = read_wsdl_file("with_restricted_elements.wsdl")
	assert file_data == wsdl_data


def test_wsdl_gen_doc_and_ret(wsdl_generator, read_wsdl_file):
	class Response(MessageBody, tag="Response"):
		number = Integer()

	wsdl_data: bytes = wsdl_generator(description="Generate Integers", return_type=Response)
	file_data: bytes = read_wsdl_file("with_doc_and_ret.wsdl")
	assert file_data == wsdl_data


def test_wsdl_gen_single_type(wsdl_generator, read_wsdl_file):
	class Model(MessageBody, tag="Model"):
		number = Integer()

	wsdl_data: bytes = wsdl_generator(body_type=Model, return_type=Model)
	file_data: bytes = read_wsdl_file("single_type_action_io.wsdl")
	assert file_data == wsdl_data
