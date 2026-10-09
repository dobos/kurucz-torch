"""
ATLAS7v Compatibility Wrapper

Provides high-level interface for reading and working with ATLAS stellar
atmosphere models.
"""

from typing import Union, TextIO
import sys
from pathlib import Path

# Add parent directory to path to import model_reader
sys.path.insert(0, str(Path(__file__).parent.parent))

from model_reader import AtlasModelReader
from atmosphere import Atmosphere


class Atlas7v:
    """Compatibility wrapper for ATLAS7v stellar atmosphere models.
    
    Provides a clean Python interface for reading pre-computed ATLAS models
    from card deck input files.
    
    Typical usage:
        atlas = Atlas7v()
        atm = atlas.read_model("model.txt")
        print(f"TEFF = {atm.TEFF} K")
        print(f"GRAV = {atm.GRAV} dyne/cm²")
        print(f"Temperature structure: {atm.T}")
    """
    
    def __init__(self):
        """Initialize ATLAS7v wrapper."""
        self.reader = AtlasModelReader()
    
    def read_model(self, filepath: Union[str, TextIO]) -> Atmosphere:
        """Read a pre-computed stellar atmosphere model from an ATLAS card deck.
        
        This method reads an ATLAS input file and populates an Atmosphere object
        with all the model parameters. No computation is performed—the atmosphere
        is assumed to be pre-calculated.
        
        Args:
            filepath: Path to ATLAS input file (str) or open file object (TextIO)
        
        Returns:
            Atmosphere object with populated model data:
            - TEFF, GRAV, GLOG: Stellar parameters
            - NRHOX: Number of depth points
            - RHOX: Optical depth grid
            - T: Temperature structure [K]
            - P: Pressure structure [dyne/cm²]
            - XNE: Electron number density [cm⁻³]
            - Optional: TITLE, NLTEON, IFMOL, IFCONV, IFTURB
        
        Raises:
            ValueError: If required fields are missing or parsing fails
            IOError: If file cannot be read
        
        Examples:
            # Read a single model
            atlas = Atlas7v()
            atm = atlas.read_model("solar_model.txt")
            print(f"Effective temperature: {atm.TEFF} K")
            print(f"Number of depth points: {atm.NRHOX}")
            
            # Access arrays
            print(f"Temperature at surface: {atm.T[0]} K")
            print(f"Pressure at photosphere: {atm.P[0]} dyne/cm²")
        """
        return self.reader.read_model(filepath)