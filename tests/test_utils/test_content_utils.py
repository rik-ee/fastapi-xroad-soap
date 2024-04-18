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
from fastapi_xroad_soap.internal.utils import content_utils as utils


__all__ = [
	"test_split_on_find",
	"test_guess_mime_type",
	"test_detect_decode_with_utf8",
	"test_detect_decode_with_unicode_error",
	"test_detect_decode_with_binary",
	"test_detect_decode_with_specific_encoding",
	"test_convert_to_utf8_with_utf8_input",
	"test_convert_to_utf8_with_non_utf8_input",
	"test_convert_to_utf8_with_binary_data",
	"test_convert_to_utf8_with_high_confidence_detection",
	"test_remove_memory_addresses_with_addresses",
	"test_remove_memory_addresses_without_addresses",
	"test_remove_memory_addresses_with_multiple_addresses",
	"test_remove_memory_addresses_empty_string"
]


def test_split_on_find():
	test_str = "qwerty---asdfg"
	ret = utils.split_on_find(test_str, '---')
	assert isinstance(ret, tuple)
	assert len(ret) == 2
	assert ret[0] == "qwerty"
	assert ret[1] == "asdfg"

	ret = utils.split_on_find(test_str, '+++')
	assert ret[0] == test_str
	assert ret[1] == test_str


def test_guess_mime_type():
	mime_map = {
		"file.json": ["application/json"],
		"file.txt": ["text/plain"],
		"file.xml": ["text/xml", "application/xml"],
		"file.zip": ["application/zip", "application/x-zip-compressed"],
		"file.tar": ["application/tar", "application/x-tar"],
		"file.exe": ["application/octet-stream", "application/x-msdownload", "application/x-msdos-program"],
		"file.bin": ["application/octet-stream"],
		"file.pdf": ["application/pdf"],
		"file.jpg": ["image/jpeg"],
		"file.png": ["image/png"],
		"file.mp4": ["video/mp4"],
		"file.mov": ["video/quicktime"],
		"file.unknown": ["application/octet-stream"]
	}
	for k, v in mime_map.items():
		assert utils.guess_mime_type(k) in v


def test_detect_decode_with_utf8():
	input_str = "hello world".encode("utf-8")
	expected = ("hello world", "utf-8")
	res = utils.detect_decode(input_str)
	assert res == expected


def test_detect_decode_with_unicode_error():
	input_str = "hello wörld".encode("cp1252")
	expected = ("hello wörld", "Windows-1252")
	res = utils.detect_decode(input_str, "utf-8")
	assert res == expected


def test_detect_decode_with_binary():
	input_str = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
	expected = (input_str, None)
	ret = utils.detect_decode(input_str)
	assert ret == expected


def test_detect_decode_with_specific_encoding():
	input_str = "olá mundo".encode("iso-8859-1")
	expected = ("olá mundo", "iso-8859-1")
	res = utils.detect_decode(input_str, "iso-8859-1")
	assert res == expected


def test_convert_to_utf8_with_utf8_input():
	utf8_string = "hello world".encode('utf-8')
	assert utils.convert_to_utf8(utf8_string) == utf8_string


def test_convert_to_utf8_with_non_utf8_input():
	latin1_string = "café".encode('latin-1')
	expected_output = "café".encode('utf-8')
	assert utils.convert_to_utf8(latin1_string) == expected_output


def test_convert_to_utf8_with_binary_data():
	binary_data = b'\xff\xd8\xff\xe0'
	assert utils.convert_to_utf8(binary_data) == binary_data


def test_convert_to_utf8_with_high_confidence_detection():
	greek_string = "γειά σου".encode('iso-8859-7')
	expected_output = "γειά σου".encode('utf-8')
	assert utils.convert_to_utf8(greek_string) == expected_output


def test_remove_memory_addresses_with_addresses():
	input_string = b"Error at 0x1A2B3C4D: Memory access violation"
	expected_output = b"Error at : Memory access violation"
	assert utils.remove_memory_addresses(input_string) == expected_output


def test_remove_memory_addresses_without_addresses():
	input_string = b"No memory address here"
	expected_output = b"No memory address here"
	assert utils.remove_memory_addresses(input_string) == expected_output


def test_remove_memory_addresses_with_multiple_addresses():
	input_string = b"Addresses 0xABC and 0x123 found here"
	expected_output = b"Addresses  and  found here"
	assert utils.remove_memory_addresses(input_string) == expected_output


def test_remove_memory_addresses_empty_string():
	input_string = expected_output = b''
	assert utils.remove_memory_addresses(input_string) == expected_output
