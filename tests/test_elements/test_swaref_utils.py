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
import pytest
import base64
import hashlib
import typing as t
from fastapi_xroad_soap.internal.base import MessageBody
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.multipart import DecodedBodyPart
from fastapi_xroad_soap.internal.file_size import FileSize
from fastapi_xroad_soap.internal.elements.models import (
	String, SwaRef, SwaRefUtils
)


class DeepModel(MessageBody):
	deep_file: SwaRef.File = SwaRef.Element(tag="DeepFile")


class NestedModel(MessageBody):
	nested_files: t.List[SwaRef.File] = SwaRef.Element(tag="NestedFiles")
	deep_model: DeepModel


class TopModel(MessageBody):
	text = String(tag="Text")
	nested_model: NestedModel


def test_swa_ref_utils():
	assert SwaRefUtils.contains_swa_ref_specs(TopModel) is True
	assert SwaRefUtils.contains_swa_ref_specs(NestedModel) is True
	assert SwaRefUtils.contains_swa_ref_specs(DeepModel) is True

	model = TopModel(
		text="Hello World",
		nested_model=NestedModel(
			deep_model=DeepModel(
				deep_file=SwaRef.File(name="dfghj.zip", content=b"1234567")
			),
			nested_files=[
				SwaRef.File(name="asdfg.txt", content=b"qwerty"),
				SwaRef.File(name="tyuio.xml", content=b"zxcvbn")
			]
		)
	)
	specs, files = SwaRefUtils.gather_specs_and_files(t.cast(MessageBody, 1))
	assert len(specs) == 0
	assert len(files) == 0

	specs, files = SwaRefUtils.gather_specs_and_files(model)
	assert len(specs) == 2
	assert len(files) == 3

	for spec in specs:
		assert spec.tag in ["NestedFiles", "DeepFile"]

	data_map = {
		"dfghj.zip": b"1234567",
		"asdfg.txt": b"qwerty",
		"tyuio.xml": b"zxcvbn"
	}
	for file in files:
		assert data_map[file.name] == file.content
