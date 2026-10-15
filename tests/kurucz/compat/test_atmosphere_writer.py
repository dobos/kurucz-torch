import os
import tempfile
import torch
from unittest import TestCase

from kurucz.atmosphere import Atmosphere
from kurucz.compat.atmospherereader import AtmosphereReader
from kurucz.compat.atmospherewriter import AtmosphereWriter


class TestAtmosphereWriter(TestCase):
    def test_write_atmosphere(self):
        # Create a simple test atmosphere
        atmosphere = Atmosphere(
            TEFF=torch.tensor(5770.0),
            GLOG=torch.tensor(4.440),
            XSCALE=torch.tensor(1.0),
            TITLE='Test',
            IFOP=[1] * 20,
            IFCONV=1,
            IFTURB=0,
            MIXLTH=torch.tensor(1.25),
            TRBFDG=torch.tensor(0.0),
            TRBPOW=torch.tensor(0.0),
            TRBSND=torch.tensor(0.0),
            TRBCON=torch.tensor(0.0),
            NRHOX=2,
            RHOX=torch.tensor([1e-3, 2e-3]),
            T=torch.tensor([3000.0, 3500.0]),
            P=torch.tensor([10.0, 15.0]),
            XNE=torch.tensor([1e9, 2e9]),
            ABROSS=torch.tensor([1e-4, 2e-4]),
            ACCRAD=torch.tensor([0.01, 0.02]),
            VTURB=torch.tensor([0.0, 0.0]),
            ABUND=torch.tensor([0.9, 0.1]),
            PRADK0=torch.tensor(1.0),
            NLTEON=0,
            ITER=1,
            IFWAVE=0
        )

        # Test writing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.out') as f:
            temp_filename = f.name

        try:
            writer = AtmosphereWriter()
            writer.write_atmosphere(atmosphere, temp_filename)
            
            # Verify file was created and has content
            self.assertTrue(os.path.exists(temp_filename))
            self.assertGreater(os.path.getsize(temp_filename), 0)
            
            # Read back and verify basic content
            with open(temp_filename, 'r') as f:
                content = f.read()
            
            # Check that key elements are present
            self.assertIn('TEFF', content)
            self.assertIn('GRAVITY', content)
            self.assertIn('TITLE', content)
            self.assertIn('READ DECK', content)
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_write_matches_output_synthe(self):
        ground_truth_path = "/home/dobos/project/kurucz-torch/data/tests/output_synthe.out"
        atmosphere = AtmosphereReader().read_atmosphere(ground_truth_path)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".out") as handle:
            output_path = handle.name

        try:
            AtmosphereWriter().write_atmosphere(atmosphere, output_path)
            with open(ground_truth_path, "r") as expected_handle:
                expected_text = expected_handle.read()
            with open(output_path, "r") as actual_handle:
                actual_text = actual_handle.read()
            self.assertEqual(actual_text, expected_text)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
