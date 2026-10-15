import torch
from unittest import TestCase

from kurucz.atmosphere import Atmosphere

class TestAtmosphere(TestCase):
    def test_atmosphere_creation(self):
        """Test creating an atmosphere object."""
        # Test with None defaults (all parameters should be None initially)
        atm = Atmosphere()
        
        # Test that all parameters are None by default
        self.assertIsNone(atm.TEFF)
        self.assertIsNone(atm.GLOG)
        self.assertIsNone(atm.GRAV)
        self.assertIsNone(atm.XSCALE)
        self.assertIsNone(atm.ABUND)
        self.assertIsNone(atm.NRHOX)
        self.assertIsNone(atm.RHOX)
        self.assertIsNone(atm.T)
        self.assertIsNone(atm.P)
        self.assertIsNone(atm.XNE)
        self.assertIsNone(atm.ABROSS)
        self.assertIsNone(atm.ACCRAD)
        self.assertIsNone(atm.VTURB)
        self.assertIsNone(atm.TITLE)
        
        # Test with specific values
        atm2 = Atmosphere(
            TEFF=torch.tensor(5770.0),
            GLOG=torch.tensor(4.440),
            GRAV=torch.tensor(0.0),  # Will be calculated from GLOG
            XSCALE=torch.tensor(1.0),
            ABUND=torch.tensor([0.0] * 99),
            NRHOX=72,
            RHOX=torch.tensor([0.0] * 72),
            T=torch.tensor([0.0] * 72),
            P=torch.tensor([0.0] * 72),
            XNE=torch.tensor([0.0] * 72),
            ABROSS=torch.tensor([0.0] * 72),
            ACCRAD=torch.tensor([0.0] * 72),
            VTURB=torch.tensor([0.0] * 72),
            TITLE="Test Atmosphere"
        )
        
        self.assertEqual(atm2.TEFF.item(), 5770.0)
        self.assertTrue(torch.isclose(atm2.GLOG, torch.tensor(4.440)).item())
        self.assertEqual(atm2.XSCALE.item(), 1.0)
        self.assertEqual(atm2.TITLE, "Test Atmosphere")
        self.assertEqual(atm2.NRHOX, 72)
        
        # Test derived parameter calculation
        # Create an atmosphere with GLOG=4.440 and GRAV=None (should be calculated)
        atm3 = Atmosphere(
            TEFF=torch.tensor(5770.0),
            GLOG=torch.tensor(4.440),
            GRAV=None,  # Will be calculated from GLOG
            XSCALE=torch.tensor(1.0),
            ABUND=torch.tensor([0.0] * 99),
            NRHOX=0,
            RHOX=torch.tensor([]),
            T=torch.tensor([]),
            P=torch.tensor([]),
            XNE=torch.tensor([]),
            ABROSS=torch.tensor([]),
            ACCRAD=torch.tensor([]),
            VTURB=torch.tensor([]),
            TITLE=""
        )
        
        # Check that GRAV was calculated (just verify it's not None and has a reasonable value)
        self.assertIsNotNone(atm3.GRAV)
        self.assertGreater(atm3.GRAV.item(), 0)
        
        # Test reverse calculation - GLOG from GRAV
        atm4 = Atmosphere(
            TEFF=torch.tensor(5770.0),
            GLOG=None,  # Will be calculated from GRAV
            GRAV=torch.tensor(27542.291015625),  # Approximate value from torch calculation
            XSCALE=torch.tensor(1.0),
            ABUND=torch.tensor([0.0] * 99),
            NRHOX=0,
            RHOX=torch.tensor([]),
            T=torch.tensor([]),
            P=torch.tensor([]),
            XNE=torch.tensor([]),
            ABROSS=torch.tensor([]),
            ACCRAD=torch.tensor([]),
            VTURB=torch.tensor([]),
            TITLE=""
        )
        
        # Check that GLOG was calculated (just verify it's not None and has a reasonable value)
        self.assertIsNotNone(atm4.GLOG)
        self.assertGreater(atm4.GLOG.item(), 0)
        