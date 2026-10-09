"""Spectral Line Data and Atomic/Molecular Properties"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class LineQuantumNumbers:
    """Quantum numbers identifying a spectral line and its upper/lower states."""
    NELION: int  # Ionization state: 1 = neutral, 2 = singly ionized, etc.
    NBLO: int  # Lower level number (quantum state index)
    NBUP: int  # Upper level number (quantum state index)
    ISO1: int  # Isotope code for lower state
    ISO2: int  # Isotope code for upper state
    NUPRD: Optional[int] = None  # Partial redistribution level code
    LINPRD: Optional[int] = None  # Partial redistribution line identifier

@dataclass
class LineWavelength:
    """Wavelength information for a spectral line."""
    WL: float  # Air wavelength [Angstrom]
    WLVAC: float  # Vacuum wavelength [Angstrom]
    DWL: float  # Wavelength uncertainty [Angstrom]
    CENTER: Optional[float] = None  # Line center intensity (computed during RT)
    CONCEN: Optional[float] = None  # Line wing intensity (computed during RT)

@dataclass
class LineEnergy:
    """Energy levels associated with the transition."""
    E: float  # Lower energy level [eV]
    EP: float  # Upper energy level [eV]
    ELO: float  # Lower level excitation energy [eV]

@dataclass
class LineOscillatorStrength:
    """Oscillator strength and related line strength parameters."""
    GFLOG: float  # Log10 of (g * f) where g is statistical weight
    GF: float  # (g * f): product of weight and oscillator strength
    XJ: float  # Total angular momentum of lower level
    XJP: float  # Total angular momentum of upper level
    CODE: float  # Transition code

@dataclass
class LineBroadening:
    """Line broadening parameters from quantum mechanical calculations."""
    GAMMAR: float  # Radiative damping constant [s^-1]
    DGAMMAR: float  # Uncertainty in radiative damping
    GAMMAS: float  # Stark broadening parameter [cm^3 s^-1]
    DGAMMAS: float  # Uncertainty in Stark broadening
    GAMMAW: float  # Van der Waals broadening parameter [cm^3 s^-1]
    DGAMMAW: float  # Uncertainty in vdW broadening
    GS: float  # Stark broadening factor
    GR: float  # Radiative broadening factor
    GW: float  # Van der Waals broadening factor

@dataclass
class LineIdentification:
    """Labels and references identifying a spectral line."""
    LABEL: str  # Lower level term symbol
    LABELP: str  # Upper level term symbol
    OTHER1: str  # Additional label field 1
    OTHER2: str  # Additional label field 2
    REF: str  # Reference code (e.g., 'vald', 'nist', 'kurucz')

@dataclass
class LineExtraData:
    """Additional parameters and derivatives for spectral lines."""
    DGFLOG: float  # Uncertainty in log(gf)
    EXTRA1: float  # Extra parameter 1
    EXTRA2: float  # Extra parameter 2
    EXTRA3: float  # Extra parameter 3
    X1: float  # Lower state isotope mass shift [Angstrom]
    X2: float  # Upper state isotope mass shift [Angstrom]

@dataclass
class SpectralLine:
    """Complete description of a single spectral line."""
    wavelength: LineWavelength  # Wavelength information
    energy: LineEnergy  # Energy levels of transition
    quantum_numbers: LineQuantumNumbers  # Quantum numbers
    oscillator_strength: LineOscillatorStrength  # Oscillator strength
    broadening: LineBroadening  # Line broadening parameters
    identification: LineIdentification  # Labels and references
    extra_data: LineExtraData  # Additional parameters
    
    def transition_energy_eV(self) -> float:
        """Energy of the transition [eV]."""
        return self.energy.EP - self.energy.E

@dataclass
class ElementalAbundance:
    """Elemental abundance and atomic mass information."""
    ELEM: str  # Element symbol (H, He, C, O, Fe, etc.)
    Z: int  # Atomic number
    ABUND: float  # Abundance [dex] relative to reference scale
    ATMASS: float  # Atomic mass [atomic mass units]
    XABUND: Optional[float] = None  # Alternative abundance scale

@dataclass
class ElementalAbundances:
    """Collection of all elemental abundances in the model."""
    abundances: dict  # Dict[int Z, ElementalAbundance]
    WTMOLE: float  # Mean molecular weight [amu]
    
    def __getitem__(self, z: int) -> ElementalAbundance:
        return self.abundances.get(z)
    
    def __setitem__(self, z: int, abund: ElementalAbundance):
        self.abundances[z] = abund
