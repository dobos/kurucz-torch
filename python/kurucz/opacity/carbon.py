from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class CarbonOpacity(Opacity):
    """Carbon bound-free opacity from COMMON /BC/. Important for CH molecules and lines."""
    
    # Carbon neutral opacity. Shape: (n_depth, 14)
    BC1: Optional[torch.Tensor] = None
    
    # Carbon absorption. Shape: (n_depth,)
    AC1: Optional[torch.Tensor] = None
    
    # Carbon scattering. Shape: (n_depth,)
    SC1: Optional[torch.Tensor] = None
    
    # Carbon ionization stages. Shape: (n_depth, 2)
    XNFPC: Optional[torch.Tensor] = None
    
    # Carbon ionized opacity. Shape: (n_depth, 6)
    BC2: Optional[torch.Tensor] = None
