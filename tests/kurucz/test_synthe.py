import os
import tempfile
import unittest

from kurucz.synthe import Synthe


class TestSynthe(unittest.TestCase):
    def test_synthe_initialization(self):
        """Test that Synthe can be initialized properly."""
        synthe = Synthe()
        self.assertIsNone(synthe.atmosphere)
        self.assertIsNone(synthe.spectrum_parameters)
        self.assertIsNone(synthe.continuum_opacity)
        self.assertIsNone(synthe.line_list)
        
    def test_synthe_attributes(self):
        """Test that Synthe has the expected attributes."""
        synthe = Synthe()
        self.assertTrue(hasattr(synthe, 'atmosphere'))
        self.assertTrue(hasattr(synthe, 'spectrum_parameters'))
        self.assertTrue(hasattr(synthe, 'continuum_opacity'))
        self.assertTrue(hasattr(synthe, 'line_list'))
        self.assertTrue(hasattr(synthe, 'NRHOX'))
        self.assertTrue(hasattr(synthe, 'LENGTH'))
        self.assertTrue(hasattr(synthe, 'NEDGE'))
        self.assertTrue(hasattr(synthe, 'NCON'))


if __name__ == "__main__":
    unittest.main()