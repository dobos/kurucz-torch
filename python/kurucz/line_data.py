"""Spectral Line Data and Atomic/Molecular Properties"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class LineQuantumNumbers:
    """Quantum numbers identifying a spectral line and its upper/lower states."""
    NELION: int  # Ionization state
    NBLO: int  # Lower level number
    NBUP: int  # Upper level number
    ISO1: int  # Isotope code lower
    ISO2: int  # Isotope code upper
    NUPRD: Optional[int] = None
    LINPRD: Optional[int] = None

@dataclass
class LineWavelength:
    """Wavelength information for a spectral line."""
    WL: float  # Air wavelength [Angstrom]
    WLVAC: float  # Vacuum wavelength [Angstrom]
    DWL: float  # Wavelength uncertainty [Angstrom]
    CENTER: Optional[float] = None
    CONCEN: Optional[float] = None

@dataclass
class LineEnergy:
    """Energy levels of the transition."""
    E: float  # Lower energy [eV]
    EP: float  # Upper energy [eV]
    ELO: float  # Excitation energy [eV]

@dataclass
class LineOscillatorStrength:
    """Oscillator strength and line strength parameters."""
    GFLOG: float  # Log10(gf)
    GF: float  # g*f product
    XJ: float  # Lower J
    XJP: float  # Upper J
    CODE: float  # Transition code

@dataclass
class LineBroadening:
    """Line broadening parameters."""
    GAMMAR: float  # Radiative damping
    DGAMMAR: float  # Uncertainty
    GAMMAS: float  # Stark broadening
    DGAMMAS: float  # Uncertainty
    GAMMAW: float  # Van der Waals broadening
    DGAMMAW: float  # Uncertainty
    GS: float  # Stark factor
    GR: float  # Radiative factor
    GW: float  # VdW factor

@dataclass
class LineIdentification:
    """Labels and references for the line."""
    LABEL: str  # Lower term symbol
    LABELP: str  # Upper term symbol
    OTHER1: str  # Additional label
    OTHER2: str  # Additional label
    REF: str  # Reference code

@dataclass
class LineExtraData:
    """Additional parameters and derivatives."""
    DGFLOG: float  # Uncertainty in log(gf)
    EXTRA1: float  # Extra parameter
    EXTRA2: float  # Extra parameter
    EXTRA3: float  # Extra parameter
    X1: float  # Lower isotope shift
    X2: float  # Upper isotope shift

@dataclass
class SpectralLine:
    """Complete description of a spectral line."""
    wavelength: LineWavelength
    energy: LineEnergy
    quantum_numbers: LineQuantumNumbers
    oscillator_strength: LineOscillatorStrength
    broadening: LineBroadening
    identification: LineIdentification
    extra_data: LineExtraData
    
    def transition_energy_eV(self) -> float:
        """Energy of transition [eV]."""
        return self.energy.EP - self.energy.E

@dataclass
class ElementalAbundance:
    """Elemental abundance and atomic mass."""
    ELEM: str  # Element symbol
    Z: int  # Atomic number
    ABUND: float  # Abundance [dex]
    ATMASS: float  # Atomic mass [amu]
    XABUND: Optional[float] = None

@dataclass
class ElementalAbundances:
    """Collection of all elemental abundances."""
    abundances: dict  # Dict[Z: int -> ElementalAbundance]
    WTMOLE: float  # Mean molecular weight [amu]
    
    def __getitem__(self, z: int) -> ElementalAbundance:
        return self.abundances.get(z)
    
    def __setitem__(self, z: int, abund: ElementalAbundance):
        self.abundances[z] = abund
