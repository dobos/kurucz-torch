from dataclasses import dataclass
from typing import Optional

import torch


@dataclass
class OpacityVectors:
    """
    Dataclass to store opacity vectors for a stellar atmosphere.
    
    Attributes:
        NRHOX: Number of atmospheric layers.
        NWAVE: Number of wavelength samples in the opacity vector.
        ASYNTH: Stack of per-layer opacity vectors for successive wavelength samples.
    """

    # Number of atmospheric layers.
    NRHOX: Optional[int] = None

    # Number of wavelength samples in the opacity vector.
    NWAVE: Optional[int] = None

    # Stack of per-layer opacity vectors for successive wavelength samples.
    ASYNTH: Optional[torch.Tensor] = None

    def __post_init__(self):
        if self.ASYNTH is None:
            self.ASYNTH = torch.zeros((self.NRHOX, self.NWAVE), dtype=torch.float32)


__all__ = [
    "OpacityVectors",
]
