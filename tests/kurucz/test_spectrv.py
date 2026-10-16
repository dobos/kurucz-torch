import os
import struct
import tempfile
import unittest

from kurucz.spectrv import Spectrv


class TestSpectrv(unittest.TestCase):
    def test_read_spectrum_data_from_file9_uses_spectrum_parameters(self):
        payload = struct.pack("<dddiiifi", 4500.0, 200000.0, 4550.0, 64, 72, 0, 1.0, 0)
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(record)
            filename = handle.name

        try:
            spectrv = Spectrv()
            parameters = spectrv.read_spectrum_data_from_file9(filename)

            self.assertAlmostEqual(parameters.WLBEG, 4500.0, places=6)
            self.assertEqual(spectrv.spectrum_parameters, parameters)
            self.assertEqual(parameters.IFVAC, 0)
        finally:
            os.unlink(filename)


if __name__ == "__main__":
    unittest.main()
