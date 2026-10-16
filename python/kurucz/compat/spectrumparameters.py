from dataclasses import dataclass
from typing import Optional


@dataclass
class SpectrumParameters:
    """
    Dataclass to store spectral synthesis parameters read from file 9 (fort.9).

    These values come from the first unformatted Fortran record:
    READ(9) WLBEG, RESOLU, WLEND, LENGTH, N, LINOUT, TURBV, IFVAC
    """

    WLBEG: Optional[float] = None
    RESOLU: Optional[float] = None
    WLEND: Optional[float] = None
    LENGTH: Optional[int] = None
    N: Optional[int] = None
    LINOUT: Optional[int] = None
    TURBV: Optional[float] = None
    IFVAC: Optional[int] = None
