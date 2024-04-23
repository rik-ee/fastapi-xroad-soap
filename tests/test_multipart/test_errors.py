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
from fastapi_xroad_soap.internal.multipart import errors as e


__all__ = [
	"test_non_multipart_error",
	"test_invalid_separator_error",
	"test_missing_content_id_error"
]


def test_non_multipart_error():
	obj = e.MultipartBoundaryError()
	assert str(obj) == "Unable to locate multipart boundary in Content-Type header"


def test_invalid_separator_error():
	obj = e.InvalidSeparatorError()
	assert str(obj) == "Multipart request body does not conform to RFC-5322"


def test_missing_content_id_error():
	obj = e.MissingContentIDError()
	assert str(obj) == "All file attachments must have Content-ID headers"
