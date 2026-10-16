import os
import struct
import tempfile
import unittest

from kurucz.compat.spectrumparametersreader import SpectrumParametersReader


class TestSpectrumParametersReader(unittest.TestCase):
    def test_reads_first_file9_record_only(self):
        first_payload = struct.pack("<dddiiifi", 3000.0, 500000.0, 3100.0, 128, 72, -20, 2.0, 1)
        first_record = (
            struct.pack("<i", len(first_payload))
            + first_payload
            + struct.pack("<i", len(first_payload))
        )

        second_payload = struct.pack("<i", 123456789)
        second_record = (
            struct.pack("<i", len(second_payload))
            + second_payload
            + struct.pack("<i", len(second_payload))
        )

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(first_record)
            handle.write(second_record)
            filename = handle.name

        try:
            reader = SpectrumParametersReader(filename)
            parameters = reader.read_spectrum_parameters()

            self.assertAlmostEqual(parameters.WLBEG, 3000.0, places=6)
            self.assertAlmostEqual(parameters.RESOLU, 500000.0, places=6)
            self.assertAlmostEqual(parameters.WLEND, 3100.0, places=6)
            self.assertEqual(parameters.LENGTH, 128)
            self.assertEqual(parameters.N, 72)
            self.assertEqual(parameters.LINOUT, -20)
            self.assertAlmostEqual(parameters.TURBV, 2.0, places=6)
            self.assertEqual(parameters.IFVAC, 1)
        finally:
            os.unlink(filename)

    def test_reads_spectrum_parameters_from_reference_fort9(self):
        reader = SpectrumParametersReader("/home/dobos/project/kurucz-torch/data/tests/fort.9")
        parameters = reader.read_spectrum_parameters()

        self.assertAlmostEqual(parameters.WLBEG, 100.0, places=6)
        self.assertAlmostEqual(parameters.RESOLU, 600000.0, places=6)
        self.assertAlmostEqual(parameters.WLEND, 2850.0, places=6)
        self.assertEqual(parameters.LENGTH, 2009944)
        self.assertEqual(parameters.N, 72)
        self.assertEqual(parameters.LINOUT, -1)
        self.assertAlmostEqual(parameters.TURBV, 1.5, places=6)
        self.assertEqual(parameters.IFVAC, 1)


if __name__ == "__main__":
    unittest.main()
