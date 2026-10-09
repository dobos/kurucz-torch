from dataclasses import dataclass
from typing import Optional
import torch

from .opacity import Opacity


@dataclass
class DiatomicMolecularOpacity(Opacity):
    """Opacity from diatomic molecules from COMMON /CHOH/."""
    
    # CH molecule density/opacity. Shape: (n_depth,)
    XNFPCH: Optional[torch.Tensor] = None
    
    # OH radical density/opacity. Shape: (n_depth,)
    XNFPOH: Optional[torch.Tensor] = None
