from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class AluminumOpacity(Opacity):
    """Aluminum bound-free opacity from COMMON /BAL/. Important in some stellar atmospheres."""
    
    # Aluminum neutral opacity. Shape: (n_depth, 9)
    BAL1: Optional[torch.Tensor] = None
    
    # Aluminum absorption. Shape: (n_depth,)
    AAL1: Optional[torch.Tensor] = None
    
    # Aluminum scattering. Shape: (n_depth,)
    SAL1: Optional[torch.Tensor] = None
    
    # Aluminum ionization. Shape: (n_depth, 2)
    XNFPAL: Optional[torch.Tensor] = None
    
    # Aluminum ionized opacity. Shape: (n_depth, 1)
    BAL2: Optional[torch.Tensor] = None
