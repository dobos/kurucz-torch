"""Spectral Synthesis Configuration and Output"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class WavelengthGrid:
    """Specification of the wavelength/frequency grid for spectrum calculation."""
    WBEGIN: float  # Starting wavelength [Angstrom]
    DELTAW: float  # Wavelength spacing / Resolution (λ/Δλ)
    WLBEG: float  # Beginning wavelength [Angstrom]
    WLEND: float  # Ending wavelength [Angstrom]
    NULO: int  # First wavelength point index (1-based)
    NUHI: int  # Last wavelength point index (1-based)
    NUMNU: int  # Total number of wavelength points
    IFWAVE: int  # Wavelength flag
    FRESET: Optional['torch.Tensor'] = None  # Frequency reset values. Shape: (500,)
    RCOSET: Optional['torch.Tensor'] = None  # Frequency reset coefficients. Shape: (500,)
    
    @property
    def resolution(self) -> float:
        """Spectral resolution R = λ/Δλ."""
        return self.DELTAW
    
    @property
    def n_wavelength_points(self) -> int:
        """Number of wavelength points in current grid."""
        return self.NUHI - self.NULO + 1

@dataclass
class SurfaceIntensityCalculation:
    """Configuration for angle-dependent intensity calculations."""
    ANGLE: 'torch.Tensor'  # Cosine of viewing angle: μ = cos(θ). Shape: (n_angles,)
    SURFI: 'torch.Tensor'  # Surface intensity [erg/cm^2/Hz/strad]. Shape: (n_angles,)
    NMU: int  # Number of viewing angles computed
    NMU2: Optional[int] = None  # 2 * NMU

@dataclass
class TurbulentVelocity:
    """Turbulent velocity and related dynamic parameters."""
    VTURB: 'torch.Tensor'  # Microturbulent velocity [cm/s]. Shape: (n_depth,)
    PTURB: 'torch.Tensor'  # Turbulent pressure [dyne/cm^2]. Shape: (n_depth,)
    TRBFDG: float  # Turbulent fudge factor
    TRBCON: float  # Turbulence constant
    TRBPOW: float  # Turbulence power law exponent
    TRBSND: float  # Turbulence sound speed relation parameter
    IFTURB: int  # Turbulence flag: 0 = off, 1 = on

@dataclass
class PartialRedistribution:
    """Partial redistribution (PRD) parameters for non-resonant scattering."""
    PRDDOP: float  # Doppler width parameter for PRD [Angstrom]
    PRDPOW: float  # Power law index for PRD frequency dependence
    ITPRD: int  # PRD iteration type flag
    NITPRD: int  # Number of PRD iterations
    SIGPRD: Optional['torch.Tensor'] = None  # PRD sigma parameter. Shape: (n_depth,)
    NUPRD: Optional[int] = None  # Current frequency point index
    LINPRD: Optional[int] = None  # Current line index
    
    @property
    def prd_enabled(self) -> bool:
        """Whether partial redistribution is enabled."""
        return self.PRDDOP > 0.0

@dataclass
class ControlFlags:
    """Boolean/integer flags controlling various aspects of the calculation."""
    IFCORR: int  # Correction flag
    IFPRES: int  # Pressure dependence flag
    IFSURF: int  # Surface output type: 1 = flux, 2 = intensity
    IFSCAT: int  # Scattering flag: 0 = no, 1 = yes
    IFMOL: int  # Molecular opacity flag: 0 = atoms only, 1 = molecules
    NLTEON: int  # Non-LTE flag: 0 = LTE, 1 = non-LTE
    IFOP: 'torch.Tensor'  # Opacity control flags. Shape: (20,)
    
    @property
    def with_scattering(self) -> bool:
        return self.IFSCAT == 1
    
    @property
    def with_molecules(self) -> bool:
        return self.IFMOL == 1
    
    @property
    def compute_flux(self) -> bool:
        return self.IFSURF == 1
    
    @property
    def non_lte(self) -> bool:
        return self.NLTEON == 1

@dataclass
class IterationControl:
    """Iteration and output control parameters."""
    ITER: int  # Current iteration number
    IFPRNT: 'torch.Tensor'  # Print flags (1-15). Shape: (15,)
    IFPNCH: 'torch.Tensor'  # Output flags (1-15). Shape: (15,)
    NUMITS: int  # Total number of iterations

@dataclass
class VacuumAirWavelength:
    """Wavelength scale specification (vacuum vs air)."""
    IFVAC: int  # Vacuum/air flag: 0 = air, 1 = vacuum
    AIR: float  # Air wavelength
    
    @property
    def is_vacuum(self) -> bool:
        return self.IFVAC == 1
    
    @property
    def is_air(self) -> bool:
        return self.IFVAC == 0

@dataclass
class CoronaModel:
    """Corona (chromosphere) atmospheric extension data."""
    RHOXCO: 'torch.Tensor'  # Depth coordinate in corona. Shape: (42,)
    TCO: 'torch.Tensor'  # Temperature in corona [K]. Shape: (42,)
    TCOLOG: 'torch.Tensor'  # Log10 of corona temperature. Shape: (42,)
    XNECO: 'torch.Tensor'  # Electron density in corona [cm^-3]. Shape: (42,)
    VCO: 'torch.Tensor'  # Velocity in corona [cm/s]. Shape: (42,)
    SCO: 'torch.Tensor'  # Source function in corona. Shape: (42,)
    ACORON: 'torch.Tensor'  # Corona absorption opacity. Shape: (42,)
    SCORON: 'torch.Tensor'  # Corona scattering opacity. Shape: (42,)
    IFCORO: int  # Corona flag: 0 = no corona, 1 = include
    NCORO: int  # Number of corona depth points (42)

@dataclass
class SpectralSynthesisConfig:
    """Complete configuration for spectral synthesis calculation."""
    wavelength_grid: WavelengthGrid  # Wavelength grid specification
    surface_intensity: SurfaceIntensityCalculation  # Angle-dependent intensity config
    turbulence: TurbulentVelocity  # Turbulent velocity parameters
    prd: Optional[PartialRedistribution] = None  # Partial redistribution (optional)
    control_flags: Optional[ControlFlags] = None  # Control flags (optional)
    iteration: Optional[IterationControl] = None  # Iteration control (optional)
    vacuum_air: Optional[VacuumAirWavelength] = None  # Wavelength scale (optional)
    corona: Optional[CoronaModel] = None  # Corona model (optional)
    
    @property
    def is_full_disk(self) -> bool:
        """Whether full disk (multiple viewing angles) is computed."""
        return self.surface_intensity.NMU > 1
    
    @property
    def has_corona(self) -> bool:
        """Whether corona extension is included."""
        return self.corona is not None and self.corona.IFCORO == 1
