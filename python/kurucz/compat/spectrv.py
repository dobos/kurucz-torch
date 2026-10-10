"""
ATLAS7v Compatibility Wrapper

Provides high-level interface for reading and working with ATLAS stellar
atmosphere models.
"""

import sys
from typing import Union, TextIO
from .atmosphere_reader import AtmosphereReader
from .continuum_opacity_reader import ContinuumOpacityReader
from ..atmosphere import Atmosphere

from .atlas7v import Atlas7v


class Spectrv:
    """High-level interface for working with the SPECTRV tool."""

    def __init__(self):
        pass

    def main(self):
        reader = AtmosphereReader()
        atmosphere = reader.read(sys.stdin)

        continuum_opacity_reader = ContinuumOpacityReader()
        continuum_opacity = continuum_opacity_reader.read("fort.10", atmosphere.NRHOX)

        pass        

if __name__ == "__main__":
    Spectrv().main()

