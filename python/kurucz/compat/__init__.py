"""
ATLAS Compatibility Layer

Provides reader implementations for ATLAS stellar atmosphere models.

Classes:
- Atlas7v: High-level interface for reading ATLAS models
- AtlasModelReader: Main READIN implementation
- CardReader: Low-level 80-character card parser
"""

from .atlas7v import Atlas7v
from .model_reader import AtlasModelReader
from .card_reader import CardReader

__all__ = [
    "Atlas7v",
    "AtlasModelReader",
    "CardReader",
]
