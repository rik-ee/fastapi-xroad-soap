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
import io
from .. import helpers


__all__ = ["EncodedBodyPart", "CustomBytesIO", "FileWrapper"]


class EncodedBodyPart(object):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body
        self.headers_unread = True
        self.len = len(self.headers) + helpers.total_len(self.body)

    @classmethod
    def from_field(cls, field, encoding):
        headers = helpers.encode_with(field.render_headers(), encoding)
        body = field.data
        if not isinstance(field.data, CustomBytesIO):
            if hasattr(field.data, 'getvalue'):
                body = CustomBytesIO(field.data.getvalue(), encoding)
            if hasattr(field.data, 'fileno'):
                body = FileWrapper(field.data)
            if not hasattr(field.data, 'read'):
                body = CustomBytesIO(field.data, encoding)
        return cls(headers, body)

    def bytes_left_to_write(self):
        to_read = 0
        if self.headers_unread:
            to_read += len(self.headers)
        return (to_read + helpers.total_len(self.body)) > 0

    def write_to(self, buffer, size):
        written = 0
        if self.headers_unread:
            written += buffer.append(self.headers)
            self.headers_unread = False
        while helpers.total_len(self.body) > 0 and (size == -1 or written < size):
            amount_to_read = size
            if size != -1:
                amount_to_read = size - written
            written += buffer.append(self.body.read(amount_to_read))
        return written


class CustomBytesIO(io.BytesIO):
    def __init__(self, buffer=None, encoding='utf-8'):
        buffer = helpers.encode_with(buffer, encoding)
        super(CustomBytesIO, self).__init__(buffer)

    def _get_end(self):
        current_pos = self.tell()
        self.seek(0, 2)
        length = self.tell()
        self.seek(current_pos, 0)
        return length

    @property
    def len(self):
        length = self._get_end()
        return length - self.tell()

    def append(self, bytes_):
        with helpers.reset(self):
            written = self.write(bytes_)
        return written

    def smart_truncate(self):
        to_be_read = helpers.total_len(self)
        already_read = self._get_end() - to_be_read

        if already_read >= to_be_read:
            old_bytes = self.read()
            self.seek(0, 0)
            self.truncate()
            self.write(old_bytes)
            self.seek(0, 0)


class FileWrapper(object):
    def __init__(self, file_object):
        self.fd = file_object

    @property
    def len(self):
        return helpers.total_len(self.fd) - self.fd.tell()

    def read(self, length=-1):
        return self.fd.read(length)
