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
    
    # Interpolation coefficients (computed in update())
    # Midpoint wavelengths between edges. Shape: (NEDGE-1,)
    HALFEDGE: Optional[torch.Tensor] = None
    
    # Squared wavelength differences for interpolation. Shape: (NEDGE-1,)
    DELEDGE: Optional[torch.Tensor] = None
    
    def update(self):
        """Compute wavelength edge processing and interpolation coefficients.
        
        Implements Fortran spectrv.patched.for lines 145-151:
        1. Take absolute values of wavelengths
        2. Compute midpoints between consecutive wavelength edges (HALFEDGE)
        3. Compute squared wavelength differences (DELEDGE) for interpolation
        """
        import numpy as np
        
        if self.WLEDGE is None or self.NEDGE == 0:
            return
        
        # Convert to numpy for manipulation, then back to tensor
        wledge_np = self.WLEDGE.numpy() if isinstance(self.WLEDGE, torch.Tensor) else np.array(self.WLEDGE)
        
        # Take absolute values of wavelengths (Fortran line 145)
        wledge_np[0] = abs(wledge_np[0])
        for iedge in range(1, self.NEDGE):
            wledge_np[iedge] = abs(wledge_np[iedge])
        
        self.WLEDGE = torch.from_numpy(wledge_np)
        
        # Compute HALFEDGE and DELEDGE (Fortran lines 146-150)
        halfedge_list = []
        deledge_list = []
        
        for iedge in range(1, self.NEDGE):
            # HALFEDGE(IEDGE-1) = (WLEDGE(IEDGE-1) + WLEDGE(IEDGE)) * 0.5
            halfedge = (float(wledge_np[iedge-1]) + float(wledge_np[iedge])) * 0.5
            halfedge_list.append(halfedge)
            
            # DELEDGE(IEDGE-1) = (WLEDGE(IEDGE) - WLEDGE(IEDGE-1))**2 * 0.5
            deledge = (float(wledge_np[iedge]) - float(wledge_np[iedge-1])) ** 2 * 0.5
            deledge_list.append(deledge)
        
        self.HALFEDGE = torch.tensor(halfedge_list, dtype=torch.float64)
        self.DELEDGE = torch.tensor(deledge_list, dtype=torch.float64)
    
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
        if self.HALFEDGE is not None:
            self.HALFEDGE = self.HALFEDGE.to(device)
        if self.DELEDGE is not None:
            self.DELEDGE = self.DELEDGE.to(device)
        return self
