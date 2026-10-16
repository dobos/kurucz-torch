import os
import struct
import tempfile
import unittest

import torch

from kurucz.compat.continuumopacityreader import ContinuumOpacityReader
from kurucz.compat.spectrumparametersreader import SpectrumParametersReader
from kurucz.fortran.binaryfile import BinaryFile
from kurucz.spectrv import Spectrv


class TestContinuumOpacityReader(unittest.TestCase):
    def _read_edge_table_from_file(self, filename, skip_prefix_records=0):
        with open(filename, "rb") as handle:
            binary_file = BinaryFile(handle)
            for _ in range(skip_prefix_records):
                binary_file.start_record()
                binary_file.skip_record()

            binary_file.start_record()
            nedge = binary_file.read_int()
            frqedg = []
            wledge = []
            cmedge = []
            for _ in range(nedge):
                frqedg.append(binary_file.read_double())
                wledge.append(binary_file.read_double())
                cmedge.append(binary_file.read_double())
            binary_file.skip_record()

        return (
            nedge,
            torch.tensor(frqedg, dtype=torch.float64),
            torch.tensor(wledge, dtype=torch.float64),
            torch.tensor(cmedge, dtype=torch.float64),
        )

    def test_reads_opacity_edge_table_from_binary_record(self):
        nedge = 3
        triples = [
            (1.0, 10.0, 100.0),
            (2.0, 20.0, 200.0),
            (3.0, 30.0, 300.0),
        ]
        payload = struct.pack("<i", nedge) + b"".join(
            struct.pack("<ddd", frq, wle, cme)
            for frq, wle, cme in triples
        )
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(record)
            filename = handle.name

        try:
            opacity = ContinuumOpacityReader(filename).read_continuum_opacity()

            self.assertEqual(opacity.NEDGE, nedge)
            self.assertEqual(opacity.FRQEDG.shape, (nedge,))
            self.assertEqual(opacity.WLEDGE.shape, (nedge,))
            self.assertEqual(opacity.CMEDGE.shape, (nedge,))
            self.assertAlmostEqual(opacity.FRQEDG[0].item(), 1.0)
            self.assertAlmostEqual(opacity.WLEDGE[1].item(), 20.0)
            self.assertAlmostEqual(opacity.CMEDGE[2].item(), 300.0)
        finally:
            os.unlink(filename)

    def test_spectrv_reads_continuum_opacity_from_file9(self):
        nedge = 2
        triples = [
            (4.5, 40.0, 400.0),
            (5.5, 50.0, 500.0),
        ]
        payload = struct.pack("<i", nedge) + b"".join(
            struct.pack("<ddd", frq, wle, cme)
            for frq, wle, cme in triples
        )
        record = struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(record)
            filename = handle.name

        try:
            spectrv = Spectrv()
            opacity = spectrv.read_continuum_opacity_from_file9(filename)

            self.assertEqual(spectrv.NEDGE, nedge)
            self.assertAlmostEqual(spectrv.FRQEDG[0].item(), 4.5)
            self.assertAlmostEqual(opacity.WLEDGE[1].item(), 50.0)
            self.assertAlmostEqual(opacity.CMEDGE[0].item(), 400.0)
        finally:
            os.unlink(filename)

    def test_reads_asynth_vectors_after_spectrum_header_in_file9_mode(self):
        nrhox = 72
        nwave = 3
        header_payload = struct.pack("<dddiiifi", 100.0, 600000.0, 2850.0, 2009944, 72, 1, 1.5, 1)
        header_record = struct.pack("<i", len(header_payload)) + header_payload + struct.pack("<i", len(header_payload))

        nedge = 2
        triples = [(1.0, 10.0, 100.0), (2.0, 20.0, 200.0)]
        edge_payload = struct.pack("<i", nedge) + b"".join(
            struct.pack("<ddd", frq, wle, cme)
            for frq, wle, cme in triples
        )
        edge_record = struct.pack("<i", len(edge_payload)) + edge_payload + struct.pack("<i", len(edge_payload))

        asynth_records = []
        for row_index in range(nwave):
            values = [float(row_index * 100 + i) for i in range(99)]
            payload = b"".join(struct.pack("<f", value) for value in values)
            asynth_records.append(
                struct.pack("<i", len(payload)) + payload + struct.pack("<i", len(payload))
            )

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as handle:
            handle.write(header_record)
            handle.write(edge_record)
            for record in asynth_records:
                handle.write(record)
            filename = handle.name

        try:
            opacity = ContinuumOpacityReader(filename).read_continuum_opacity(
                include_asynth=True,
                mode="fort9",
                read_header=True,
                nrhox=nrhox,
                nwave=nwave,
            )

            self.assertEqual(opacity.ASYNTH.shape, (nwave, nrhox))
            self.assertAlmostEqual(opacity.ASYNTH[0, 0].item(), 0.0)
            self.assertAlmostEqual(opacity.ASYNTH[0, nrhox - 1].item(), float(nrhox - 1))
            self.assertAlmostEqual(opacity.ASYNTH[1, 0].item(), 100.0)
            self.assertAlmostEqual(opacity.ASYNTH[2, 0].item(), 200.0)
        finally:
            os.unlink(filename)

    def test_reads_opacity_edges_after_spectrum_header_from_reference_fort9(self):
        filename = "/home/dobos/project/kurucz-torch/data/tests/fort.9"

        with open(filename, "rb") as handle:
            header = SpectrumParametersReader(handle).read_spectrum_parameters()
            self.assertAlmostEqual(header.WLBEG, 100.0, places=6)
            self.assertAlmostEqual(header.RESOLU, 600000.0, places=6)
            self.assertAlmostEqual(header.WLEND, 2850.0, places=6)
            self.assertEqual(header.LENGTH, 2009944)
            self.assertEqual(header.N, 72)
            self.assertEqual(header.LINOUT, -1)
            self.assertAlmostEqual(header.TURBV, 1.5, places=6)
            self.assertEqual(header.IFVAC, 1)

            opacity = ContinuumOpacityReader(handle).read_continuum_opacity(
                include_asynth=True,
                mode="fort9",
                nrhox=header.N,
                nwave=header.LENGTH,
            )

            self.assertEqual(opacity.NEDGE, 344)
            self.assertEqual(len(opacity.FRQEDG), 344)
            self.assertAlmostEqual(opacity.FRQEDG[0].item(), 2.99792458e17, places=6)
            self.assertAlmostEqual(opacity.WLEDGE[0].item(), 1.0, places=6)
            self.assertAlmostEqual(opacity.CMEDGE[0].item(), 1.0e7, places=6)
            self.assertAlmostEqual(opacity.FRQEDG[-1].item(), -599584916000, places=6)
            self.assertAlmostEqual(opacity.WLEDGE[-1].item(), 500000, places=6)
            self.assertAlmostEqual(opacity.CMEDGE[-1].item(), -20, places=6)

            self.assertEqual(opacity.ASYNTH.shape, (header.LENGTH, header.N))
            self.assertAlmostEqual(opacity.ASYNTH[0, 0].item(), 70.0570297241211, places=6)
            self.assertAlmostEqual(opacity.ASYNTH[1, 0].item(), 69.70396423339844, places=6)
            self.assertAlmostEqual(opacity.ASYNTH[2, 0].item(), 69.65155792236328, places=6)

    def test_fort9_and_fort10_have_same_opacity_edges_up_to_absolute_value(self):
        fort9_nedge, fort9_frqedg, fort9_wledge, fort9_cmedge = self._read_edge_table_from_file(
            "/home/dobos/project/kurucz-torch/data/tests/fort.9", skip_prefix_records=1
        )
        fort10_nedge, fort10_frqedg, fort10_wledge, fort10_cmedge = self._read_edge_table_from_file(
            "/home/dobos/project/kurucz-torch/data/tests/fort.10", skip_prefix_records=1
        )

        self.assertEqual(fort9_nedge, 344)
        self.assertEqual(fort9_nedge, fort10_nedge)

        self.assertTrue(torch.allclose(torch.abs(fort9_frqedg), torch.abs(fort10_frqedg)))
        self.assertTrue(torch.allclose(torch.abs(fort9_wledge), torch.abs(fort10_wledge)))
        self.assertTrue(torch.allclose(torch.abs(fort9_cmedge), torch.abs(fort10_cmedge)))

        self.assertAlmostEqual(fort9_frqedg[0].item(), fort10_frqedg[0].item(), places=12)
        self.assertAlmostEqual(fort9_wledge[0].item(), fort10_wledge[0].item(), places=12)
        self.assertAlmostEqual(fort9_cmedge[0].item(), fort10_cmedge[0].item(), places=12)


if __name__ == "__main__":
    unittest.main()
