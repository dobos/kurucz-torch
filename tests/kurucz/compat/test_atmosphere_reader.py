from unittest import TestCase

from kurucz.compat.atmospherereader import AtmosphereReader


class TestAtmosphereReader(TestCase):
    def test_read_output_synthe(self):
        reader = AtmosphereReader()
        atmosphere = reader.read_atmosphere("/home/dobos/project/kurucz-torch/data/tests/output_synthe.out")

        self.assertEqual(atmosphere.NUMITS, 1)
        self.assertEqual(atmosphere.IFPRNT, 2)
        self.assertEqual(atmosphere.IFPNCH, 2)
        self.assertEqual(atmosphere.IFCORR, "OFF")
        self.assertEqual(atmosphere.IFPRES, "OFF")
        self.assertEqual(atmosphere.IFMOL, "ON")

        self.assertAlmostEqual(atmosphere.TEFF.item(), 5770.0, places=6)
        self.assertAlmostEqual(atmosphere.GLOG.item(), 4.44, places=6)
        self.assertEqual(atmosphere.WLTE, "")
        self.assertEqual(atmosphere.TITLE, "  B a s i c A T L A S                                                     ")

        self.assertEqual(atmosphere.IFOP, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(atmosphere.IFCONV, 1)
        self.assertEqual(atmosphere.IFTURB, 0)
        self.assertAlmostEqual(atmosphere.MIXLTH.item(), 1.25, places=6)
        self.assertAlmostEqual(atmosphere.TRBFDG.item(), 0.0, places=6)
        self.assertAlmostEqual(atmosphere.TRBPOW.item(), 0.0, places=6)
        self.assertAlmostEqual(atmosphere.TRBSND.item(), 0.0, places=6)
        self.assertAlmostEqual(atmosphere.TRBCON.item(), 0.0, places=6)

        self.assertAlmostEqual(atmosphere.XSCALE.item(), 1.0, places=6)
        self.assertEqual(atmosphere.ABUND.shape[0], 99)
        self.assertAlmostEqual(atmosphere.ABUND[0].item(), 0.91183, places=6)
        self.assertAlmostEqual(atmosphere.ABUND[1].item(), 0.08708, places=6)
        self.assertAlmostEqual(atmosphere.ABUND[98].item(), -20.0, places=6)

        self.assertEqual(atmosphere.NRHOX, 72)
        self.assertEqual(atmosphere.RHOX.shape[0], 72)
        self.assertAlmostEqual(atmosphere.RHOX[0].item(), 4.95171714e-04, places=12)
        self.assertAlmostEqual(atmosphere.T[0].item(), 3691.9, places=6)
        self.assertAlmostEqual(atmosphere.P[0].item(), 1.364e+01, places=6)
        self.assertAlmostEqual(atmosphere.VTURB[0].item(), 0.0, places=6)
        self.assertAlmostEqual(atmosphere.FLXRAD[0].item(), 5.001e+09, places=2)
        self.assertAlmostEqual(atmosphere.VCONV[0].item(), 0.0, places=6)
        self.assertAlmostEqual(atmosphere.VELSND[0].item(), 6.753e+05, places=2)

        self.assertAlmostEqual(atmosphere.RHOX[-1].item(), 7.91227809e+00, places=8)
        self.assertAlmostEqual(atmosphere.T[-1].item(), 9981.5, places=6)
        self.assertAlmostEqual(atmosphere.P[-1].item(), 2.179e+05, places=2)
        self.assertAlmostEqual(atmosphere.FLXRAD[-1].item(), 1.505e+08, places=2)
        self.assertAlmostEqual(atmosphere.VCONV[-1].item(), 2.047e+05, places=2)
        self.assertAlmostEqual(atmosphere.VELSND[-1].item(), 9.053e+05, places=2)

        self.assertAlmostEqual(atmosphere.PRADK0.item(), 1.4802, places=6)
        self.assertEqual(atmosphere.ITER, 15)
