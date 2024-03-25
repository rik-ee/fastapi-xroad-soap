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
__all__ = ["BaseError", "NonMultipartError", "CorruptMultipartError"]


class BaseError(Exception):
    """Parent class of all errors of the fastapi-xroad-soap library."""
    pass


class NonMultipartError(BaseError):
    pass


class CorruptMultipartError(BaseError):
    pass
