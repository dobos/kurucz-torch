from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class KaliumOpacity(Opacity):
    """Potassium (Kalium) bound-free opacity from COMMON /BK/. Important in cool stellar atmospheres."""
    
    # Potassium neutral opacity. Shape: (n_depth, 8)
    BK1: Optional[torch.Tensor] = None
    
    # Potassium ionization. Shape: (n_depth, 1)
    XNFPK: Optional[torch.Tensor] = None
