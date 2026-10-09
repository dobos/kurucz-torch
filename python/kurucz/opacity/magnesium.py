from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class MagnesiumOpacity(Opacity):
    """Magnesium opacity from COMMON /BMG/. Important for MgH molecule."""
    
    # Mg neutral. Shape: (n_depth, 11)
    BMG1: Optional[torch.Tensor] = None
    
    # Mg absorption. Shape: (n_depth,)
    AMG1: Optional[torch.Tensor] = None
    
    # Mg scattering. Shape: (n_depth,)
    SMG1: Optional[torch.Tensor] = None
    
    # Mg ionization. Shape: (n_depth, 2)
    XNFPMG: Optional[torch.Tensor] = None
    
    # Mg ionized. Shape: (n_depth, 6)
    BMG2: Optional[torch.Tensor] = None
