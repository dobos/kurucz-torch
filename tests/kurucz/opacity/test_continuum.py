"""Unit tests for ContinuumOpacity data class.

Tests the data structure and device migration methods of ContinuumOpacity.
For file I/O tests, see test_spectrv.py (SpectrvReader tests).
"""

import unittest
import torch

from kurucz.opacity import ContinuumOpacity


class TestContinuumOpacityDataStructure(unittest.TestCase):
    """Test ContinuumOpacity class data structure and fields."""

    def test_instantiation(self):
        """Test that ContinuumOpacity can be instantiated."""
        cont = ContinuumOpacity()
        self.assertIsInstance(cont, ContinuumOpacity)

    def test_default_values(self):
        """Test default field values."""
        cont = ContinuumOpacity()
        self.assertEqual(cont.NEDGE, 0)
        self.assertEqual(cont.NCON, 0)
        self.assertEqual(cont.NRHOX, 0)
        self.assertIsNone(cont.FRQEDG)
        self.assertIsNone(cont.WLEDGE)
        self.assertIsNone(cont.CMEDGE)
        self.assertIsNone(cont.CONFRQ)
        self.assertIsNone(cont.CONTABS)
        self.assertIsNone(cont.CONTSCAT)

    def test_field_types(self):
        """Test that all fields have correct types."""
        cont = ContinuumOpacity()
        self.assertIsInstance(cont.NEDGE, int)
        self.assertIsInstance(cont.NCON, int)
        self.assertIsInstance(cont.NRHOX, int)


class TestContinuumOpacityDeviceMigration(unittest.TestCase):
    """Test device migration methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.cont = ContinuumOpacity(
            NEDGE=10,
            NCON=5,
            NRHOX=3,
            FRQEDG=torch.randn(10),
            WLEDGE=torch.randn(10),
            CMEDGE=torch.randn(10),
            CONFRQ=torch.randn(5),
            CONTABS=torch.randn(5, 3),
            CONTSCAT=torch.randn(5, 3),
        )

    def test_to_cpu(self):
        """Test moving tensors to CPU."""
        self.cont.to('cpu')

        self.assertEqual(str(self.cont.FRQEDG.device), 'cpu')
        self.assertEqual(str(self.cont.CONTABS.device), 'cpu')

    def test_to_gpu_if_available(self):
        """Test moving tensors to GPU if available."""
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")

        self.cont.to('cuda')

        self.assertTrue(self.cont.FRQEDG.is_cuda)
        self.assertTrue(self.cont.CONTABS.is_cuda)

    def test_to_returns_self(self):
        """Test that .to() returns self."""
        result = self.cont.to('cpu')
        self.assertIs(result, self.cont)


if __name__ == '__main__':
    unittest.main()
