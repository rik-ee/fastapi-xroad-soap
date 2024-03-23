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
import os
import contextlib
from uuid import uuid4
from fastapi_xroad_soap.internal.multipart import fields


class MultipartEncoder:
    def __init__(self, fields_, boundary=None, encoding='utf-8'):
        #: Boundary value either passed in by the user or created
        self.boundary_value = boundary or uuid4().hex

        # Computed boundary
        self.boundary = '--{}'.format(self.boundary_value)

        #: Encoding of the data being passed in
        self.encoding = encoding

        # Pre-encoded boundary
        self._encoded_boundary = b''.join([
            encode_with(self.boundary, self.encoding),
            encode_with('\r\n', self.encoding)
            ])

        #: Fields provided by the user
        self.fields = fields_

        #: Whether the encoder is finished
        self.finished = False

        #: Pre-computed parts of the upload
        self.parts = []

        # Pre-computed parts iterator
        self._iter_parts = iter([])

        # The part we're currently working with
        self._current_part = None

        # Cached computation of the body's length
        self._len = None

        # Our buffer
        self._buffer = CustomBytesIO(encoding=encoding)

        # Pre-compute each part's headers
        self._prepare_parts()

        # Load boundary into buffer
        self._write_boundary()

    @property
    def len(self):
        return self._len or self._calculate_length()

    def __repr__(self):
        return '<MultipartEncoder: {!r}>'.format(self.fields)

    def _calculate_length(self):
        boundary_len = len(self.boundary)
        self._len = sum(
            (boundary_len + total_len(p) + 4) for p in self.parts
            ) + boundary_len + 4
        return self._len

    def _calculate_load_amount(self, read_size):
        amount = read_size - total_len(self._buffer)
        return amount if amount > 0 else 0

    def _load(self, amount):
        self._buffer.smart_truncate()
        part = self._current_part or self._next_part()
        while amount == -1 or amount > 0:
            written = 0
            if part and not part.bytes_left_to_write():
                written += self._write(b'\r\n')
                written += self._write_boundary()
                part = self._next_part()

            if not part:
                written += self._write_closing_boundary()
                self.finished = True
                break

            written += part.write_to(self._buffer, amount)

            if amount != -1:
                amount -= written

    def _next_part(self):
        try:
            p = self._current_part = next(self._iter_parts)
        except StopIteration:
            p = None
        return p

    def _iter_fields(self):
        _fields = self.fields
        if hasattr(self.fields, 'items'):
            _fields = list(self.fields.items())
        for k, v in _fields:
            file_name = None
            file_type = None
            file_headers = None
            if isinstance(v, (list, tuple)):
                if len(v) == 2:
                    file_name, file_pointer = v
                elif len(v) == 3:
                    file_name, file_pointer, file_type = v
                else:
                    file_name, file_pointer, file_type, file_headers = v
            else:
                file_pointer = v

            field = fields.RequestField(
                name=k, data=file_pointer,
                filename=file_name,
                headers=file_headers
            )
            field.make_multipart(content_type=file_type)
            yield field

    def _prepare_parts(self):
        enc = self.encoding
        self.parts = [Part.from_field(f, enc) for f in self._iter_fields()]
        self._iter_parts = iter(self.parts)

    def _write(self, bytes_to_write):
        return self._buffer.append(bytes_to_write)

    def _write_boundary(self):
        return self._write(self._encoded_boundary)

    def _write_closing_boundary(self):
        with reset(self._buffer):
            self._buffer.seek(-2, 2)
            self._buffer.write(b'--\r\n')
        return 2

    def _write_headers(self, headers):
        return self._write(encode_with(headers, self.encoding))

    @property
    def content_type(self):
        return f'multipart/form-data; boundary={self.boundary_value}'

    def to_string(self):
        return self.read()

    def read(self, size=-1):
        if self.finished:
            return self._buffer.read(size)

        bytes_to_load = size
        if bytes_to_load != -1 and bytes_to_load is not None:
            bytes_to_load = self._calculate_load_amount(int(size))

        self._load(bytes_to_load)
        return self._buffer.read(size)


def encode_with(string, encoding):
    if not (string is None or isinstance(string, bytes)):
        return string.encode(encoding)
    return string


def total_len(o):
    if hasattr(o, '__len__'):
        return len(o)

    if hasattr(o, 'len'):
        return o.len

    if hasattr(o, 'fileno'):
        try:
            fileno = o.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            return os.fstat(fileno).st_size

    if hasattr(o, 'getvalue'):
        # e.g. BytesIO, cStringIO.StringIO
        return len(o.getvalue())


@contextlib.contextmanager
def reset(buffer):
    original_position = buffer.tell()
    buffer.seek(0, 2)
    yield
    buffer.seek(original_position, 0)


def coerce_data(data, encoding):
    if not isinstance(data, CustomBytesIO):
        if hasattr(data, 'getvalue'):
            return CustomBytesIO(data.getvalue(), encoding)

        if hasattr(data, 'fileno'):
            return FileWrapper(data)

        if not hasattr(data, 'read'):
            return CustomBytesIO(data, encoding)

    return data


class Part(object):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body
        self.headers_unread = True
        self.len = len(self.headers) + total_len(self.body)

    @classmethod
    def from_field(cls, field, encoding):
        headers = encode_with(field.render_headers(), encoding)
        body = coerce_data(field.data, encoding)
        return cls(headers, body)

    def bytes_left_to_write(self):
        to_read = 0
        if self.headers_unread:
            to_read += len(self.headers)

        return (to_read + total_len(self.body)) > 0

    def write_to(self, buffer, size):
        written = 0
        if self.headers_unread:
            written += buffer.append(self.headers)
            self.headers_unread = False
        while total_len(self.body) > 0 and (size == -1 or written < size):
            amount_to_read = size
            if size != -1:
                amount_to_read = size - written
            written += buffer.append(self.body.read(amount_to_read))
        return written


class CustomBytesIO(io.BytesIO):
    def __init__(self, buffer=None, encoding='utf-8'):
        buffer = encode_with(buffer, encoding)
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
        with reset(self):
            written = self.write(bytes_)
        return written

    def smart_truncate(self):
        to_be_read = total_len(self)
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
        return total_len(self.fd) - self.fd.tell()

    def read(self, length=-1):
        return self.fd.read(length)
