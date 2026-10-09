from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class HeliumOpacity(Opacity):
    """Helium bound-free opacity from COMMON /BHE/. Second most abundant."""
    
    # He neutral BF opacity. Shape: (n_depth, 29)
    BHE1: Optional[torch.Tensor] = None
    
    # He neutral absorption. Shape: (n_depth,)
    AHE1: Optional[torch.Tensor] = None
    
    # He neutral scattering. Shape: (n_depth,)
    SHE1: Optional[torch.Tensor] = None
    
    # He+ BF opacity. Shape: (n_depth, 6)
    BHE2: Optional[torch.Tensor] = None
    
    # He+ absorption. Shape: (n_depth,)
    AHE2: Optional[torch.Tensor] = None
    
    # He+ scattering. Shape: (n_depth,)
    SHE2: Optional[torch.Tensor] = None
    
    # He- minimum opacity. Shape: (n_depth,)
    AHEMIN: Optional[torch.Tensor] = None
    
    # Continuum scattering cross section for He. Shape: (n_depth,)
    SIGHE: Optional[torch.Tensor] = None
    
    # He and He+ partition functions. Shape: (n_depth, 3)
    XNFPHE: Optional[torch.Tensor] = None
    
    # He number density. Shape: (n_depth, 2)
    XNFHE: Optional[torch.Tensor] = None
