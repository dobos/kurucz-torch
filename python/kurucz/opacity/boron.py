from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class BoronOpacity(Opacity):
    """Boron bound-free opacity from COMMON /BB/. Trace element."""
    
    # Boron neutral opacity. Shape: (n_depth, 7)
    BB1: Optional[torch.Tensor] = None
    
    # Boron ionization. Shape: (n_depth, 1)
    XNFPB: Optional[torch.Tensor] = None
