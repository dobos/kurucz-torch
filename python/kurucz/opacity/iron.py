from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class IronOpacity(Opacity):
    """Iron opacity from COMMON /BFE/. Important for many lines and UV opacity."""
    
    # Fe opacity. Shape: (n_depth, 15)
    BFE1: Optional[torch.Tensor] = None
    
    # Fe absorption. Shape: (n_depth,)
    AFE1: Optional[torch.Tensor] = None
    
    # Fe scattering. Shape: (n_depth,)
    SFE1: Optional[torch.Tensor] = None
    
    # Fe ionization. Shape: (n_depth, 1)
    XNFPFE: Optional[torch.Tensor] = None
