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
__all__ = [
    "MultipartError",
    "MultipartBoundaryError",
    "InvalidSeparatorError",
    "MissingContentIDError"
]


class MultipartError(Exception):
    pass


class MultipartBoundaryError(MultipartError):
    def __init__(self):
        msg = "Unable to locate multipart boundary in Content-Type header"
        super().__init__(msg)


class InvalidSeparatorError(MultipartError):
    def __init__(self):
        msg = "Multipart request body does not conform to RFC-5322"
        super().__init__(msg)


class MissingContentIDError(MultipartError):
    def __init__(self):
        msg = "All file attachments must have Content-ID headers"
        super().__init__(msg)
