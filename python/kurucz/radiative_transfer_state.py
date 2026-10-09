"""Radiative Transfer Quantities and Opacity Data

Complete radiative transfer state for a given frequency/wavelength point,
including all optical depth, source function, and opacity-related quantities.

Variable names match Fortran COMMON blocks for consistency with ATLAS code.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RadiativeTransferState:
    """Complete radiative transfer state for current frequency/wavelength.
    
    This flat class groups all radiative transfer quantities organized by
    physical concept for clarity, but all fields are directly accessible.
    
    Corresponds to radiative transfer calculation at a single wavelength/frequency.
    """
    
    # ========== Frequency-dependent quantities ==========
    FREQ: Optional[float] = None  # Frequency of current wavelength [Hz]
    FREQLG: Optional[float] = None  # Log10 of frequency
    WAVENO: Optional[float] = None  # Wavenumber [cm^-1]
    BNU: Optional['torch.Tensor'] = None  # Planck function value [erg/cm^3/Hz/strad] at each depth. Shape: (n_depth,)
    EHVKT: Optional['torch.Tensor'] = None  # Exponential term: exp(-hν/k_B*T) at each depth. Shape: (n_depth,)
    STIM: Optional['torch.Tensor'] = None  # Stimulated emission factor: 1 - EHVKT. Shape: (n_depth,)
    
    # ========== Optical depth and source function ==========
    TAUNU: Optional['torch.Tensor'] = None  # Optical depth τ_ν at each depth. Shape: (n_depth,)
    SNU: Optional['torch.Tensor'] = None  # Source function S_ν at each depth [erg/cm^3/Hz/strad]. Shape: (n_depth,)
    HNU: Optional['torch.Tensor'] = None  # H-moment (Eddington flux). Shape: (n_depth,)
    JNU: Optional['torch.Tensor'] = None  # Mean intensity J_ν [erg/cm^3/Hz/strad]. Shape: (n_depth,)
    JMINS: Optional['torch.Tensor'] = None  # Minimum intensity value. Shape: (n_depth,)
    
    # ========== Continuum opacity ==========
    ACONT: Optional['torch.Tensor'] = None  # Continuum absorption coefficient. Shape: (n_depth,)
    SCONT: Optional['torch.Tensor'] = None  # Continuum scattering coefficient. Shape: (n_depth,)
    SIGMAC: Optional['torch.Tensor'] = None  # Continuum cross-section per particle [cm^2]. Shape: (n_depth,)
    
    # ========== Line opacity ==========
    ALINE: Optional['torch.Tensor'] = None  # Line absorption coefficient. Shape: (n_depth,)
    SLINE: Optional['torch.Tensor'] = None  # Line scattering coefficient. Shape: (n_depth,)
    SIGMAL: Optional['torch.Tensor'] = None  # Line cross-section per particle [cm^2]. Shape: (n_depth,)
    
    # ========== Detailed opacity sources (various atomic/molecular processes) ==========
    ACOOL: Optional['torch.Tensor'] = None  # Cooling opacity. Shape: (n_depth,)
    ALUKE: Optional['torch.Tensor'] = None  # Luke's opacity contribution. Shape: (n_depth,)
    AHOT: Optional['torch.Tensor'] = None  # Hot opacity (UV region). Shape: (n_depth,)
    ALINES: Optional['torch.Tensor'] = None  # Line blanketing opacity. Shape: (n_depth,)
    SIGEL: Optional['torch.Tensor'] = None  # Electron scattering cross-section. Shape: (n_depth,)
    SIGLIN: Optional['torch.Tensor'] = None  # Line scattering cross-section. Shape: (n_depth,)
    AXLINE: Optional['torch.Tensor'] = None  # X-ray line opacity. Shape: (n_depth,)
    SIGXL: Optional['torch.Tensor'] = None  # X-ray line scattering cross-section. Shape: (n_depth,)
    AXCONT: Optional['torch.Tensor'] = None  # X-ray continuum opacity. Shape: (n_depth,)
    SIGX: Optional['torch.Tensor'] = None  # X-ray scattering cross-section. Shape: (n_depth,)
    SXLINE: Optional['torch.Tensor'] = None  # Additional X-ray line scattering term. Shape: (n_depth,)
    SXCONT: Optional['torch.Tensor'] = None  # Additional X-ray continuum scattering term. Shape: (n_depth,)
    
    # ========== Reference depth opacity ==========
    PZERO: Optional[float] = None  # Reference pressure [dyne/cm^2]
    PCON: Optional[float] = None  # Pressure-related constant
    PRADK0: Optional[float] = None  # Radiation pressure at reference depth [dyne/cm^2]
    PTURB0: Optional[float] = None  # Turbulent pressure at reference depth [dyne/cm^2]
    KNU: Optional['torch.Tensor'] = None  # Absorption opacity [cm^-1] at each depth. Shape: (n_depth,)
    PRADK: Optional['torch.Tensor'] = None  # Radiation pressure [dyne/cm^2]. Shape: (n_depth,)
    EDENS: Optional['torch.Tensor'] = None  # Energy density [erg/cm^3]. Shape: (n_depth,)
    
    # ========== Rosseland opacity and opaqueness measures ==========
    ABTOT: Optional['torch.Tensor'] = None  # Total opacity [cm^-1]. Shape: (n_depth,)
    ALPHA: Optional['torch.Tensor'] = None  # Opacity-related parameter (scattering fraction etc). Shape: (n_depth,)
    ABROSS: Optional['torch.Tensor'] = None  # Rosseland mean opacity [cm^-1]. Shape: (n_depth,)
    TAUROS: Optional['torch.Tensor'] = None  # Rosseland optical depth. Shape: (n_depth,)
    
    def total_absorption(self):
        """Total absorption opacity (continuum + line)."""
        return self.ACONT + self.ALINE
    
    def total_scattering(self):
        """Total scattering opacity (continuum + line)."""
        return self.SCONT + self.SLINE
    
    def total_opacity(self):
        """Total opacity (absorption + scattering)."""
        return self.total_absorption() + self.total_scattering()
    
    def albedo(self):
        """Single-scattering albedo: ω = σ / (κ + σ)."""
        total_opac = self.total_opacity()
        return self.total_scattering() / (total_opac + 1e-30)
