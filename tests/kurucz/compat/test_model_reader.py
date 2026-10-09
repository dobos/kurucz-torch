"""
Unit tests for AtlasModelReader

Tests the ATLAS model reader implementation (READIN).
"""

import unittest
import sys
from pathlib import Path

# Add python module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

from kurucz.compat.model_reader import AtlasModelReader
from kurucz.atmosphere import Atmosphere


class AtlasModelReaderTests(unittest.TestCase):
    """Tests for AtlasModelReader main class"""
    
    def test_init(self):
        """Test AtlasModelReader initialization"""
        reader = AtlasModelReader()
        self.assertIsNotNone(reader)
        self.assertIsNone(reader.current_atm)
        self.assertIsNone(reader.reader)
    
    def test_read_model_minimal(self):
        """Test reading minimal test file"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm)
        self.assertIsInstance(atm, Atmosphere)
    
    def test_read_model_teff(self):
        """Test that TEFF is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertEqual(atm.TEFF, 5777.0)
    
    def test_read_model_gravity(self):
        """Test that GRAVITY is correctly read and converted"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Input gravity is 4.43 (log scale)
        # Should be converted to 10^4.43 ≈ 26900
        self.assertGreater(atm.GRAV, 26000)
        self.assertLess(atm.GRAV, 27000)
    
    def test_read_model_glog(self):
        """Test that GLOG is correctly computed"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # GLOG should be log10(GRAV)
        self.assertAlmostEqual(atm.GLOG, 4.43, places=2)
    
    def test_read_model_title(self):
        """Test that TITLE is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm.TITLE)
        self.assertIn("Solar Model", atm.TITLE)
    
    def test_read_model_nlteon(self):
        """Test that NLTEON flag is set correctly"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # File specifies LTE (not NLTE)
        self.assertEqual(atm.NLTEON, 0)
    
    def test_read_model_nrhox(self):
        """Test that NRHOX is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertEqual(atm.NRHOX, 3)
    
    def test_read_model_rhox_array(self):
        """Test that RHOX array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm.RHOX)
        self.assertEqual(len(atm.RHOX), 3)
        self.assertAlmostEqual(atm.RHOX[0], 1e-10, places=12)
        self.assertAlmostEqual(atm.RHOX[1], 1.2e-10, places=12)
        self.assertAlmostEqual(atm.RHOX[2], 1.44e-10, places=12)
    
    def test_read_model_temperature_array(self):
        """Test that temperature array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm.T)
        self.assertEqual(len(atm.T), 3)
        self.assertEqual(atm.T[0], 3800.0)
        self.assertEqual(atm.T[1], 3900.0)
        self.assertEqual(atm.T[2], 4000.0)
    
    def test_read_model_pressure_array(self):
        """Test that pressure array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm.P)
        self.assertEqual(len(atm.P), 3)
        self.assertEqual(atm.P[0], 10.0)
        self.assertAlmostEqual(atm.P[1], 11.0, places=2)
        self.assertAlmostEqual(atm.P[2], 12.1, places=2)
    
    def test_read_model_electron_density_array(self):
        """Test that electron density array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        self.assertIsNotNone(atm.XNE)
        self.assertEqual(len(atm.XNE), 3)
        self.assertEqual(atm.XNE[0], 1e8)
        self.assertAlmostEqual(atm.XNE[1], 1.1e8, delta=1e6)
        self.assertAlmostEqual(atm.XNE[2], 1.21e8, delta=1e6)
    
    def test_read_model_flux(self):
        """Test that FLUX is computed from TEFF"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # FLUX = 5.6697e-5/12.5664 * TEFF^4
        expected_flux = 5.6697e-5 / 12.5664 * (5777.0 ** 4)
        
        self.assertIsNotNone(atm.FLUX)
        self.assertAlmostEqual(atm.FLUX, expected_flux, delta=1e6)


class AtlasModelReaderEdgeCaseTests(unittest.TestCase):
    """Edge case tests for AtlasModelReader"""
    
    def test_multiple_reads_same_file(self):
        """Test reading same file multiple times"""
        reader = AtlasModelReader()
        
        atm1 = reader.read_model("tests/test_input_minimal.txt")
        atm2 = reader.read_model("tests/test_input_minimal.txt")
        
        # Both should have same values
        self.assertEqual(atm1.TEFF, atm2.TEFF)
        self.assertEqual(atm1.NRHOX, atm2.NRHOX)
    
    def test_gravity_log_scale_conversion(self):
        """Test that gravity < 10 is treated as log scale"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Input is 4.43 (log scale)
        # Should be converted to 10^4.43
        self.assertGreater(atm.GRAV, 10.0)  # Ensure it was converted
        
        # Verify GLOG is computed correctly
        import math
        expected_glog = math.log10(atm.GRAV)
        self.assertAlmostEqual(atm.GLOG, expected_glog, places=3)
    
    def test_flux_computation(self):
        """Test Stefan-Boltzmann flux calculation"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Formula: FLUX = 5.6697e-5/12.5664 * TEFF^4
        expected = 5.6697e-5 / 12.5664 * (atm.TEFF ** 4)
        
        self.assertAlmostEqual(atm.FLUX, expected, delta=1e6)
    
    def test_file_not_found(self):
        """Test error handling for missing files"""
        reader = AtlasModelReader()
        
        with self.assertRaises(IOError):
            reader.read_model("nonexistent_file.txt")


class AtlasModelReaderIntegrationTests(unittest.TestCase):
    """Integration tests for AtlasModelReader"""
    
    def test_full_workflow_minimal_file(self):
        """Test complete workflow with minimal test file"""
        reader = AtlasModelReader()
        
        # Read model
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Verify complete model
        self.assertEqual(atm.TEFF, 5777.0)
        self.assertEqual(atm.NRHOX, 3)
        self.assertEqual(len(atm.T), 3)
        self.assertEqual(len(atm.P), 3)
        self.assertEqual(len(atm.XNE), 3)
        self.assertEqual(len(atm.RHOX), 3)
    
    def test_full_workflow_standard_file(self):
        """Test complete workflow with standard 12-layer test file"""
        reader = AtlasModelReader()
        
        # Read model
        atm = reader.read_model("tests/test_input_standard.txt")
        
        # Verify complete model
        self.assertEqual(atm.TEFF, 5770.0)
        self.assertGreater(atm.GRAV, 20000)  # log scale converted
        self.assertEqual(atm.NRHOX, 12)
        self.assertEqual(len(atm.T), 12)
        self.assertEqual(len(atm.P), 12)
        self.assertEqual(len(atm.XNE), 12)
        self.assertEqual(len(atm.RHOX), 12)
        
        # Verify title
        self.assertIn("Standard Solar Model", atm.TITLE)
        
        # Verify LTE mode
        self.assertEqual(atm.NLTEON, 0)
        
        # Verify first and last layer values
        self.assertEqual(atm.T[0], 3800.0)
        self.assertEqual(atm.T[-1], 4350.0)
        self.assertEqual(atm.P[0], 10.0)
        self.assertAlmostEqual(atm.P[-1], 12.2, places=1)
        self.assertEqual(atm.XNE[0], 1e8)
        self.assertEqual(atm.RHOX[0], 1e-10)


if __name__ == "__main__":
    unittest.main()
