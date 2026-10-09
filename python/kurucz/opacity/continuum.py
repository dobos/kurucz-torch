from dataclasses import dataclass
from typing import Optional
import torch


@dataclass
class ContinuumOpacity:
    """Continuum opacity from SYNTHE output (fort.10).
    
    Maps to UNIT 10 read operations in spectrv.patched.for (lines 136-167).
    Stores frequency grids and continuum absorption/scattering coefficients.
    """
    
    # Frequency edge grid
    # Number of frequency edges
    NEDGE: int = 0
    
    # Frequency at each edge. Shape: (NEDGE,)
    FRQEDG: Optional[torch.Tensor] = None
    
    # Wavelength at each edge. Shape: (NEDGE,)
    WLEDGE: Optional[torch.Tensor] = None
    
    # Center wavelength between edges. Shape: (NEDGE,)
    CMEDGE: Optional[torch.Tensor] = None
    
    # Continuum opacity frequency grid
    # Number of continuum opacity frequency points
    NCON: int = 0
    
    # Continuum opacity frequencies. Shape: (NCON,)
    CONFRQ: Optional[torch.Tensor] = None
    
    # Continuum absorption and scattering arrays
    # Continuum absorption at edges. Shape: (3, NEDGE-1, NRHOX)
    CONTABS: Optional[torch.Tensor] = None
    
    # Continuum scattering at edges. Shape: (3, NEDGE-1, NRHOX)
    CONTSCAT: Optional[torch.Tensor] = None
    
    # Number of depth points (inferred from data)
    NRHOX: int = 0
    
    def to(self, device: str) -> 'ContinuumOpacity':
        """Move all torch tensors to specified device.
        
        Args:
            device: PyTorch device ('cpu' or 'cuda')
        
        Returns:
            Self with tensors on new device
        """
        if self.FRQEDG is not None:
            self.FRQEDG = self.FRQEDG.to(device)
        if self.WLEDGE is not None:
            self.WLEDGE = self.WLEDGE.to(device)
        if self.CMEDGE is not None:
            self.CMEDGE = self.CMEDGE.to(device)
        if self.CONFRQ is not None:
            self.CONFRQ = self.CONFRQ.to(device)
        if self.CONTABS is not None:
            self.CONTABS = self.CONTABS.to(device)
        if self.CONTSCAT is not None:
            self.CONTSCAT = self.CONTSCAT.to(device)
        return self
