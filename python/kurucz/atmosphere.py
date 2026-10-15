import torch
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Atmosphere:
    """
    Dataclass to store stellar atmosphere model parameters and structure.
    Based on the FORTRAN ATLAS7V code and the output_synthe.out data file.
    
    All parameters default to None, requiring explicit assignment.
    Derived parameters (GRAV and GLOG) are calculated automatically when one is provided.
    """
    
    # Fundamental stellar parameters
    TEFF: Optional[torch.Tensor] = None
    GLOG: Optional[torch.Tensor] = None
    GRAV: Optional[torch.Tensor] = None
    
    # Abundance parameters
    XSCALE: Optional[torch.Tensor] = None
    ABUND: Optional[torch.Tensor] = None
    
    # Atmosphere structure parameters
    NRHOX: Optional[int] = None
    RHOX: Optional[torch.Tensor] = None
    T: Optional[torch.Tensor] = None
    P: Optional[torch.Tensor] = None
    XNE: Optional[torch.Tensor] = None
    ABROSS: Optional[torch.Tensor] = None
    ACCRAD: Optional[torch.Tensor] = None
    VTURB: Optional[torch.Tensor] = None
    FLXRAD: Optional[torch.Tensor] = None
    VCONV: Optional[torch.Tensor] = None
    VELSND: Optional[torch.Tensor] = None
    
    # Title identifier
    TITLE: Optional[str] = None
    
    # Additional parameters needed for writing output
    IFOP: Optional[List[int]] = None
    IFCONV: Optional[int] = None
    IFTURB: Optional[int] = None
    MIXLTH: Optional[torch.Tensor] = None
    TRBFDG: Optional[torch.Tensor] = None
    TRBPOW: Optional[torch.Tensor] = None
    TRBSND: Optional[torch.Tensor] = None
    TRBCON: Optional[torch.Tensor] = None
    PRADK0: Optional[torch.Tensor] = None
    NLTEON: Optional[int] = None
    NUMNU: Optional[int] = None
    NULO: Optional[int] = None
    NUHI: Optional[int] = None
    FREQID: Optional[List[str]] = None
    FRESET: Optional[torch.Tensor] = None
    RCOSET: Optional[torch.Tensor] = None
    ITER: Optional[int] = None
    BHYD: Optional[torch.Tensor] = None
    BMIN: Optional[torch.Tensor] = None
    WLTE: Optional[str] = None
    IFWAVE: Optional[int] = None
    NUMITS: Optional[int] = None
    IFPRNT: Optional[int] = None
    IFPNCH: Optional[int] = None
    IFCORR: Optional[str] = None
    IFPRES: Optional[str] = None
    IFMOL: Optional[str] = None
    
    def __post_init__(self):
        """Initialize derived parameters after object creation."""
        # Calculate GRAV from GLOG if GRAV is None and GLOG is set
        if self.GRAV is None and self.GLOG is not None:
            self.GRAV = 10 ** self.GLOG
        # Calculate GLOG from GRAV if GLOG is None and GRAV is set
        elif self.GLOG is None and self.GRAV is not None:
            self.GLOG = torch.log10(self.GRAV)
    
    def __repr__(self):
        return (f"Atmosphere(TEFF={self.TEFF.item() if self.TEFF is not None else 'None'}, "
                f"GLOG={self.GLOG.item() if self.GLOG is not None else 'None'}, "
                f"XSCALE={self.XSCALE.item() if self.XSCALE is not None else 'None'}, "
                f"NRHOX={self.NRHOX})")