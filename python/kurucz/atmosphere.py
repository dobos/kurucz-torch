"""
Stellar Atmosphere Model

This module defines the Atmosphere class that represents a complete stellar
atmosphere model based on inputs from ATLAS READIN subroutine.

All parameters are organized into a single flat class with comment groupings
indicating their physical meaning, matching Fortran COMMON blocks.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
import torch
from .physics import Physics


@dataclass
class Atmosphere:
    """Complete stellar atmosphere model.
    
    Encapsulates all the data that READIN reads from input cards, organized
    into logical groups by physical meaning while maintaining a flat structure.
    
    The atmosphere is defined on a depth grid with NRHOX points, typically 72,
    representing different layers from the photosphere to deeper layers.
    
    Variable names match Fortran COMMON blocks for consistency with ATLAS code.
    
    Typical usage:
        atm = Atmosphere(
            TEFF=5777, GRAV=8.94e4,
            RHOX=rhox_grid, NRHOX=72,
            T=T_grid, P=P_grid, XNE=ne_grid, ...
        )
    """
    
    # ========== Stellar parameters (COMMON /TEFF/) ==========
    TEFF: float  # Effective temperature [K]
    GRAV: float  # Surface gravity [cm/s^2]
    GLOG: Optional[float] = None  # Log10 of gravity [log10(cm/s^2)]
    
    # ========== Depth structure (COMMON /RHOX/) ==========
    RHOX: "torch.Tensor" = None  # Rosseland optical depth. Shape: (n_depth,)
    NRHOX: int = 72  # Number of depth points
    
    # ========== Height (COMMON /HEIGHT/) ==========
    HEIGHT: Optional["torch.Tensor"] = None  # Height in atmosphere [cm]. Shape: (n_depth,)
    
    # ========== Temperature structure (COMMON /TEMP/) ==========
    T: "torch.Tensor" = None  # Temperature [K]. Shape: (n_depth,)
    TK: Optional["torch.Tensor"] = None  # Temperature [thousand K]. Shape: (n_depth,)
    TLOG: Optional["torch.Tensor"] = None  # Log10(T). Shape: (n_depth,)
    TKEV: Optional["torch.Tensor"] = None  # Temperature [eV]. Shape: (n_depth,)
    HKT: Optional["torch.Tensor"] = None  # h*k_B*T/c [CGS]. Shape: (n_depth,)
    HCKT: Optional["torch.Tensor"] = None  # h*c/k_B/T [CGS]. Shape: (n_depth,)
    ITEMP: int = 1  # Temperature iteration index
    
    # ========== Pressure and density (COMMON /STATE/) ==========
    P: "torch.Tensor" = None  # Gas pressure [dyne/cm^2]. Shape: (n_depth,)
    XNE: "torch.Tensor" = None  # Electron number density [cm^-3]. Shape: (n_depth,)
    XNATOM: "torch.Tensor" = None  # Total atomic density [cm^-3]. Shape: (n_depth,)
    RHO: "torch.Tensor" = None  # Mass density [g/cm^3]. Shape: (n_depth,)
    PTOTAL: "torch.Tensor" = None  # Total pressure [dyne/cm^2]. Shape: (n_depth,)
    
    # ========== Radiation field and opacity (COMMON /RAD/, /PZERO/, /ABROSS/) ==========
    PRAD: "torch.Tensor" = None  # Radiation pressure [dyne/cm^2]. Shape: (n_depth,)
    ACCRAD: "torch.Tensor" = None  # Accumulated radiation pressure. Shape: (n_depth,)
    ABROSS: "torch.Tensor" = None  # Rosseland mean absorption coefficient. Shape: (n_depth,)
    TAUROS: "torch.Tensor" = None  # Rosseland optical depth. Shape: (n_depth,)
    PZERO: Optional[float] = None  # Reference pressure [dyne/cm^2]
    PCON: Optional[float] = None  # Pressure correction factor
    PRADK0: Optional[float] = None  # Initial radiation pressure
    PTURB0: Optional[float] = None  # Initial turbulent pressure
    PRADK: "torch.Tensor" = None  # Radiation pressure constant. Shape: (n_depth,)
    KNU: "torch.Tensor" = None  # Absorption opacity [cm^-1]. Shape: (n_depth,)
    EDENS: "torch.Tensor" = None  # Energy density. Shape: (n_depth,)
    
    # ========== Bolometric flux (COMMON /FLUX/) ==========
    FLUX: Optional[float] = None  # Bolometric flux [erg cm^-2 s^-1]
    FLXERR: Optional["torch.Tensor"] = None  # Flux error. Shape: (n_depth,)
    FLXDRV: Optional["torch.Tensor"] = None  # Flux derivative. Shape: (n_depth,)
    FLXRAD: Optional["torch.Tensor"] = None  # Radiative flux. Shape: (n_depth,)
    
    # ========== Elemental abundances (COMMON /ELEM/, /XABUND/) ==========
    ABUND: Optional["torch.Tensor"] = None  # Log abundance relative to H [99 elements]. Shape: (99,)
    ATMASS: Optional["torch.Tensor"] = None  # Atomic masses [99 elements, amu]. Shape: (99,)
    XABUND: Optional["torch.Tensor"] = None  # Fractional abundances [99 elements]. Shape: (99,)
    WTMOLE: Optional[float] = None  # Mean molecular weight [g/mol]
    
    # ========== Turbulence (COMMON /TURBPR/) ==========
    VTURB: "torch.Tensor" = None  # Microturbulence velocity [km/s]. Shape: (n_depth,)
    PTURB: "torch.Tensor" = None  # Turbulent pressure [dyne/cm^2]. Shape: (n_depth,)
    TRBFDG: Optional[float] = None  # Turbulence fudge factor (damping)
    TRBCON: Optional[float] = None  # Turbulence correction factor
    TRBPOW: Optional[float] = None  # Turbulence power law exponent
    TRBSND: Optional[float] = None  # Turbulent sound velocity
    IFTURB: int = 0  # Turbulence flag (0=off, 1=on)
    
    # ========== Convection (COMMON /CONV/) ==========
    DLTDLP: Optional["torch.Tensor"] = None  # d(ln T) / d(ln P). Shape: (n_depth,)
    HEATCP: Optional["torch.Tensor"] = None  # Heat capacity. Shape: (n_depth,)
    DLRDLT: Optional["torch.Tensor"] = None  # d(ln rho) / d(ln T). Shape: (n_depth,)
    VELSND: Optional["torch.Tensor"] = None  # Sound velocity [cm/s]. Shape: (n_depth,)
    GRDADB: Optional["torch.Tensor"] = None  # Grad - adiabatic gradient. Shape: (n_depth,)
    HSCALE: Optional["torch.Tensor"] = None  # Scale height [cm]. Shape: (n_depth,)
    FLXCNV: Optional["torch.Tensor"] = None  # Convective flux. Shape: (n_depth,)
    VCONV: Optional["torch.Tensor"] = None  # Convective velocity [cm/s]. Shape: (n_depth,)
    MIXLTH: Optional[float] = None  # Mixing length parameter
    IFCONV: int = 0  # Convection flag (0=off, 1=on)
    
    # ========== Opacity control flags (COMMON /IF/) ==========
    IFCORR: int = 0  # Correction flag
    IFPRES: int = 0  # Pressure flag
    IFSURF: int = 0  # Surface flag
    IFSCAT: int = 0  # Scattering flag
    IFMOL: int = 0  # Molecular opacity flag (0=off, 1=on)
    NLTEON: int = 0  # Non-LTE electron number density flag
    IFOP: Optional["torch.Tensor"] = None  # Opacity flags for 20 species/processes. Shape: (20,)
    
    # ========== Configuration and metadata ==========
    TITLE: Optional[str] = None  # Model title/description. Shape: 74 characters
    NUMITS: int = 0  # Maximum iterations for model calculation (from COMMON /ITER/)
    
    # ========== Physics Calculations ==========
    
    def update(self):
        """Compute all derived quantities from raw input data.
        
        This method performs calculations based on the raw parameters read from
        the input file. It should be called after the file parser has populated
        the raw fields.
        
        Calculations performed (Fortran atlas7v.for reference):
        1. RHOX log-to-linear conversion if RHOX(1) < 0 (line 1142)
        2. Gravity conversion: if GRAV < 10, convert from log scale (line 200-208)
        3. Gravity log: GLOG = log10(GRAV) (line 208)
        4. Stefan-Boltzmann flux from effective temperature (line 100)
        5. Initialize scalar pressure parameters: PRADK0, PCON, PTURB0, PZER0 (lines 1143-1145)
        6. Per-depth radiation pressure (PRADK) from PRAD and PRADK0 (line 1145)
        
        Uses numpy for calculations and torch for array operations.
        """
        # ===== RHOX log-to-linear conversion (atlas7v.for lines 1141-1142) =====
        # If RHOX(1) < 0, convert all RHOX from log scale
        if self.RHOX is not None and self.NRHOX > 0:
            if float(self.RHOX[0]) < 0:
                # Convert from log scale: RHOX = 10^RHOX (torch tensor)
                self.RHOX = torch.from_numpy(np.power(10.0, self.RHOX.numpy()))
        
        # ===== Gravity processing (atlas7v.for lines 200-208) =====
        # Convert from log scale if needed (if GRAV < 10)
        if self.GRAV is not None and self.GRAV < 10.0:
            self.GRAV = float(np.power(10.0, self.GRAV))
        
        # Compute log gravity from linear gravity
        if self.GRAV is not None and self.GRAV > 0:
            self.GLOG = float(np.log10(self.GRAV))
        
        # ===== Flux from effective temperature (atlas7v.for line 100) =====
        if self.TEFF is not None:
            self.FLUX = Physics.stefan_boltzmann(self.TEFF)
        
        # ===== Initialize scalar pressure parameters (atlas7v.for lines 1143-1145) =====
        # PRADK0=0. (or already read), PTURB0=PTURB(1), PCON=0., PZER0=PCON+PRADK0+PTURB0
        if self.PRADK0 is None:
            self.PRADK0 = 0.0
        
        if self.PCON is None:
            self.PCON = 0.0
        
        if self.PTURB0 is None and self.PTURB is not None:
            self.PTURB0 = float(self.PTURB[0])
        elif self.PTURB0 is None:
            self.PTURB0 = 0.0
        
        # PZER0 = PCON + PRADK0 + PTURB0
        self.PZERO = float(self.PCON + self.PRADK0 + self.PTURB0)
        
        # ===== Per-depth radiation pressure (atlas7v.for line 1145) =====
        # Simple addition: PRADK(J) = PRAD(J) + PRADK0
        # PRAD is always a torch tensor
        if self.PRADK0 is not None and self.PRAD is not None:
            self.PRADK = self.PRAD + self.PRADK0
    
