"""Auxiliary opacity data and miscellaneous quantities.

Element-specific bound-free opacity classes have been moved to the 'opacity' namespace:
- from kurucz.opacity import HydrogenOpacity, HeliumOpacity, CarbonOpacity, etc.

Diatomic molecular opacity has also been moved to the 'opacity' namespace:
- from kurucz.opacity import DiatomicMolecularOpacity

This module contains only auxiliary and miscellaneous data structures (not opacity-related).
"""
from dataclasses import dataclass
from typing import Optional
import torch


@dataclass
class AuxiliaryScaling:
    """Auxiliary scaling factors and fudge factors."""
    BONE: torch.Tensor  # Auxiliary scaling factor. Shape: (n_depth,)
    BFUDGE: torch.Tensor  # Opacity fudge factor (empirical correction). Shape: (n_depth,)


@dataclass
class FluxQuantities:
    """Flux and error-related quantities."""
    FLUX: float  # Current total flux [erg/cm^2/s]
    FLXERR: Optional[torch.Tensor] = None  # Flux error. Shape: (n_depth,)
    FLXDRV: Optional[torch.Tensor] = None  # Flux derivative. Shape: (n_depth,)
    FLXRAD: Optional[torch.Tensor] = None  # Radiative flux [erg/cm^2/s]. Shape: (n_depth,)


@dataclass
class MiscellaneousData:
    """Miscellaneous/auxiliary data and metadata."""
    XSCALE: float  # Scaling parameter
    TITLE: str  # Title/description (74 chars max)
    FREQID: str  # Frequency identifier (6 chars)
    WLTE: str  # Wavelength type identifier (4 chars)
