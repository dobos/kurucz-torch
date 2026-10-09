"""
Kurucz ATLAS/SYNTHE Python Module

This module provides Python dataclasses and utilities for stellar atmosphere modeling 
and spectral synthesis using the ATLAS/SYNTHE system.

Main classes:
- Atmosphere: Stellar atmospheric structure from ATLAS READIN
- Atlas7v: High-level compatibility wrapper for reading ATLAS models
- CardReader: Low-level parser for ATLAS input card deck files
- AtlasModelReader: Main reader implementation for ATLAS card decks
"""

# Core ATLAS functionality
from .atmosphere import Atmosphere

# Compatibility layer
from .compat.atlas7v import Atlas7v
from .compat.card_reader import CardReader
from .compat.model_reader import AtlasModelReader

# Auxiliary modules (import on demand if needed)
# from .line_data import ...
# from .radiative_transfer_state import ...
# from .spectral_synthesis_config import ...
# from .opacity import ...
# from .element_opacity import ...

__all__ = [
    "Atmosphere",
    "Atlas7v",
    "CardReader",
    "AtlasModelReader",
]

__version__ = "0.1.0"
