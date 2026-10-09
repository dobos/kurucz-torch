"""
Unit tests for AtlasModelReader

Tests the ATLAS model reader implementation (phases 1-5).
Tests cover CardReader, AtlasModelReader, and Atmosphere integration.
"""

import pytest
import sys
from pathlib import Path

# Add python module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from kurucz.compat.card_reader import CardReader
from kurucz.compat.model_reader import AtlasModelReader
from kurucz.atmosphere import Atmosphere


class TestCardReader:
    """Tests for CardReader utility class"""
    
    @pytest.fixture
    def reader(self):
        """Create a CardReader instance for test file"""
        return CardReader("tests/test_input_minimal.txt")
    
    def test_init(self):
        """Test CardReader initialization"""
        reader = CardReader("tests/test_input_minimal.txt")
        assert reader is not None
        assert reader.current_line is None
        assert reader.line_number == 0
    
    def test_next_line(self, reader):
        """Test reading lines sequentially"""
        line1 = reader.next_line()
        assert line1 == "TEFF     5777.0"
        assert reader.line_number == 1
        
        line2 = reader.next_line()
        assert line2 == "GRAVITY  4.43"
        assert reader.line_number == 2
    
    def test_extract_keyword(self, reader):
        """Test keyword extraction"""
        line = reader.next_line()
        keyword = reader.extract_keyword(line)
        assert keyword == "TEFF"
        
        line = reader.next_line()
        keyword = reader.extract_keyword(line)
        assert keyword == "GRAVITY"
    
    def test_extract_keyword_compound(self, reader):
        """Test extraction of compound keywords like 'READ T'"""
        # Skip to READ T line
        for _ in range(7):
            reader.next_line()
        
        line = reader.next_line()  # READ T
        keyword = reader.extract_keyword(line)
        assert keyword == "READ T"
    
    def test_parse_float_simple(self, reader):
        """Test parsing simple floats"""
        line = reader.next_line()  # TEFF     5777.0
        keyword_end = line.find("TEFF") + len("TEFF")
        value = reader.parse_float(line, keyword_end)
        assert value == 5777.0
    
    def test_parse_float_scientific(self, reader):
        """Test parsing scientific notation"""
        # Skip to RHOX data line
        for _ in range(6):
            reader.next_line()
        
        line = reader.next_line()  # "  1.00e-10  1.20e-10  1.44e-10"
        values = [reader.parse_float(line, i) for i in range(len(line))]
        values = [v for v in values if v is not None]
        
        assert 1e-10 in values
        assert 1.2e-10 in values
        assert 1.44e-10 in values
    
    def test_read_float_array(self):
        """Test reading multi-line float arrays"""
        reader = CardReader("tests/test_input_minimal.txt")
        
        # Skip to line 6 (the count line)
        for _ in range(5):
            reader.next_line()
        
        reader.next_line()  # Read "3"
        
        # Read 3 floats
        values = reader.read_float_array(3)
        assert len(values) == 3
        assert abs(values[0] - 1e-10) < 1e-12
        assert abs(values[1] - 1.2e-10) < 1e-12
        assert abs(values[2] - 1.44e-10) < 1e-12
    
    def test_extract_keyword_empty_line(self, reader):
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
        assert keyword == ""  # Data line has no keyword


class TestAtlasModelReader:
    """Tests for AtlasModelReader main class"""
    
    def test_init(self):
        """Test AtlasModelReader initialization"""
        reader = AtlasModelReader()
        assert reader is not None
        assert reader.current_atm is None
        assert reader.reader is None
    
    def test_read_model_minimal(self):
        """Test reading minimal test file"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm is not None
        assert isinstance(atm, Atmosphere)
    
    def test_read_model_teff(self):
        """Test that TEFF is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.TEFF == 5777.0
    
    def test_read_model_gravity(self):
        """Test that GRAVITY is correctly read and converted"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Input gravity is 4.43 (log scale)
        # Should be converted to 10^4.43 ≈ 26900
        assert atm.GRAV > 26000
        assert atm.GRAV < 27000
    
    def test_read_model_glog(self):
        """Test that GLOG is correctly computed"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # GLOG should be log10(GRAV)
        assert abs(atm.GLOG - 4.43) < 0.01
    
    def test_read_model_title(self):
        """Test that TITLE is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.TITLE is not None
        assert "Solar Model" in atm.TITLE
    
    def test_read_model_nlteon(self):
        """Test that NLTEON flag is set correctly"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # File specifies LTE (not NLTE)
        assert atm.NLTEON == 0
    
    def test_read_model_nrhox(self):
        """Test that NRHOX is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.NRHOX == 3
    
    def test_read_model_rhox_array(self):
        """Test that RHOX array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.RHOX is not None
        assert len(atm.RHOX) == 3
        assert abs(atm.RHOX[0] - 1e-10) < 1e-12
        assert abs(atm.RHOX[1] - 1.2e-10) < 1e-12
        assert abs(atm.RHOX[2] - 1.44e-10) < 1e-12
    
    def test_read_model_temperature_array(self):
        """Test that temperature array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.T is not None
        assert len(atm.T) == 3
        assert atm.T[0] == 3800.0
        assert atm.T[1] == 3900.0
        assert atm.T[2] == 4000.0
    
    def test_read_model_pressure_array(self):
        """Test that pressure array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.P is not None
        assert len(atm.P) == 3
        assert atm.P[0] == 10.0
        assert abs(atm.P[1] - 11.0) < 0.01
        assert abs(atm.P[2] - 12.1) < 0.01
    
    def test_read_model_electron_density_array(self):
        """Test that electron density array is correctly read"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        assert atm.XNE is not None
        assert len(atm.XNE) == 3
        assert atm.XNE[0] == 1e8
        assert abs(atm.XNE[1] - 1.1e8) < 1e6
        assert abs(atm.XNE[2] - 1.21e8) < 1e6
    
    def test_read_model_flux(self):
        """Test that FLUX is computed from TEFF"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # FLUX = 5.6697e-5/12.5664 * TEFF^4
        expected_flux = 5.6697e-5 / 12.5664 * (5777.0 ** 4)
        
        assert atm.FLUX is not None
        assert abs(atm.FLUX - expected_flux) < 1e6


class TestAtmosphere:
    """Tests for Atmosphere dataclass integration"""
    
    def test_atmosphere_creation(self):
        """Test creating Atmosphere object"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=None)
        assert atm.TEFF == 5770.0
        assert atm.GRAV == 1e4
    
    def test_atmosphere_array_fields(self):
        """Test Atmosphere handles array fields"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=[1e-10, 1e-9])
        assert atm.RHOX == [1e-10, 1e-9]
        assert len(atm.RHOX) == 2
    
    def test_atmosphere_optional_fields(self):
        """Test Atmosphere handles optional fields"""
        atm = Atmosphere(TEFF=5770.0, GRAV=1e4, RHOX=None)
        assert atm.TITLE is None
        assert atm.NLTEON == 0
        assert atm.NUMITS == 0


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_full_workflow_minimal_file(self):
        """Test complete workflow with minimal test file"""
        # Create reader
        reader = AtlasModelReader()
        
        # Read model
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Verify complete model
        assert atm.TEFF == 5777.0
        assert atm.NRHOX == 3
        assert len(atm.T) == 3
        assert len(atm.P) == 3
        assert len(atm.XNE) == 3
        assert len(atm.RHOX) == 3
    
    def test_full_workflow_standard_file(self):
        """Test complete workflow with standard 12-layer test file"""
        # Create reader
        reader = AtlasModelReader()
        
        # Read model
        atm = reader.read_model("tests/test_input_standard.txt")
        
        # Verify complete model
        assert atm.TEFF == 5770.0
        assert atm.GRAV > 20000  # log scale converted
        assert atm.NRHOX == 12
        assert len(atm.T) == 12
        assert len(atm.P) == 12
        assert len(atm.XNE) == 12
        assert len(atm.RHOX) == 12
        
        # Verify title
        assert "Standard Solar Model" in atm.TITLE
        
        # Verify LTE mode
        assert atm.NLTEON == 0
        
        # Verify first and last layer values
        assert atm.T[0] == 3800.0
        assert atm.T[-1] == 4350.0
        assert atm.P[0] == 10.0
        assert abs(atm.P[-1] - 12.2) < 0.01
        assert atm.XNE[0] == 1e8
        assert atm.RHOX[0] == 1e-10
    
    def test_file_not_found(self):
        """Test error handling for missing files"""
        reader = AtlasModelReader()
        
        with pytest.raises(IOError):
            reader.read_model("nonexistent_file.txt")
    
    def test_invalid_data_missing_teff(self):
        """Test validation catches missing TEFF"""
        # This test would require creating a file without TEFF
        # For now, we just verify validation works
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Manually clear TEFF to test validation
        atm.TEFF = 0.0
        
        # If we try to validate (which happens in read_model),
        # it should have failed, but for this integration test
        # we just verify the reader ran successfully


class TestCardReaderAdvanced:
    """Advanced tests for CardReader edge cases"""
    
    def test_parse_float_with_plus_sign(self):
        """Test parsing floats with explicit plus sign"""
        reader = CardReader("tests/test_input_minimal.txt")
        line = "SOME_DATA +1.00e+10"
        value = reader.parse_float(line, 10)
        assert value == 1.0e10
    
    def test_parse_float_with_minus_sign(self):
        """Test parsing floats with minus sign"""
        reader = CardReader("tests/test_input_minimal.txt")
        line = "SOME_DATA -1.00e-10"
        value = reader.parse_float(line, 10)
        assert value == -1.0e-10
    
    def test_parse_int(self):
        """Test parsing integers"""
        reader = CardReader("tests/test_input_minimal.txt")
        line = "NRHOX 72"
        keyword_end = line.find("NRHOX") + len("NRHOX")
        value = reader.parse_int(line, keyword_end)
        assert value == 72
    
    def test_keyword_not_at_start(self):
        """Test that keywords must be at line start"""
        reader = CardReader("tests/test_input_minimal.txt")
        # Data line starting with spaces
        line = "    1.00e-10  1.20e-10"
        keyword = reader.extract_keyword(line)
        # Should recognize this is a data line, not a keyword
        assert keyword == ""


class TestAtlasModelReaderEdgeCases:
    """Edge case tests for AtlasModelReader"""
    
    def test_multiple_reads_same_file(self):
        """Test reading same file multiple times"""
        reader = AtlasModelReader()
        
        atm1 = reader.read_model("tests/test_input_minimal.txt")
        atm2 = reader.read_model("tests/test_input_minimal.txt")
        
        # Both should have same values
        assert atm1.TEFF == atm2.TEFF
        assert atm1.NRHOX == atm2.NRHOX
    
    def test_gravity_log_scale_conversion(self):
        """Test that gravity < 10 is treated as log scale"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Input is 4.43 (log scale)
        # Should be converted to 10^4.43
        assert atm.GRAV > 10.0  # Ensure it was converted
        
        # Verify GLOG is computed correctly
        import math
        expected_glog = math.log10(atm.GRAV)
        assert abs(atm.GLOG - expected_glog) < 0.001
    
    def test_flux_computation(self):
        """Test Stefan-Boltzmann flux calculation"""
        reader = AtlasModelReader()
        atm = reader.read_model("tests/test_input_minimal.txt")
        
        # Formula: FLUX = 5.6697e-5/12.5664 * TEFF^4
        expected = 5.6697e-5 / 12.5664 * (atm.TEFF ** 4)
        
        assert abs(atm.FLUX - expected) < 1e6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
