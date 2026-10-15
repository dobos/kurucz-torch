import torch
from dataclasses import dataclass, field
from typing import Optional
from ..fortran.formattedfile import FormattedFile


@dataclass
class PlotParameters:
    """
    Dataclass to store plotting parameters read from file 25 (fort.25).
    These parameters control the spectral synthesis plotting behavior.
    """
    RHOXJ: Optional[float] = None
    R1: Optional[float] = None
    R101: Optional[float] = None
    PH1: Optional[float] = None
    PC1: Optional[float] = None
    PSI1: Optional[float] = None
    PRDDOP: Optional[float] = None
    PRDPOW: Optional[float] = None


