from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class HydrogenOpacity(Opacity):
    """Hydrogen bound-free opacity from COMMON /BHYD/. Most abundant element."""
    
    # Hydrogen BF opacity. Shape: (n_depth, 8)
    BHYD: Optional[torch.Tensor] = None
    
    # Hydrogen absorption. Shape: (n_depth,)
    AHYD: Optional[torch.Tensor] = None
    
    # Hydrogen scattering. Shape: (n_depth,)
    SHYD: Optional[torch.Tensor] = None
    
    # H- opacity. Shape: (n_depth,)
    AH2P: Optional[torch.Tensor] = None
    
    # H- minimum opacity. Shape: (n_depth,)
    BMIN: Optional[torch.Tensor] = None
    
    # H- absorption. Shape: (n_depth,)
    AHMIN: Optional[torch.Tensor] = None
    
    # H- scattering. Shape: (n_depth,)
    SHMIN: Optional[torch.Tensor] = None
    
    # Continuum scattering cross section for H. Shape: (n_depth,)
    SIGH: Optional[torch.Tensor] = None
    
    # Continuum scattering cross section for H2+. Shape: (n_depth,)
    SIGH2: Optional[torch.Tensor] = None
    
    # H line opacity. Shape: (n_depth,)
    AHLINE: Optional[torch.Tensor] = None
    
    # H line scattering. Shape: (n_depth,)
    SHLINE: Optional[torch.Tensor] = None
    
    # H and H+ partition functions. Shape: (n_depth, 2)
    XNFPH: Optional[torch.Tensor] = None
    
    # H number density. Shape: (n_depth,)
    XNFH: Optional[torch.Tensor] = None
