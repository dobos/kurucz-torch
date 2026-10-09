from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class OxygenOpacity(Opacity):
    """Oxygen bound-free opacity from COMMON /BO/. Important for OH, CO molecules."""
    
    # Oxygen opacity. Shape: (n_depth, 13)
    BO1: Optional[torch.Tensor] = None
    
    # Oxygen ionization. Shape: (n_depth, 1)
    XNFPO: Optional[torch.Tensor] = None
    
    # Oxygen ionized. Shape: (n_depth, 4)
    BO2: Optional[torch.Tensor] = None
