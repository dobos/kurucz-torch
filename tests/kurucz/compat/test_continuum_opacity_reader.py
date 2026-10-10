"""Unit tests for ContinuumOpacityReader."""

import os
import unittest
import torch
import numpy as np

from kurucz.compat import ContinuumOpacityReader
from kurucz.opacity.continuum import ContinuumOpacity


class TestContinuumOpacityReader(unittest.TestCase):
    """Test suite for ContinuumOpacityReader class."""
    
    # Path to real continuum opacity file from solar model
    FORT10_PATH = "/home/dobos/ATLAS_sun_model/synthe_1/fort.10"
    NRHOX_EXPECTED = 72
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = ContinuumOpacityReader()
    
    def test_file_exists(self):
        """Verify test data file exists."""
        self.assertTrue(
            os.path.exists(self.FORT10_PATH),
            f"Test file {self.FORT10_PATH} not found"
        )
    
    def test_read_returns_continuum_opacity_object(self):
        """Test that read() returns a ContinuumOpacity object."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont, ContinuumOpacity)
    
    def test_nedge_is_populated(self):
        """Test that NEDGE is read correctly."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsNotNone(cont.NEDGE)
        self.assertGreater(cont.NEDGE, 0)
        # Solar model should have ~344 edges
        self.assertEqual(cont.NEDGE, 344)
    
    def test_ncon_is_populated(self):
        """Test that NCON is read correctly."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsNotNone(cont.NCON)
        self.assertGreater(cont.NCON, 0)
        # Solar model actually has 1029 continuum frequencies
        self.assertEqual(cont.NCON, 1029)
    
    def test_nrhox_is_set(self):
        """Test that NRHOX is set correctly."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.NRHOX, self.NRHOX_EXPECTED)
    
    def test_frqedg_is_tensor(self):
        """Test that FRQEDG is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.FRQEDG, torch.Tensor)
    
    def test_frqedg_shape(self):
        """Test that FRQEDG has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.FRQEDG.shape[0], cont.NEDGE)
    
    def test_frqedg_dtype(self):
        """Test that FRQEDG has correct dtype."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.FRQEDG.dtype, torch.float64)
    
    def test_wledge_is_tensor(self):
        """Test that WLEDGE is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.WLEDGE, torch.Tensor)
    
    def test_wledge_shape(self):
        """Test that WLEDGE has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.WLEDGE.shape[0], cont.NEDGE)
    
    def test_wledge_dtype(self):
        """Test that WLEDGE has correct dtype."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.WLEDGE.dtype, torch.float64)
    
    def test_wledge_values_positive(self):
        """Test that WLEDGE values are positive (after abs conversion in update())."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertTrue(torch.all(cont.WLEDGE > 0))
    
    def test_wledge_reasonable_range(self):
        """Test that WLEDGE values are in reasonable wavelength range (Angstroms)."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        # Wavelengths should be between 1 Angstrom and 1 million Angstroms
        self.assertTrue(torch.all(cont.WLEDGE >= 1.0))
        self.assertTrue(torch.all(cont.WLEDGE <= 1e6))
    
    def test_cmedge_is_tensor(self):
        """Test that CMEDGE is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.CMEDGE, torch.Tensor)
    
    def test_cmedge_shape(self):
        """Test that CMEDGE has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.CMEDGE.shape[0], cont.NEDGE)
    
    def test_confrq_is_tensor(self):
        """Test that CONFRQ is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.CONFRQ, torch.Tensor)
    
    def test_confrq_shape(self):
        """Test that CONFRQ has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.CONFRQ.shape[0], cont.NCON)
    
    def test_contabs_is_tensor(self):
        """Test that CONTABS is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.CONTABS, torch.Tensor)
    
    def test_contabs_shape(self):
        """Test that CONTABS has correct shape (3, NEDGE-1, NRHOX)."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        expected_shape = (3, cont.NEDGE - 1, self.NRHOX_EXPECTED)
        self.assertEqual(cont.CONTABS.shape, expected_shape)
    
    def test_contabs_dtype(self):
        """Test that CONTABS has correct dtype."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.CONTABS.dtype, torch.float64)
    
    def test_contscat_is_tensor(self):
        """Test that CONTSCAT is a torch tensor."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.CONTSCAT, torch.Tensor)
    
    def test_contscat_shape(self):
        """Test that CONTSCAT has correct shape (3, NEDGE-1, NRHOX)."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        expected_shape = (3, cont.NEDGE - 1, self.NRHOX_EXPECTED)
        self.assertEqual(cont.CONTSCAT.shape, expected_shape)
    
    def test_contscat_dtype(self):
        """Test that CONTSCAT has correct dtype."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.CONTSCAT.dtype, torch.float64)
    
    def test_halfedge_is_tensor(self):
        """Test that HALFEDGE is a torch tensor (computed in update())."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.HALFEDGE, torch.Tensor)
    
    def test_halfedge_shape(self):
        """Test that HALFEDGE has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.HALFEDGE.shape[0], cont.NEDGE - 1)
    
    def test_halfedge_values(self):
        """Test that HALFEDGE values are midpoints between wavelength edges."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        
        # HALFEDGE[i] should equal (WLEDGE[i] + WLEDGE[i+1]) * 0.5
        for i in range(cont.NEDGE - 1):
            expected = (cont.WLEDGE[i] + cont.WLEDGE[i+1]) * 0.5
            self.assertAlmostEqual(
                float(cont.HALFEDGE[i]),
                float(expected),
                places=10,
                msg=f"HALFEDGE[{i}] mismatch"
            )
    
    def test_deledge_is_tensor(self):
        """Test that DELEDGE is a torch tensor (computed in update())."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertIsInstance(cont.DELEDGE, torch.Tensor)
    
    def test_deledge_shape(self):
        """Test that DELEDGE has correct shape."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertEqual(cont.DELEDGE.shape[0], cont.NEDGE - 1)
    
    def test_deledge_values(self):
        """Test that DELEDGE values are squared wavelength differences * 0.5."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        
        # DELEDGE[i] should equal (WLEDGE[i+1] - WLEDGE[i])^2 * 0.5
        for i in range(cont.NEDGE - 1):
            expected = (cont.WLEDGE[i+1] - cont.WLEDGE[i]) ** 2 * 0.5
            self.assertAlmostEqual(
                float(cont.DELEDGE[i]),
                float(expected),
                places=10,
                msg=f"DELEDGE[{i}] mismatch"
            )
    
    def test_deledge_all_positive(self):
        """Test that all DELEDGE values are positive."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertTrue(torch.all(cont.DELEDGE > 0))
    
    def test_contabs_finite_values(self):
        """Test that CONTABS contains finite values (no NaN or inf)."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertTrue(torch.all(torch.isfinite(cont.CONTABS)))
    
    def test_contscat_finite_values(self):
        """Test that CONTSCAT contains finite values (no NaN or inf)."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        self.assertTrue(torch.all(torch.isfinite(cont.CONTSCAT)))
    
    def test_to_method_preserves_structure(self):
        """Test that to() method (device movement) preserves all data structure."""
        cont = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        
        # Store original values
        orig_nedge = cont.NEDGE
        orig_ncon = cont.NCON
        orig_nrhox = cont.NRHOX
        orig_wledge = cont.WLEDGE.clone()
        orig_contabs_shape = cont.CONTABS.shape
        
        # Call to() with CPU (should be no-op for CPU tensors)
        cont.to('cpu')
        
        # Verify structure is preserved
        self.assertEqual(cont.NEDGE, orig_nedge)
        self.assertEqual(cont.NCON, orig_ncon)
        self.assertEqual(cont.NRHOX, orig_nrhox)
        self.assertTrue(torch.allclose(cont.WLEDGE, orig_wledge))
        self.assertEqual(cont.CONTABS.shape, orig_contabs_shape)
    
    def test_reader_consistency_multiple_reads(self):
        """Test that reading the same file multiple times gives consistent results."""
        cont1 = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        cont2 = self.reader.read(self.FORT10_PATH, nrhox=self.NRHOX_EXPECTED)
        
        # Check that key values are identical
        self.assertEqual(cont1.NEDGE, cont2.NEDGE)
        self.assertEqual(cont1.NCON, cont2.NCON)
        self.assertTrue(torch.allclose(cont1.WLEDGE, cont2.WLEDGE))
        self.assertTrue(torch.allclose(cont1.FRQEDG, cont2.FRQEDG))
        self.assertTrue(torch.allclose(cont1.CONTABS, cont2.CONTABS))
    
    def test_different_nrhox_values(self):
        """Test reading with different NRHOX values."""
        # Test with different depth counts
        for nrhox in [1, 36, 72]:
            cont = self.reader.read(self.FORT10_PATH, nrhox=nrhox)
            self.assertEqual(cont.NRHOX, nrhox)
            self.assertEqual(cont.CONTABS.shape[2], nrhox)
            self.assertEqual(cont.CONTSCAT.shape[2], nrhox)


if __name__ == '__main__':
    unittest.main()
