"""
Unit tests for Atmosphere

Tests the Atmosphere dataclass integration with the reader.
"""

import unittest
import sys
from pathlib import Path

# Add python module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

from kurucz.atmosphere import Atmosphere


class AtmosphereTests(unittest.TestCase):
    """Tests for Atmosphere dataclass"""
    
    def test_atmosphere_creation(self):
        """Test creating Atmosphere object"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=None)
        self.assertEqual(atm.TEFF, 5770.0)
        self.assertEqual(atm.GRAV, 1e4)
    
    def test_atmosphere_array_fields(self):
        """Test Atmosphere handles array fields"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=[1e-10, 1e-9])
        self.assertEqual(atm.RHOX, [1e-10, 1e-9])
        self.assertEqual(len(atm.RHOX), 2)
    
    def test_atmosphere_optional_fields(self):
        """Test Atmosphere handles optional fields"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=None)
        self.assertIsNone(atm.TITLE)
        self.assertEqual(atm.NLTEON, 0)
        self.assertEqual(atm.NUMITS, 0)


if __name__ == "__main__":
    unittest.main()
