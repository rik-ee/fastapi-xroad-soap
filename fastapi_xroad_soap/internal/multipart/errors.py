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
    "NonMultipartError",
    "CorruptMultipartError",
    "MissingContentIDError"
]


class MultipartError(Exception):
    pass


class NonMultipartError(MultipartError):
    def __init__(self, mimetype: str):
        msg = f"Unexpected mimetype in content-type header: '{mimetype}'"
        super().__init__(msg)


class CorruptMultipartError(MultipartError):
    def __init__(self):
        msg = "Request body is not a valid multipart message"
        super().__init__(msg)


class MissingContentIDError(MultipartError):
    def __init__(self):
        msg = f"All MIME file attachments must have Content-ID headers"
        super().__init__(msg)
