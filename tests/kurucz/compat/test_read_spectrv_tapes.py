from gzip import READ
from unittest import TestCase

from kurucz.compat.atmospherereader import AtmosphereReader
from kurucz.compat.opacityvectorreader import OpacityVectorReader
from kurucz.compat.spectrumparametersreader import SpectrumParametersReader
from kurucz.compat.continuumopacityreader import ContinuumOpacityReader
from kurucz.compat.linelistreader import LineListReader
from kurucz.fortran.binaryfile import BinaryFile

class TestReadSpectrvTapes(TestCase):
    def test_read_tape9(self):
        filename = "/home/dobos/project/kurucz-torch/data/tests/fort.9"

        with open(filename, "rb") as f:
            # spectrv.patched.for:223
            # READ(9)WLBEG,RESOLU,WLEND,LENGTH,N,LINOUT,TURBV,IFVAC
            reader = SpectrumParametersReader(f)
            spectrum_parameters = reader.read_spectrum_parameters()

            self.assertEqual(spectrum_parameters.N, 72)
            self.assertEqual(spectrum_parameters.LENGTH, 2009944)
            self.assertEqual(spectrum_parameters.WLBEG, 100.0)
            self.assertEqual(f.tell(), 0x34)

            # spectrv.patched.for:224
            # READ(9)NEDGE,(FRQEDG(IEDGE),WLEDGE(IEDGE),CMEDGE(IEDGE),IEDGE=1,NEDGE)
            reader = ContinuumOpacityReader(f)
            continuum_opacity = reader.read_continuum_edges()

            self.assertEqual(continuum_opacity.NEDGE, 344)
            self.assertEqual(continuum_opacity.FRQEDG.shape[0], 344)
            self.assertEqual(continuum_opacity.WLEDGE.shape[0], 344)
            self.assertEqual(continuum_opacity.CMEDGE.shape[0], 344)
            self.assertEqual(f.tell(), 0x26c0)

            # spectrv.patched.for:317
            # READ(9)ASYNTH
            reader = OpacityVectorReader(f)
            opacity_vectors = reader.read_opacity_vectors(
                nrhox=spectrum_parameters.N,
                nwave=spectrum_parameters.LENGTH
            )

            self.assertEqual(opacity_vectors.NRHOX, 72)
            self.assertEqual(opacity_vectors.NWAVE, 2009944)
            self.assertEqual(opacity_vectors.ASYNTH.shape, (2009944, 72))
            self.assertEqual(f.tell(), 0x30668da0)

            # :359
            # READ(9)NLINES
            # :368
            # READ(9)LINDAT8I,LABEL,LABELP,OTHER1,OTHER2,LINDAT8II,LINDAT4I,REF,LINDAT4II,ALINEC
            reader = LineListReader(f)
            line_list = reader.read_line_list(spectrum_parameters.N)

            self.assertEqual(line_list.NLINES, 0)  # Example expected value

            # End of file
            self.assertEqual(f.peek(), b'')

    def test_read_tape10(self):
        filename = "/home/dobos/project/kurucz-torch/data/tests/fort.10"

        with open(filename, "rb") as f:
            # spectrv.patched.for:137
            # READ(10)
            binary_file = BinaryFile(f)
            binary_file.start_record()
            binary_file.skip_record()
            self.assertEqual(f.tell(), 0x66)

            # spectrv.patched.for:138
            # READ(10)NEDGE,(FRQEDG(IEDGE),WLEDGE(IEDGE),CMEDGE(IEDGE),IEDGE=1,NEDGE)
            reader = ContinuumOpacityReader(f)
            continuum_opacity = reader.read_continuum_edges()

            self.assertEqual(continuum_opacity.NEDGE, 344)
            self.assertEqual(continuum_opacity.FRQEDG.shape[0], 344)
            self.assertEqual(continuum_opacity.WLEDGE.shape[0], 344)
            self.assertEqual(continuum_opacity.CMEDGE.shape[0], 344)
            self.assertEqual(f.tell(), 0x26f2)

            # spectrv.patched.for:142
            # READ(10)NCON,(CONFRQ(NU),NU=1,NCON)
            reader = ContinuumOpacityReader(f)
            continuum_opacity = reader.read_continuum_frequencies()

            self.assertEqual(continuum_opacity.NCON, 1029)
            self.assertEqual(continuum_opacity.CONFRQ.shape, (1029,))
            self.assertEqual(f.tell(), 0x4726)

            # spectrv.patched.for:149
            # READ(10)
            binary_file = BinaryFile(f)
            binary_file.start_record()
            binary_file.skip_record()
            self.assertEqual(f.tell(), 0x78ae)

            # TODO: read continuum absorption and scattering
            # spectrv.patched.for:152
            # READ(10)
            # READ(10)QCONTABS
            # READ(10)QCONTSCAT
            # READ(10)
            reader = ContinuumOpacityReader(f)
            continuum_opacity = reader.read_continuum_abs_scat(72)

            self.assertEqual(continuum_opacity.QCONTABS.shape, (72, 1131))
            self.assertEqual(continuum_opacity.QCONTSCAT.shape, (72, 1131))
            self.assertEqual(f.tell(), 0x2cfcee)

            # End of file
            self.assertEqual(f.peek(), b'')

    def test_read_output_synthe(self):
        filename = "/home/dobos/project/kurucz-torch/data/tests/output_synthe.out"

        with open(filename, "rb") as f:
            reader = AtmosphereReader(f)
            atmosphere = reader.read_atmosphere()

            pass