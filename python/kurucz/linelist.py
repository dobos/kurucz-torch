import torch
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class LineList:
    """
    Dataclass to store line list data from Fortran tape 9.
    
    This represents the line data structure read from tape 9 in the SPECTRV program.
    The line data is read in two parts:
    1. First part: LINDAT8I, LABEL, LABELP, OTHER1, OTHER2, LINDAT8II, LINDAT4I, REF, LINDAT4II
    2. The LINDAT8I and LINDAT8II are 3-element arrays of REAL*8
    3. The LINDAT4I and LINDAT4II are arrays of REAL*4
    """

    NLINES: Optional[int] = None  # Number of lines in the line list
    
    # First part of LINDAT8I (REAL*8)
    WL: Optional[torch.Tensor] = None  # First element of LINDAT8I
    E: Optional[torch.Tensor] = None   # Second element of LINDAT8I
    EP: Optional[torch.Tensor] = None  # Third element of LINDAT8I
    
    # Character data
    LABEL: Optional[torch.Tensor] = None  # 10-character string
    LABELP: Optional[torch.Tensor] = None  # 10-character string
    OTHER1: Optional[torch.Tensor] = None  # 10-character string
    OTHER2: Optional[torch.Tensor] = None  # 10-character string
    
    # Second part of LINDAT8II (REAL*8)
    WLVAC: Optional[torch.Tensor] = None  # First element of LINDAT8II
    CENTER: Optional[torch.Tensor] = None  # Second element of LINDAT8II
    CONCEN: Optional[torch.Tensor] = None  # Third element of LINDAT8II
    
    # First part of LINDAT4I (REAL*4)
    NELION: Optional[torch.Tensor] = None  # First element of LINDAT4I
    GAMMAR: Optional[torch.Tensor] = None  # Second element of LINDAT4I
    GAMMAS: Optional[torch.Tensor] = None  # Third element of LINDAT4I
    GAMMAW: Optional[torch.Tensor] = None  # Fourth element of LINDAT4I
    
    # Character data
    REF: Optional[torch.Tensor] = None  # 4-character string
    
    # Second part of LINDAT4II (REAL*4)
    NBLO: Optional[torch.Tensor] = None  # First element of LINDAT4II
    NBUP: Optional[torch.Tensor] = None  # Second element of LINDAT4II
    ISO1: Optional[torch.Tensor] = None  # Third element of LINDAT4II
    X1: Optional[torch.Tensor] = None    # Fourth element of LINDAT4II
    ISO2: Optional[torch.Tensor] = None  # Fifth element of LINDAT4II
    X2: Optional[torch.Tensor] = None    # Sixth element of LINDAT4II
    GFLOG: Optional[torch.Tensor] = None # Seventh element of LINDAT4II
    XJ: Optional[torch.Tensor] = None    # Eighth element of LINDAT4II
    XJP: Optional[torch.Tensor] = None   # Ninth element of LINDAT4II
    CODE: Optional[torch.Tensor] = None  # Tenth element of LINDAT4II
    ELO: Optional[torch.Tensor] = None   # Eleventh element of LINDAT4II
    GF: Optional[torch.Tensor] = None    # Twelfth element of LINDAT4II
    GS: Optional[torch.Tensor] = None    # Thirteenth element of LINDAT4II
    GR: Optional[torch.Tensor] = None    # Fourteenth element of LINDAT4II
    GW: Optional[torch.Tensor] = None    # Fifteenth element of LINDAT4II
    DWL: Optional[torch.Tensor] = None   # Sixteenth element of LINDAT4II
    DGFLOG: Optional[torch.Tensor] = None # Seventeenth element of LINDAT4II
    DGAMMAR: Optional[torch.Tensor] = None # Eighteenth element of LINDAT4II
    DGAMMAS: Optional[torch.Tensor] = None # Nineteenth element of LINDAT4II
    DGAMMAW: Optional[torch.Tensor] = None # Twentieth element of LINDAT4II
    EXTRA1: Optional[torch.Tensor] = None # Twenty-first element of LINDAT4II
    EXTRA2: Optional[torch.Tensor] = None # Twenty-second element of LINDAT4II
    EXTRA3: Optional[torch.Tensor] = None # Twenty-third element of LINDAT4II

    # Additional line data (ALINEC)
    ALINEC: Optional[torch.Tensor] = None  # 99-element array of REAL*4