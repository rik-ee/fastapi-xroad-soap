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
from pydantic_xml import model
from fastapi_xroad_soap.internal.base import BaseElementSpec
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage
from fastapi_xroad_soap.internal.multipart import DecodedBodyPart
from fastapi_xroad_soap.internal.file_size import FileSize
from fastapi_xroad_soap.internal.elements.models import (
	SwaRef, SwaRefSpec, SwaRefInternal
)


__all__ = [
	"test_swa_ref_spec",
	"test_swa_ref_spec_data_init",
	"test_swa_ref_spec_restrictions",
	"test_swa_ref_internal"
]


def test_swa_ref_spec(nsmap, a8n_type_tester):
	spec = t.cast(SwaRefSpec, SwaRef.Element(
		tag="TestSwaRef",
		ns="pytest",
		nsmap=nsmap,
		min_occurs=123,
		max_occurs=456
	))
	assert isinstance(spec, SwaRefSpec)
	assert issubclass(SwaRefSpec, BaseElementSpec)

	assert spec.tag == "TestSwaRef"
	assert spec.ns == "pytest"
	assert spec.nsmap == nsmap
	assert spec.min_occurs == 123
	assert spec.max_occurs == 456
	assert spec.element_type == SwaRef.File
	assert spec.internal_type == SwaRefInternal
	assert spec.has_constraints is False

	for value in [True, False]:
		assert spec.wsdl_type_name(with_tns=value) == "wsi:swaRef"
	with pytest.raises(NotImplementedError):
		_ = spec.default_wsdl_type_name

	element = spec.get_element('')
	assert spec.get_element_a8n() == t.List[SwaRefInternal]
	assert isinstance(element, model.XmlEntityInfo)
	assert element.path == "TestSwaRef"
	assert element.ns == "pytest"
	assert element.nsmap == nsmap
	assert element.default_factory == list

	a8n_type_tester(spec)


def test_swa_ref_spec_data_init():
	spec = t.cast(SwaRefSpec, SwaRef.Element())

	file = t.cast(SwaRefInternal, SwaRef.File(
		name="asdfg.txt", content=b"qwerty"
	))
	assert file.name == "asdfg.txt"
	assert file.content == b"qwerty"
	assert file.size == 0
	assert file.digest == ''
	assert file.mimetype == ''
	assert file.content_id is None

	delattr(file, "content_id")
	spec.init_instantiated_data([file])
	assert file.size != 0
	assert file.digest != ''
	assert file.mimetype != ''
	assert not hasattr(file, "content_id")

	storage = GlobalWeakStorage()
	pretend_dbp = t.cast(DecodedBodyPart, file)
	fingerprint = storage.insert_object(pretend_dbp)

	other_file = t.cast(SwaRefInternal, SwaRef.File(
		name='', content=b''
	))
	file.content_id = None

	delattr(other_file, "content_id")
	spec.init_deserialized_data([other_file])
	assert other_file.name == ''
	assert other_file.content == b''

	other_file.content_id = "fingerprint"
	with pytest.raises(ValueError):
		spec.init_deserialized_data([other_file])

	other_file.content_id = fingerprint
	spec.init_deserialized_data([other_file])

	assert other_file.name == file.name
	assert other_file.content == file.content
	assert other_file.size == file.size
	assert other_file.digest == file.digest
	assert other_file.mimetype == file.mimetype
	assert not hasattr(other_file, "content_id")

	GlobalWeakStorage._inst_counter = 0  # clean up


def test_swa_ref_spec_restrictions():
	spec = t.cast(SwaRefSpec, SwaRef.Element(
		allowed_filetypes=[".xml"],
		max_filesize=FileSize.KB(1),
		hash_func="sha256"
	))
	with pytest.raises(ValueError):
		file = t.cast(SwaRefInternal, SwaRef.File(
			name="asdfgtxt", content=b'x' * 1024
		))
		spec.init_instantiated_data([file])
	with pytest.raises(ValueError):
		file = t.cast(SwaRefInternal, SwaRef.File(
			name="asdfg.txt", content=b'x' * 1024
		))
		spec.init_instantiated_data([file])
	with pytest.raises(ValueError):
		file = t.cast(SwaRefInternal, SwaRef.File(
			name="asdfg.xml", content=b'x' * 1025
		))
		spec.init_instantiated_data([file])
	file = t.cast(SwaRefInternal, SwaRef.File(
		name="asdfg.xml", content=b'x' * 1024
	))
	spec.init_instantiated_data([file])
	digest = hashlib.sha256(file.content).digest()
	b64_hash = base64.b64encode(digest).decode()
	assert f"sha256={b64_hash}" == file.digest


def test_swa_ref_internal():
	internal = SwaRefInternal(content=b"internal")
	assert internal.content_id is None

	internal = SwaRefInternal(name="internal")
	assert internal.content_id == "internal"
	assert internal.mime_cid == ''

	internal = SwaRefInternal(name="cid:0123456789")
	assert internal.mime_cid == "<0123456789>"
