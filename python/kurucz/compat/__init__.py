"""
ATLAS Compatibility Layer

Provides reader implementations for ATLAS stellar atmosphere models.

Classes:
- Atlas7v: High-level interface for reading ATLAS models
- AtlasModelReader: Main READIN implementation
- AtmosphereReader: Reads pre-computed ATLAS atmosphere models (READIN MODE=2)
- ContinuumOpacityReader: Reads continuum opacity from UNIT 10
- CardReader: Low-level 80-character card parser
"""

from .atlas7v import Atlas7v
from .model_reader import AtlasModelReader
from .atmosphere_reader import AtmosphereReader
from .continuum_opacity_reader import ContinuumOpacityReader
from .card_reader import CardReader

__all__ = [
    "Atlas7v",
    "AtlasModelReader",
    "AtmosphereReader",
    "ContinuumOpacityReader",
    "CardReader",
]
