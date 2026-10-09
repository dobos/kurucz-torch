"""
Kurucz ATLAS/SYNTHE Python Module

This module provides Python dataclasses and utilities for stellar atmosphere modeling 
and spectral synthesis using the ATLAS/SYNTHE system.

Main classes:
- Atmosphere: Stellar atmospheric structure from ATLAS READIN
- CardReader: Parser for ATLAS input card deck files
- AtlasModelReader: Main reader for ATLAS model files
"""

# Core ATLAS functionality
from .atmosphere import Atmosphere
from .card_reader import CardReader
from .model_reader import AtlasModelReader

# Auxiliary modules (import on demand if needed)
# from .line_data import ...
# from .radiative_transfer_state import ...
# from .spectral_synthesis_config import ...
# from .opacity import ...
# from .element_opacity import ...

__all__ = [
    "Atmosphere",
    "CardReader",
    "AtlasModelReader",
]

__version__ = "0.1.0"
