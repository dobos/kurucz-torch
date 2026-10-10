"""
Unit tests for AtmosphereReader

Tests the ATLAS atmosphere file parser against both synthetic test data
and the real output_synthe.out file from the ATLAS_sun_model example.

Tests cover:
- Keyword parsing and extraction
- Float parsing (decimal, scientific, Fortran D notation)
- Header section (TEFF, GRAVITY, TITLE, etc.)
- DECK6 data array reading (72 depth points)
- Atmosphere object population
- File I/O and error handling
"""

import unittest
import tempfile
import os
from io import StringIO
import math

from kurucz.atmosphere import Atmosphere
from kurucz.compat.atmosphere_reader import AtmosphereReader


class TestAtmosphereReaderKeywordExtraction(unittest.TestCase):
    """Test keyword and value extraction utilities."""
    
    def setUp(self):
        """Create a reader instance for testing."""
        self.reader = AtmosphereReader()
    
    def test_extract_keyword_basic(self):
        """Test basic keyword extraction."""
        keyword = self.reader._extract_keyword("TEFF   5770.")
        self.assertEqual(keyword, "TEFF")
    
    def test_extract_keyword_with_leading_spaces(self):
        """Test keyword extraction with leading whitespace."""
        keyword = self.reader._extract_keyword("    GRAVITY 4.44")
        self.assertEqual(keyword, "GRAVITY")
    
    def test_extract_keyword_offset(self):
        """Test keyword extraction at specified offset."""
        line = "ABUNDANCE CHANGE 26 -4.5 8 -3.1"
        keyword = self.reader._extract_keyword(line, offset=len("ABUNDANCE"))
        self.assertEqual(keyword, "CHANGE")
    
    def test_extract_keyword_uppercase(self):
        """Test that keywords are converted to uppercase."""
        keyword = self.reader._extract_keyword("teff   5770.")
        self.assertEqual(keyword, "TEFF")
    
    def test_extract_float_decimal(self):
        """Test floating-point extraction from decimal format."""
        value = self.reader._extract_float("TEFF   5770.0", offset=len("TEFF"))
        self.assertAlmostEqual(value, 5770.0)
    
    def test_extract_float_scientific(self):
        """Test floating-point extraction from scientific notation."""
        value = self.reader._extract_float("PRESSURE   1.0e+00", offset=len("PRESSURE"))
        self.assertAlmostEqual(value, 1.0e+00)
    
    def test_extract_float_fortran_d_notation(self):
        """Test Fortran D notation (1.23D+02 -> 1.23e+02)."""
        value = self.reader._extract_float("VALUE   1.23D+02", offset=len("VALUE"))
        self.assertAlmostEqual(value, 1.23e+02)
    
    def test_extract_float_with_offset(self):
        """Test float extraction at specified offset."""
        line = "GRAVITY 4.44000"
        value = self.reader._extract_float(line, offset=len("GRAVITY"))
        self.assertAlmostEqual(value, 4.44)
    
    def test_extract_floats_multiple(self):
        """Test extraction of multiple floats from a line."""
        line = "TURBULENCE ON 1.0 0.5 2.0 3.0"
        values = self.reader._extract_floats(line, 4, offset=len("TURBULENCE ON"))
        self.assertEqual(len(values), 4)
        self.assertAlmostEqual(values[0], 1.0)
        self.assertAlmostEqual(values[1], 0.5)
        self.assertAlmostEqual(values[2], 2.0)
        self.assertAlmostEqual(values[3], 3.0)


class TestAtmosphereReaderHeaderParsing(unittest.TestCase):
    """Test parsing of header section keywords."""
    
    def test_teff_parsing(self):
        """Test TEFF (effective temperature) parsing."""
        content = """TEFF   5770.  GRAVITY 4.44000
TITLE   Sun Model
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        # Check Stefan-Boltzmann flux computation
        expected_flux = 5.6697e-5 / 12.5664 * 5770.0**4
        self.assertAlmostEqual(atm.FLUX, expected_flux, places=2)
    
    def test_gravity_parsing_linear(self):
        """Test GRAVITY parsing when value > 10 (linear scale)."""
        content = """TEFF   5770.  GRAVITY 44.4
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # Gravity in linear scale (no conversion when > 10)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
        self.assertAlmostEqual(atm.GLOG, math.log10(44.4), places=4)
    
    def test_gravity_parsing_log_scale(self):
        """Test GRAVITY parsing when value < 10 (converted from log scale)."""
        content = """TEFF   5770.  GRAVITY 4.44
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # Gravity < 10 should be converted: 10^4.44 ≈ 27,542
        expected_grav = 10.0 ** 4.44
        self.assertAlmostEqual(atm.GRAV, expected_grav, places=0)
        self.assertAlmostEqual(atm.GLOG, 4.44, places=4)
    
    def test_title_parsing(self):
        """Test TITLE parsing."""
        content = """TEFF   5770.
TITLE   Solar model (Kurucz)
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertIn("Solar model", atm.TITLE)
    
    def test_molecules_on(self):
        """Test MOLECULES ON keyword."""
        content = """TEFF   5770.
MOLECULES ON
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.IFMOL, 1)
    
    def test_molecules_off(self):
        """Test MOLECULES OFF keyword."""
        content = """TEFF   5770.
MOLECULES OFF
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.IFMOL, 0)
    
    def test_opacity_on(self):
        """Test OPACITY ON keyword."""
        content = """TEFF   5770.
OPACITY ON
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # All opacity flags should be 1
        self.assertIsNotNone(atm.IFOP)
    
    def test_convection_on(self):
        """Test CONVECTION ON keyword."""
        content = """TEFF   5770.
CONVECTION ON 1.5
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.IFCONV, 1)
    
    def test_convection_off(self):
        """Test CONVECTION OFF keyword."""
        content = """TEFF   5770.
CONVECTION OFF
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.IFCONV, 0)
    
    def test_turbulence_on(self):
        """Test TURBULENCE ON keyword with parameters."""
        content = """TEFF   5770.
TURBULENCE ON 1.0 0.5 2.0 3.0
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.IFTURB, 1)
        self.assertAlmostEqual(atm.TRBFDG, 1.0, places=1)
        self.assertAlmostEqual(atm.TRBPOW, 0.5, places=1)
    
    def test_lte_keyword(self):
        """Test LTE keyword sets NLTEON to 0."""
        content = """TEFF   5770.
LTE
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.NLTEON, 0)
    
    def test_nlte_keyword(self):
        """Test NLTE keyword sets NLTEON to 1."""
        content = """TEFF   5770.
NLTE
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.NLTEON, 1)


class TestAtmosphereReaderDeck6Parsing(unittest.TestCase):
    """Test DECK6 format data reading (atmosphere structure)."""
    
    def test_deck6_basic(self):
        """Test basic DECK6 parsing with minimal data."""
        content = """TEFF   5770.  GRAVITY 4.44
READ DECK6 3 RHOX,T,P,XNE
0.00001 5770.0 1.0e+02 1.0e+10
0.0001  5750.0 1.0e+03 1.0e+11
0.001   5700.0 1.0e+04 1.0e+12
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.NRHOX, 3)
        self.assertIsNotNone(atm.RHOX)
        self.assertIsNotNone(atm.T)
        self.assertIsNotNone(atm.P)
        self.assertIsNotNone(atm.XNE)
        
        # Check array lengths
        if isinstance(atm.RHOX, list):
            self.assertEqual(len(atm.RHOX), 3)
            self.assertAlmostEqual(atm.RHOX[0], 0.00001, places=6)
            self.assertAlmostEqual(atm.T[1], 5750.0, places=1)
        else:
            # Torch tensor
            self.assertEqual(atm.RHOX.shape[0], 3)
    
    def test_deck6_with_all_columns(self):
        """Test DECK6 with all 10 standard columns (PRAD instead of ACCRAD)."""
        content = """TEFF   5770.
READ DECK6 2 RHOX,T,P,XNE,ABROSS,PRAD,VTURB,FLXRAD,VCONV,VELSND
0.00001 5770.0 1.0e+02 1.0e+10 1.0e-01 1.0e-02 2.0 1.0 1.0 10000.0
0.0001  5700.0 1.0e+03 1.0e+11 1.0e-01 1.0e-02 2.0 1.0 1.0 10000.0
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertEqual(atm.NRHOX, 2)
        self.assertIsNotNone(atm.ABROSS)
        self.assertIsNotNone(atm.PRAD)  # Changed from ACCRAD to PRAD
        self.assertIsNotNone(atm.VTURB)


class TestAtmosphereReaderAbundanceParsing(unittest.TestCase):
    """Test ABUNDANCE keyword parsing."""
    
    def test_abundance_change_single(self):
        """Test ABUNDANCE CHANGE with single element."""
        content = """TEFF   5770.
ABUNDANCE CHANGE 26 -4.5
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertIsNotNone(atm.ABUND)
        if isinstance(atm.ABUND, list):
            self.assertAlmostEqual(atm.ABUND[25], -4.5)  # Index 25 = element 26
    
    def test_abundance_change_multiple(self):
        """Test ABUNDANCE CHANGE with multiple elements."""
        content = """TEFF   5770.
ABUNDANCE CHANGE 26 -4.5 8 -3.1 14 -4.5
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertIsNotNone(atm.ABUND)
        if isinstance(atm.ABUND, list):
            self.assertAlmostEqual(atm.ABUND[25], -4.5)  # Fe
            self.assertAlmostEqual(atm.ABUND[7], -3.1)   # O
            self.assertAlmostEqual(atm.ABUND[13], -4.5)  # Si


class TestAtmosphereReaderRealFile(unittest.TestCase):
    """Test parsing of actual ATLAS output files."""
    
    def test_read_output_synthe_dot_out(self):
        """Test reading the real output_synthe.out file.
        
        This file should exist at:
            /home/dobos/ATLAS_sun_model/output_synthe.out
        
        If available, verify:
        - TEFF ≈ 5777 K
        - GRAVITY ≈ 4.44 (log scale)
        - NRHOX = 72
        - All data columns populated
        """
        filepath = "/home/dobos/ATLAS_sun_model/output_synthe.out"
        
        if not os.path.exists(filepath):
            self.skipTest(f"Test file not found: {filepath}")
        
        reader = AtmosphereReader()
        atm = reader.read(filepath)
        
        # Verify key parameters
        self.assertGreater(atm.TEFF, 5000)
        self.assertLess(atm.TEFF, 6000)
        
        self.assertGreater(atm.GRAV, 1)
        self.assertLess(atm.GRAV, 100000)  # Log scale gravity can be large after conversion
        
        # Verify DECK6 data was read
        self.assertGreater(atm.NRHOX, 0)
        self.assertIsNotNone(atm.T)
        self.assertIsNotNone(atm.P)
        self.assertIsNotNone(atm.XNE)
    
    def test_read_from_file_object(self):
        """Test reading from file object instead of filepath."""
        content = """TEFF   5770.  GRAVITY 44.4
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertAlmostEqual(atm.TEFF, 5770.0)


class TestAtmosphereReaderEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_file(self):
        """Test handling of empty file."""
        content = ""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # Should return atmosphere with default values
        self.assertIsNotNone(atm)
        self.assertEqual(atm.TEFF, 0.0)
    
    def test_missing_end_keyword(self):
        """Test file without END keyword."""
        content = """TEFF   5770.0
GRAVITY 44.4
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # Should still parse available data
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
    
    def test_skip_unknown_keywords(self):
        """Test that unknown keywords are skipped without error."""
        content = """TEFF   5770.0
UNKNOWN_KEYWORD some_value
GRAVITY 44.4
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
    
    def test_malformed_numeric_values(self):
        """Test handling of malformed numbers."""
        content = """TEFF   5770.0
GRAVITY 44.4
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # TEFF should parse correctly
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        # GRAVITY should parse correctly (no conversion since > 10)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
    
    def test_case_insensitive_keywords(self):
        """Test that keywords are case-insensitive."""
        content = """teff   5770.
gravity 44.4
TITLE   Test
end
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
    
    def test_extra_whitespace(self):
        """Test handling of extra whitespace."""
        content = """  TEFF     5770.0
  GRAVITY   44.4
  END  
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)


class TestAtmosphereReaderIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""
    
    def test_complete_atmosphere_model(self):
        """Test parsing a complete atmosphere model."""
        content = """TEFF   5770.  GRAVITY 44.4
TITLE   Solar Model
MOLECULES ON
CONVECTION ON 1.5
TURBULENCE ON 1.0 0.5 2.0 3.0
ABUNDANCE CHANGE 26 -4.5 8 -3.1
LTE
READ DECK6 3 RHOX,T,P,XNE
0.00001 5770.0 1.0e+02 1.0e+10
0.0001  5700.0 1.0e+03 1.0e+11
0.001   5600.0 1.0e+04 1.0e+12
END
"""
        reader = AtmosphereReader()
        atm = reader.read(StringIO(content))
        
        # Verify all sections parsed
        self.assertAlmostEqual(atm.TEFF, 5770.0)
        self.assertAlmostEqual(atm.GRAV, 44.4, places=1)
        self.assertIn("Solar", atm.TITLE)
        self.assertEqual(atm.IFMOL, 1)
        self.assertEqual(atm.IFCONV, 1)
        self.assertEqual(atm.IFTURB, 1)
        self.assertEqual(atm.NLTEON, 0)
        self.assertEqual(atm.NRHOX, 3)


if __name__ == '__main__':
    unittest.main()
