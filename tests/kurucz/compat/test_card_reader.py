"""
Unit tests for CardReader

Tests the ATLAS card deck parsing utility class.
"""

import unittest
import sys
from pathlib import Path

# Add python module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

from kurucz.compat.card_reader import CardReader


class CardReaderTests(unittest.TestCase):
    """Tests for CardReader utility class"""
    
    def setUp(self):
        """Create a CardReader instance for test file"""
        self.reader = CardReader("tests/test_input_minimal.txt")
    
    def test_init(self):
        """Test CardReader initialization"""
        reader = CardReader("tests/test_input_minimal.txt")
        self.assertIsNotNone(reader)
        self.assertIsNone(reader.current_line)
        self.assertEqual(reader.line_number, 0)
    
    def test_next_line(self):
        """Test reading lines sequentially"""
        line1 = self.reader.next_line()
        self.assertEqual(line1, "TEFF     5777.0")
        self.assertEqual(self.reader.line_number, 1)
        
        line2 = self.reader.next_line()
        self.assertEqual(line2, "GRAVITY  4.43")
        self.assertEqual(self.reader.line_number, 2)
    
    def test_extract_keyword(self):
        """Test keyword extraction"""
        line = self.reader.next_line()
        keyword = self.reader.extract_keyword(line)
        self.assertEqual(keyword, "TEFF")
        
        line = self.reader.next_line()
        keyword = self.reader.extract_keyword(line)
        self.assertEqual(keyword, "GRAVITY")
    
    def test_extract_keyword_compound(self):
        """Test extraction of compound keywords like 'READ T'"""
        # Skip to READ T line
        for _ in range(7):
            self.reader.next_line()
        
        line = self.reader.next_line()  # READ T
        keyword = self.reader.extract_keyword(line)
        self.assertEqual(keyword, "READ T")
    
    def test_parse_float_simple(self):
        """Test parsing simple floats"""
        line = self.reader.next_line()  # TEFF     5777.0
        keyword_end = line.find("TEFF") + len("TEFF")
        value = self.reader.parse_float(line, keyword_end)
        self.assertEqual(value, 5777.0)
    
    def test_parse_float_scientific(self):
        """Test parsing scientific notation"""
        # Skip to RHOX data line
        for _ in range(6):
            self.reader.next_line()
        
        line = self.reader.next_line()  # "  1.00e-10  1.20e-10  1.44e-10"
        values = [self.reader.parse_float(line, i) for i in range(len(line))]
        values = [v for v in values if v is not None]
        
        self.assertIn(1e-10, values)
        self.assertIn(1.2e-10, values)
        self.assertIn(1.44e-10, values)
    
    def test_read_float_array(self):
        """Test reading multi-line float arrays"""
        reader = CardReader("tests/test_input_minimal.txt")
        
        # Skip to line 6 (the count line)
        for _ in range(5):
            reader.next_line()
        
        reader.next_line()  # Read "3"
        
        # Read 3 floats
        values = reader.read_float_array(3)
        self.assertEqual(len(values), 3)
        self.assertAlmostEqual(values[0], 1e-10, places=12)
        self.assertAlmostEqual(values[1], 1.2e-10, places=12)
        self.assertAlmostEqual(values[2], 1.44e-10, places=12)
    
    def test_extract_keyword_empty_line(self):
        """Test that empty lines return empty keyword"""
        # Create a reader with data line (starts with spaces)
        reader = CardReader("tests/test_input_minimal.txt")
        # Skip to a data line
        for _ in range(6):
            reader.next_line()
        reader.next_line()  # CHANGE RHOX
        reader.next_line()  # "3"
        line = reader.next_line()  # Data line "  1.00e-10  ..."
        
        keyword = reader.extract_keyword(line)
        self.assertEqual(keyword, "")  # Data line has no keyword
    
    def test_parse_float_with_plus_sign(self):
        """Test parsing floats with explicit plus sign"""
        line = "SOME_DATA +1.00e+10"
        value = self.reader.parse_float(line, 10)
        self.assertEqual(value, 1.0e10)
    
    def test_parse_float_with_minus_sign(self):
        """Test parsing floats with minus sign"""
        line = "SOME_DATA -1.00e-10"
        value = self.reader.parse_float(line, 10)
        self.assertEqual(value, -1.0e-10)
    
    def test_parse_int(self):
        """Test parsing integers"""
        line = "NRHOX 72"
        keyword_end = line.find("NRHOX") + len("NRHOX")
        value = self.reader.parse_int(line, keyword_end)
        self.assertEqual(value, 72)


if __name__ == "__main__":
    unittest.main()
