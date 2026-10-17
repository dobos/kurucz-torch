import unittest
import tempfile
import os
import io
from kurucz.compat.plotparametersreader import PlotParameterReader
from kurucz.compat.plotparameters import PlotParameters


class TestPlotParameters(unittest.TestCase):
    
    def test_plot_parameters_dataclass(self):
        """Test that PlotParameters dataclass works correctly."""
        params = PlotParameters(
            RHOXJ=1.0,
            R1=2.0,
            R101=3.0,
            PH1=4.0,
            PC1=5.0,
            PSI1=6.0,
            PRDDOP=7.0,
            PRDPOW=8.0
        )
        
        self.assertEqual(params.RHOXJ, 1.0)
        self.assertEqual(params.R1, 2.0)
        self.assertEqual(params.R101, 3.0)
        self.assertEqual(params.PH1, 4.0)
        self.assertEqual(params.PC1, 5.0)
        self.assertEqual(params.PSI1, 6.0)
        self.assertEqual(params.PRDDOP, 7.0)
        self.assertEqual(params.PRDPOW, 8.0)
        
    def test_plot_parameter_reader(self):
        """Test that PlotParameterReader correctly parses the format."""
        # Create a temporary file with the same format as FORTRAN: 8F10.5
        # Each number should be 10 characters wide with 5 decimal places
        test_content = "    1.00000    2.00000    3.00000    4.00000    5.00000    6.00000    7.00000    8.00000"
                    
        reader = PlotParameterReader(io.StringIO(test_content))
        params = reader.read_plot_parameters()
        
        self.assertEqual(params.RHOXJ, 1.0)
        self.assertEqual(params.R1, 2.0)
        self.assertEqual(params.R101, 3.0)
        self.assertEqual(params.PH1, 4.0)
        self.assertEqual(params.PC1, 5.0)
        self.assertEqual(params.PSI1, 6.0)
        self.assertEqual(params.PRDDOP, 7.0)
        self.assertEqual(params.PRDPOW, 8.0)


if __name__ == '__main__':
    unittest.main()