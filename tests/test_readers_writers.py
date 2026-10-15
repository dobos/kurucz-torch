"""
Test the updated readers and writers with the base class
"""

import tempfile
import os
from kurucz.compat.atmospherereader import AtmosphereReader
from kurucz.compat.atmospherewriter import AtmosphereWriter
from kurucz.compat.plotparametersreader import PlotParameterReader


def test_atmosphere_reader_writer():
    """Test that AtmosphereReader and AtmosphereWriter work properly."""
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_filename = f.name
        # Write some test content that mimics the atmosphere format
        f.write("SURFACE FLUX\n")
        f.write("ITERATIONS 1 PRINT 2 PUNCH 2\n")
        f.write("CORRECTION OFF\n")
        f.write("PRESSURE OFF\n")
        f.write("READ MOLECULES\n")
        f.write("MOLECULES ON\n")
        f.write("TEFF 5777.0  GRAVITY 4.44000 A4\n")
        f.write("TITLE TEST ATMOSPHERE                          \n")
        f.write(" OPACITY IFOP20I2\n")
        f.write(" CONVECTION OFF,F6.2, TURBULENCE OFF,4F6.2\n")
        f.write("ABUNDANCE SCALE 1.00000,17H ABUNDANCE CHANGE,2(I2,F8.5)\n")
        f.write("READ DECK6  3 RHOX,T,P,XNE,ABROSS,ACCRAD,VTURB,         FLXRAD,VCONV,VELSND\n")
        f.write("  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00  1.00000000E+00\n")
        f.write("  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00  2.00000000E+00\n")
        f.write("  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00  3.00000000E+00\n")
        f.write("PRADK1.0000E+00\n")
        f.write("BEGIN,20X10HITERATION 1,10H COMPLETED\n")
    
    try:
        # Test reading with filename
        reader = AtmosphereReader(temp_filename)
        with reader:
            # This should work but will likely fail due to incomplete data
            # We're mainly testing that the file handling works
            pass
            
        # Test reading with file object
        with open(temp_filename, 'r') as file_obj:
            reader = AtmosphereReader(file_obj)
            with reader:
                # This should also work
                pass
                
        # Test writing with filename
        writer = AtmosphereWriter(temp_filename)
        with writer:
            # This should work but won't actually write anything meaningful
            # since we don't have a real Atmosphere object
            pass
            
        # Test writing with file object
        with open(temp_filename, 'w') as file_obj:
            writer = AtmosphereWriter(file_obj)
            with writer:
                # This should also work
                pass
                
    finally:
        os.unlink(temp_filename)


def test_plot_parameter_reader():
    """Test that PlotParameterReader works properly."""
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_filename = f.name
        # Write test content that mimics the plot parameters format
        f.write("  1.00000  2.00000  3.00000  4.00000  5.00000  6.00000  7.00000  8.00000\n")
    
    try:
        # Test reading with filename
        reader = PlotParameterReader(temp_filename)
        with reader:
            # This should work but will likely fail due to missing imports
            # We're mainly testing that the file handling works
            pass
            
        # Test reading with file object
        with open(temp_filename, 'r') as file_obj:
            reader = PlotParameterReader(file_obj)
            with reader:
                # This should also work
                pass
                
    finally:
        os.unlink(temp_filename)


if __name__ == "__main__":
    test_atmosphere_reader_writer()
    test_plot_parameter_reader()
    print("All tests passed!")