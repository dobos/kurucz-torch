import io
import os
import struct
import tempfile
from unittest import TestCase

from kurucz.fortran.binaryfile import BinaryFile


class TestBinaryFile(TestCase):
    def test_read_scalar_values_from_single_record(self):
        payload = struct.pack("<dddiiifi", 1000.0, 500000.0, 1001.0, 2, 72, -1, 1.5, 1)
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))
        stream = io.BytesIO(record)

        bf = BinaryFile(stream)
        bf.start_record()
        self.assertAlmostEqual(bf.read_double(), 1000.0, places=6)
        self.assertAlmostEqual(bf.read_double(), 500000.0, places=6)
        self.assertAlmostEqual(bf.read_double(), 1001.0, places=6)
        self.assertEqual(bf.read_int(), 2)
        self.assertEqual(bf.read_int(), 72)
        self.assertEqual(bf.read_int(), -1)
        self.assertAlmostEqual(bf.read_float(), 1.5, places=6)
        self.assertEqual(bf.read_int(), 1)
        bf.end_record()

    def test_write_and_read_individual_record_types(self):
        stream = io.BytesIO()
        bf = BinaryFile(stream)
        bf.write_int(11)
        bf.write_float(2.5)
        bf.write_double(7.25)

        stream.seek(0)
        reader = BinaryFile(stream)
        reader.start_record()
        self.assertEqual(reader.read_int(), 11)
        reader.end_record()

        reader.start_record()
        self.assertAlmostEqual(reader.read_float(), 2.5, places=6)
        reader.end_record()

        reader.start_record()
        self.assertAlmostEqual(reader.read_double(), 7.25, places=6)
        reader.end_record()

    def test_skip_record_discards_remaining_bytes_in_current_record(self):
        payload = struct.pack("<dddii", 1.0, 2.0, 3.0, 4, 5)
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))
        bf = BinaryFile(io.BytesIO(record))

        bf.start_record()
        self.assertAlmostEqual(bf.read_double(), 1.0, places=6)
        bf.skip_record()
        bf.end_record()

    def test_can_read_from_filename_in_binary_read_mode(self):
        payload = struct.pack("<dddii", 1.0, 2.0, 3.0, 4, 5)
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(record)
            filename = handle.name

        try:
            bf = BinaryFile(filename)
            bf.start_record()
            self.assertAlmostEqual(bf.read_double(), 1.0, places=6)
            self.assertAlmostEqual(bf.read_double(), 2.0, places=6)
            self.assertAlmostEqual(bf.read_double(), 3.0, places=6)
            self.assertEqual(bf.read_int(), 4)
            self.assertEqual(bf.read_int(), 5)
            bf.end_record()
            bf.close()
        finally:
            os.unlink(filename)

    def test_detects_mismatched_record_markers(self):
        payload = struct.pack("<i", 10)
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload) + 4)
        bf = BinaryFile(io.BytesIO(record))

        with self.assertRaises(ValueError):
            bf.start_record()
