"""Unit tests for SpectrvReader class.

Tests Fortran unformatted binary file reading and ContinuumOpacity population
for SYNTHE spectral synthesis output (fort.10).
"""

import unittest
import os
from pathlib import Path
import tempfile
import struct
import numpy as np
import torch

from kurucz.spectrv import SpectrvReader
from kurucz.opacity import ContinuumOpacity


# Path to existing ATLAS sun model with SYNTHE output
TEST_DATA_DIR = Path('/home/dobos/ATLAS_sun_model')


class TestFortranRecordReading(unittest.TestCase):
    """Test Fortran binary record reading utilities."""

    def test_read_fortran_record(self):
        """Test reading a Fortran unformatted record."""
        # Create a temporary Fortran-formatted binary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_path = f.name
            
            # Write a simple record: length marker + data + length marker
            data = b'HELLO'
            record_length = len(data)
            f.write(struct.pack('<i', record_length))
            f.write(data)
            f.write(struct.pack('<i', record_length))
        
        try:
            # Read the record
            with open(temp_path, 'rb') as f:
                record = SpectrvReader._read_fortran_record(f)
            
            self.assertEqual(record, data)
        finally:
            os.unlink(temp_path)

    def test_read_fortran_reals_float64(self):
        """Test reading Fortran REAL*8 values."""
        # Create binary data with 3 doubles
        values = np.array([1.5, 2.7, 3.14], dtype=np.float64)
        data = struct.pack('<3d', *values)
        
        result = SpectrvReader._read_fortran_reals(data, 3, 'float64')
        
        np.testing.assert_array_almost_equal(result, values)

    def test_read_fortran_integers(self):
        """Test reading Fortran INTEGER values."""
        # Create binary data with 3 integers
        values = np.array([42, 100, -5], dtype=np.int32)
        data = struct.pack('<3i', *values)
        
        result = SpectrvReader._read_fortran_integers(data, 3)
        
        np.testing.assert_array_equal(result, values)

    def test_read_fortran_record_corrupted(self):
        """Test error handling for corrupted records."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_path = f.name
            
            # Write mismatched record markers (both have data, but markers don't match)
            f.write(struct.pack('<i', 10))  # Say 10 bytes
            f.write(b'HELLO' + b'WORLD')  # Write exactly 10 bytes
            f.write(struct.pack('<i', 20))  # Trailing marker says 20 (mismatch!)
        
        try:
            with open(temp_path, 'rb') as f:
                with self.assertRaises(ValueError):
                    SpectrvReader._read_fortran_record(f)
        finally:
            os.unlink(temp_path)


class TestSpectrvReaderContinuumOpacityFileReading(unittest.TestCase):
    """Test reading SYNTHE continuum opacity output files."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_data_dir = TEST_DATA_DIR
        cls.synthe_dir = cls.test_data_dir / 'synthe_1'
        cls.fort10_path = cls.synthe_dir / 'fort.10'

    def test_fort10_exists(self):
        """Test that fort.10 file exists (or can be created)."""
        if not self.fort10_path.exists():
            self.skipTest(
                f"fort.10 not found at {self.fort10_path}. "
                "Run SYNTHE to generate: "
                "cd /home/dobos/ATLAS_sun_model && synthe < synthe_launch.com"
            )

    def test_read_continuum_opacity_file(self):
        """Test reading continuum opacity from fort.10."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping file read test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Verify that data was loaded
        self.assertGreater(cont.NEDGE, 0, "NEDGE should be > 0")
        self.assertGreater(cont.NCON, 0, "NCON should be > 0")
        self.assertGreater(cont.NRHOX, 0, "NRHOX should be > 0")

    def test_read_continuum_opacity_shapes(self):
        """Test that loaded arrays have correct shapes."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping shape test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Check array shapes
        self.assertEqual(cont.FRQEDG.shape[0], cont.NEDGE)
        self.assertEqual(cont.WLEDGE.shape[0], cont.NEDGE)
        self.assertEqual(cont.CMEDGE.shape[0], cont.NEDGE)
        self.assertEqual(cont.CONFRQ.shape[0], cont.NCON)

        # Check CONTABS and CONTSCAT shapes
        self.assertEqual(cont.CONTABS.shape[0], cont.NCON)
        self.assertEqual(cont.CONTABS.shape[1], cont.NRHOX)
        self.assertEqual(cont.CONTSCAT.shape[0], cont.NCON)
        self.assertEqual(cont.CONTSCAT.shape[1], cont.NRHOX)

    def test_read_continuum_opacity_data_types(self):
        """Test that loaded data has correct types."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping dtype test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Check tensor types
        self.assertIsInstance(cont.FRQEDG, torch.Tensor)
        self.assertIsInstance(cont.WLEDGE, torch.Tensor)
        self.assertIsInstance(cont.CMEDGE, torch.Tensor)
        self.assertIsInstance(cont.CONFRQ, torch.Tensor)
        self.assertIsInstance(cont.CONTABS, torch.Tensor)
        self.assertIsInstance(cont.CONTSCAT, torch.Tensor)

    def test_read_continuum_opacity_values_positive(self):
        """Test that opacity values are physically reasonable (positive)."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping values test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Wavelengths should be positive
        self.assertTrue(torch.all(cont.WLEDGE > 0), "All wavelengths should be positive")
        self.assertTrue(torch.all(cont.CMEDGE > 0), "All center wavelengths should be positive")

        # Frequencies should be positive
        self.assertTrue(torch.all(cont.FRQEDG > 0), "All frequencies should be positive")

        # Opacity values should typically be non-negative
        # (absorption and scattering shouldn't be negative)
        self.assertTrue(torch.all(cont.CONTABS >= 0), "Absorption should be non-negative")
        self.assertTrue(torch.all(cont.CONTSCAT >= 0), "Scattering should be non-negative")

    def test_read_continuum_opacity_cpu_device(self):
        """Test reading onto CPU device."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping device test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path), device='cpu')

        self.assertEqual(str(cont.FRQEDG.device), 'cpu')
        self.assertEqual(str(cont.CONTABS.device), 'cpu')

    def test_read_continuum_opacity_gpu_device(self):
        """Test reading onto CUDA device if available."""
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available - skipping GPU test")

        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found - skipping GPU read test")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path), device='cuda')

        self.assertTrue(cont.FRQEDG.is_cuda)
        self.assertTrue(cont.CONTABS.is_cuda)


class TestSpectrvReaderIntegration(unittest.TestCase):
    """Integration tests for SpectrvReader."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_data_dir = TEST_DATA_DIR
        cls.synthe_dir = cls.test_data_dir / 'synthe_1'
        cls.fort10_path = cls.synthe_dir / 'fort.10'

    def test_read_and_access_data(self):
        """Test reading file and accessing data fields."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found")

        cont = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Access various fields
        nedge = cont.NEDGE
        ncon = cont.NCON
        nrhox = cont.NRHOX

        # Check consistency
        self.assertEqual(cont.FRQEDG.shape[0], nedge)
        self.assertEqual(cont.CONTABS.shape, (ncon, nrhox))

        # Extract a single depth layer
        first_depth_abs = cont.CONTABS[:, 0]
        self.assertEqual(first_depth_abs.shape[0], ncon)

    def test_read_multiple_times(self):
        """Test reading the same file multiple times."""
        if not self.fort10_path.exists():
            self.skipTest("fort.10 not found")

        cont1 = SpectrvReader.read_continuum_opacity(str(self.fort10_path))
        cont2 = SpectrvReader.read_continuum_opacity(str(self.fort10_path))

        # Should have same dimensions
        self.assertEqual(cont1.NEDGE, cont2.NEDGE)
        self.assertEqual(cont1.NCON, cont2.NCON)
        self.assertEqual(cont1.NRHOX, cont2.NRHOX)

        # Should have same data (within numerical precision)
        torch.testing.assert_close(cont1.CONTABS, cont2.CONTABS)


class TestSpectrvReaderErrorHandling(unittest.TestCase):
    """Test error handling in SpectrvReader."""

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            SpectrvReader.read_continuum_opacity('/nonexistent/path/fort.10')

    def test_invalid_fortran_record(self):
        """Test error handling for invalid Fortran records."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_path = f.name
            # Write incomplete record
            f.write(struct.pack('<i', 100))
            f.write(b'SHORT')
            # Don't write trailing marker

        try:
            with self.assertRaises(EOFError):
                with open(temp_path, 'rb') as f:
                    SpectrvReader._read_fortran_record(f)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
