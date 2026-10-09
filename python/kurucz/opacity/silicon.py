from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class SiliconOpacity(Opacity):
    """Silicon opacity from COMMON /BSI/. Important for SiH, SiO molecules."""
    
    # Si neutral. Shape: (n_depth, 11)
    BSI1: Optional[torch.Tensor] = None
    
    # Si absorption. Shape: (n_depth,)
    ASI1: Optional[torch.Tensor] = None
    
    # Si scattering. Shape: (n_depth,)
    SSI1: Optional[torch.Tensor] = None
    
    # Si ionization. Shape: (n_depth, 2)
    XNFPSI: Optional[torch.Tensor] = None
    
    # Si ionized. Shape: (n_depth, 10)
    BSI2: Optional[torch.Tensor] = None
