import unittest
import tempfile
import os

import torch

from kurucz.compat.linelistreader import LineListReader
from kurucz.compat.spectrumparametersreader import SpectrumParametersReader
from kurucz.compat.continuumopacityreader import ContinuumOpacityReader
from kurucz.linelist import LineList


class TestLineListReader(unittest.TestCase):
    """Test cases for LineListReader class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dat')
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        os.unlink(self.temp_file.name)

    def test_line_list_dataclass(self):
        """Test that LineList dataclass can be instantiated."""
        line_list = LineList()
        self.assertIsInstance(line_list, LineList)
        
        # Test that all fields are initialized as None by default
        self.assertIsNone(line_list.WL)
        self.assertIsNone(line_list.E)
        self.assertIsNone(line_list.EP)
        self.assertIsNone(line_list.LABEL)
        self.assertIsNone(line_list.LABELP)
        self.assertIsNone(line_list.OTHER1)
        self.assertIsNone(line_list.OTHER2)
        self.assertIsNone(line_list.WLVAC)
        self.assertIsNone(line_list.CENTER)
        self.assertIsNone(line_list.CONCEN)
        self.assertIsNone(line_list.NELION)
        self.assertIsNone(line_list.GAMMAR)
        self.assertIsNone(line_list.GAMMAS)
        self.assertIsNone(line_list.GAMMAW)
        self.assertIsNone(line_list.REF)
        self.assertIsNone(line_list.NBLO)
        self.assertIsNone(line_list.NBUP)
        self.assertIsNone(line_list.ISO1)
        self.assertIsNone(line_list.X1)
        self.assertIsNone(line_list.ISO2)
        self.assertIsNone(line_list.X2)
        self.assertIsNone(line_list.GFLOG)
        self.assertIsNone(line_list.XJ)
        self.assertIsNone(line_list.XJP)
        self.assertIsNone(line_list.CODE)
        self.assertIsNone(line_list.ELO)
        self.assertIsNone(line_list.GF)
        self.assertIsNone(line_list.GS)
        self.assertIsNone(line_list.GR)
        self.assertIsNone(line_list.GW)
        self.assertIsNone(line_list.DWL)
        self.assertIsNone(line_list.DGFLOG)
        self.assertIsNone(line_list.DGAMMAR)
        self.assertIsNone(line_list.DGAMMAS)
        self.assertIsNone(line_list.DGAMMAW)
        self.assertIsNone(line_list.EXTRA1)
        self.assertIsNone(line_list.EXTRA2)
        self.assertIsNone(line_list.EXTRA3)
        self.assertIsNone(line_list.ALINEC)

    def test_line_list_reader_instantiation(self):
        """Test that LineListReader can be instantiated."""
        reader = LineListReader(self.temp_file.name)
        self.assertIsInstance(reader, LineListReader)

    def test_read_line_list_from_reference_fort9(self):
        """Test reading line list from reference fort.9 file."""

        with open("/home/dobos/project/kurucz-torch/data/tests/fort.9", "rb") as f:
            # Read spectrum parameters first (as done in Fortran program)
            spectrum_reader = SpectrumParametersReader(f)
            spectrum_params = spectrum_reader.read_spectrum_parameters()
            
            # Read continuum opacity data (as done in Fortran program)
            continuum_reader = ContinuumOpacityReader(f)
            continuum_opacity = continuum_reader.read_continuum_opacity(
                include_asynth=True,
                mode="fort9",
            )
            
            # Now read the line list (as done in Fortran program)
            reader = LineListReader(f)
            line_list = reader.read_line_list(spectrum_params.N)
        
        # Verify that we got some data
        self.assertIsNotNone(line_list)
        self.assertIsNotNone(line_list.WL)
        self.assertIsNotNone(line_list.E)
        self.assertIsNotNone(line_list.EP)
        self.assertIsNotNone(line_list.LABEL)
        self.assertIsNotNone(line_list.LABELP)
        self.assertIsNotNone(line_list.OTHER1)
        self.assertIsNotNone(line_list.OTHER2)
        self.assertIsNotNone(line_list.WLVAC)
        self.assertIsNotNone(line_list.CENTER)
        self.assertIsNotNone(line_list.CONCEN)
        self.assertIsNotNone(line_list.NELION)
        self.assertIsNotNone(line_list.GAMMAR)
        self.assertIsNotNone(line_list.GAMMAS)
        self.assertIsNotNone(line_list.GAMMAW)
        self.assertIsNotNone(line_list.REF)
        self.assertIsNotNone(line_list.NBLO)
        self.assertIsNotNone(line_list.NBUP)
        self.assertIsNotNone(line_list.ISO1)
        self.assertIsNotNone(line_list.X1)
        self.assertIsNotNone(line_list.ISO2)
        self.assertIsNotNone(line_list.X2)
        self.assertIsNotNone(line_list.GFLOG)
        self.assertIsNotNone(line_list.XJ)
        self.assertIsNotNone(line_list.XJP)
        self.assertIsNotNone(line_list.CODE)
        self.assertIsNotNone(line_list.ELO)
        self.assertIsNotNone(line_list.GF)
        self.assertIsNotNone(line_list.GS)
        self.assertIsNotNone(line_list.GR)
        self.assertIsNotNone(line_list.GW)
        self.assertIsNotNone(line_list.DWL)
        self.assertIsNotNone(line_list.DGFLOG)
        self.assertIsNotNone(line_list.DGAMMAR)
        self.assertIsNotNone(line_list.DGAMMAS)
        self.assertIsNotNone(line_list.DGAMMAW)
        self.assertIsNotNone(line_list.EXTRA1)
        self.assertIsNotNone(line_list.EXTRA2)
        self.assertIsNotNone(line_list.EXTRA3)
        self.assertIsNotNone(line_list.ALINEC)
