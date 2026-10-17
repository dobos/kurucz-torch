import struct


class BinaryFile:
    """A tiny file-like wrapper that reads and writes Fortran unformatted records."""

    def __init__(self, file_obj, endian="<", marker_format="i", mode: str | None = None):
        # If file_obj is a string, treat it as a filename and open it.
        # For read access, the default is binary read mode; callers writing a new file
        # can pass mode="wb" explicitly.
        if isinstance(file_obj, str):
            self._filename = file_obj
            mode = mode if mode is not None else "rb"
            self.file = open(file_obj, mode)
            self._owns_file = True
        else:
            self.file = file_obj
            self._owns_file = False

        self._endian = endian
        self._marker_format = marker_format
        self._marker_size = struct.calcsize(marker_format)
        self._record_data = b""
        self._record_index = 0

    def _read_exact(self, byte_count):
        data = self.file.read(byte_count)
        if len(data) != byte_count:
            raise EOFError("Unexpected end of file while reading binary data")
        return data

    def _pack(self, format_string, value):
        return struct.pack(self._endian + format_string, value)

    def _unpack(self, format_string, data):
        return struct.unpack(self._endian + format_string, data)[0]

    def _read_record(self):
        marker = self.file.read(self._marker_size)
        if marker == b"":
            raise EOFError("Unexpected end of file while reading record marker")
        if len(marker) != self._marker_size:
            raise EOFError("Incomplete record marker")

        payload_size = self._unpack(self._marker_format, marker)
        if payload_size < 0:
            raise ValueError(f"Negative Fortran record length {payload_size}")

        payload = self._read_exact(payload_size)
        trailing_marker = self._read_exact(self._marker_size)
        trailing_size = self._unpack(self._marker_format, trailing_marker)
        if trailing_size != payload_size:
            raise ValueError(
                f"Record length markers do not match ({payload_size} != {trailing_size})"
            )

        self._record_data = payload
        self._record_index = 0
        return payload

    def _write_record(self, payload):
        payload_size = len(payload)
        marker = self._pack(self._marker_format, payload_size)
        self.file.write(marker)
        self.file.write(payload)
        self.file.write(marker)
        self._record_data = payload
        self._record_index = payload_size
        return payload

    def _ensure_record(self, format_string="i", count: int = 1):
        item_size = struct.calcsize(format_string)
        required_size = item_size * count
        if self._record_index >= len(self._record_data):
            self._read_record()
        if self._record_index + required_size > len(self._record_data):
            raise EOFError("Not enough bytes remaining in current Fortran record")

    def _read_from_record(self, format_string, count: int = 1):
        self._ensure_record(format_string, count)
        item_size = struct.calcsize(format_string)
        required_size = item_size * count
        if self._record_index + required_size > len(self._record_data):
            raise EOFError("Not enough bytes remaining in current Fortran record")
        chunk = self._record_data[self._record_index : self._record_index + required_size]
        self._record_index += required_size
        if count == 1:
            return self._unpack(format_string, chunk)
        return list(struct.unpack(self._endian + format_string * count, chunk))

    def _write_to_record(self, format_string, value):
        return self._pack(format_string, value)

    def read_int(self, count: int | None = None):
        count = 1 if count is None else count
        return self._read_from_record("i", count)

    def read_float(self, count: int | None = None):
        count = 1 if count is None else count
        return self._read_from_record("f", count)

    def read_double(self, count: int | None = None):
        count = 1 if count is None else count
        return self._read_from_record("d", count)

    def read_bytes(self, byte_count):
        self._ensure_record()
        if self._record_index + byte_count > len(self._record_data):
            raise EOFError("Not enough bytes remaining in current Fortran record")
        chunk = self._record_data[self._record_index : self._record_index + byte_count]
        self._record_index += byte_count
        return chunk

    def read_ints(self, count):
        return self._read_from_record("i", count)

    def read_floats(self, count):
        return self._read_from_record("f", count)

    def read_doubles(self, count):
        return self._read_from_record("d", count)

    def write_int(self, value):
        return self._write_record(self._write_to_record("i", int(value)))

    def write_float(self, value):
        return self._write_record(self._write_to_record("f", float(value)))

    def write_double(self, value):
        return self._write_record(self._write_to_record("d", float(value)))

    def write_ints(self, values):
        payload = b"".join(self._write_to_record("i", int(value)) for value in values)
        return self._write_record(payload)

    def write_floats(self, values):
        payload = b"".join(self._write_to_record("f", float(value)) for value in values)
        return self._write_record(payload)

    def write_doubles(self, values):
        payload = b"".join(self._write_to_record("d", float(value)) for value in values)
        return self._write_record(payload)

    def write_bytes(self, payload):
        return self._write_record(payload)

    def start_record(self):
        self._read_record()
        return len(self._record_data)

    def skip_record(self):
        """Consume the remainder of the current in-memory record without reading it."""
        self._record_index = len(self._record_data)

    def end_record(self):
        if self._record_index != len(self._record_data):
            raise ValueError("Current record has unread bytes remaining")
        self._record_data = b""
        self._record_index = 0

    def close(self):
        """Close the underlying file if it was opened by this instance."""
        if self._owns_file and hasattr(self.file, "close"):
            self.file.close()

    def __getattr__(self, name):
        return getattr(self.file, name)

    def __iter__(self):
        return iter(self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


__all__ = [
    "BinaryFile",
]
