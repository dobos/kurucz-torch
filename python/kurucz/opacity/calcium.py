from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class CalciumOpacity(Opacity):
    """Calcium bound-free opacity from COMMON /BCA/. Important in stellar atmospheres."""
    
    # Calcium neutral opacity. Shape: (n_depth, 8)
    BCA1: Optional[torch.Tensor] = None
    
    # Calcium ionized opacity. Shape: (n_depth, 5)
    BCA2: Optional[torch.Tensor] = None
    
    # Calcium ionization. Shape: (n_depth, 2)
    XNFPCA: Optional[torch.Tensor] = None
