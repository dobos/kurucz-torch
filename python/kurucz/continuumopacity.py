from dataclasses import dataclass
from typing import Optional

import torch


@dataclass
class ContinuumOpacity:
    """
    Continuum opacity data read from the tape-9 / tape-10 opacity stream.

    The edge table is read as:
    READ(9) NEDGE, (FRQEDG(IEDGE), WLEDGE(IEDGE), CMEDGE(IEDGE), IEDGE=1, NEDGE)
    and the associated continuum frequency grid is read as:
    READ(10) NCON, (CONFRQ(NU), NU=1, NCON)

    Meaning of the arrays:
    - FRQEDG: continuum-edge frequencies used to determine where opacity changes.
      These are raw values from the binary file; because the legacy Fortran code does
      an absolute-value transform before using them, the stored values may appear
      negative even though the physically meaningful quantity is a magnitude.
    - WLEDGE: wavelength edge grid for the same breakpoints.
    - CMEDGE: midpoint/center wavelength associated with each edge interval.
    - CONFRQ: the continuum frequency grid used for the tabulated opacity values
      (absorption/scattering) on each atmospheric layer.
    - ASYNTH: the per-depth continuum opacity vector for a single wavelength sample.
      In the original SYNTHE code this is declared as REAL*4 ASYNTH(kw) with kw=99,
      and only the first NRHOX entries are meaningful. The rest of the fixed-length
      array is unused padding.

    In other words, FRQEDG/WLEDGE/CMEDGE describe the interpolation breakpoints,
    while CONFRQ is the actual continuum frequency sample grid. The code later uses
    abs(FRQEDG), abs(WLEDGE), and abs(CMEDGE) during interpolation. ASYNTH is the
    instantaneous opacity vector per wavelength, stored in a fixed-size array that
    is only partially populated.
    """

    # Number of continuum edges in the opacity table.
    NEDGE: Optional[int] = None

    # Continuum-edge frequencies. Values are raw binary entries and may be signed;
    # the legacy Fortran implementation applies abs() before interpolation.
    FRQEDG: Optional[torch.Tensor] = None

    # Continuum-edge wavelengths. These correspond 1:1 with FRQEDG and are also
    # treated as magnitudes by the interpolation logic.
    WLEDGE: Optional[torch.Tensor] = None

    # Midpoint/center wavelength for each interval between consecutive edges.
    CMEDGE: Optional[torch.Tensor] = None

    # Number of continuum frequency samples in the opacity grid.
    NCON: Optional[int] = None

    # Continuum frequency grid used for the tabulated absorption/scattering values.
    CONFRQ: Optional[torch.Tensor] = None

    # Continuum absorption values for each atmospheric layer.
    QCONTABS: Optional[torch.Tensor] = None

    # Continuum scattering values for each atmospheric layer.
    QCONTSCAT: Optional[torch.Tensor] = None

    # Stack of per-layer opacity vectors for successive wavelength samples.
    # In spectrv.patched.for this is read inside the loop DO 25 NU=NULO,NUHI:
    #   READ(9)ASYNTH
    #   DO 241 J=1,NRHOX
    #       ALINE(J)=ASYNTH(J)*(1.-FSCAT(J))
    #       SIGMAL(J)=ASYNTH(J)*FSCAT(J)
    # so each record contains one ASYNTH array for one wavelength, and the full file
    # contains many such records stacked one after another. The legacy FORTRAN code
    # declares this as a fixed-size kw=99 buffer, but the actual valid range is the
    # first NRHOX entries of the record; any remaining values are unused padding.
    ASYNTH: Optional[torch.Tensor] = None

    def __post_init__(self):
        if self.NEDGE is not None and self.FRQEDG is None:
            self.FRQEDG = torch.zeros(self.NEDGE, dtype=torch.float64)
        if self.NEDGE is not None and self.WLEDGE is None:
            self.WLEDGE = torch.zeros(self.NEDGE, dtype=torch.float64)
        if self.NEDGE is not None and self.CMEDGE is None:
            self.CMEDGE = torch.zeros(self.NEDGE, dtype=torch.float64)
        if self.NCON is not None and self.CONFRQ is None:
            self.CONFRQ = torch.zeros(self.NCON, dtype=torch.float64)
        if self.ASYNTH is None:
            self.ASYNTH = torch.zeros(0, dtype=torch.float32)


__all__ = [
    "ContinuumOpacity",
]
