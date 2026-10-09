# Atmosphere Class - Design Documentation

## Overview

The `Atmosphere` class represents a complete stellar atmosphere model based on the ATLAS code's READIN subroutine. It organizes Fortran COMMON blocks into logically related Python dataclasses.

## Class Structure

### Core Components

The `Atmosphere` class is composed of several specialized dataclasses that group related physical quantities:

```
Atmosphere
├── stellar_params: StellarParameters
│   ├── teff: float (Effective temperature [K])
│   ├── logg: float (Surface gravity [log10(g cm/s^2)])
│   └── grav: float (Linear gravity [cm/s^2])
│
├── depth: DepthStructure
│   ├── RHOX: torch.Tensor (Depth coordinate, shape: (n_depth,))
│   ├── NRHOX: int (Number of depth points)
│   └── HEIGHT: torch.Tensor (Height [cm], shape: (n_depth,))
│
├── temperature: TemperatureStructure
│   ├── T: torch.Tensor (Temperature [K], shape: (n_depth,))
│   ├── TK: torch.Tensor (Temperature [kK], shape: (n_depth,))
│   ├── TLOG: torch.Tensor (log10(T), shape: (n_depth,))
│   ├── TKEV: torch.Tensor (Temperature [eV], shape: (n_depth,))
│   ├── HKT: torch.Tensor (h*k_B*T/c [CGS], shape: (n_depth,))
│   └── HCKT: torch.Tensor (h*c/k_B/T [CGS], shape: (n_depth,))
│
├── pressure: PressureAndDensity
│   ├── P: torch.Tensor (Gas pressure [dyne/cm^2], shape: (n_depth,))
│   ├── XNE: torch.Tensor (Electron density [cm^-3], shape: (n_depth,))
│   ├── XNATOM: torch.Tensor (Atomic density [cm^-3], shape: (n_depth,))
│   ├── RHO: torch.Tensor (Mass density [g/cm^3], shape: (n_depth,))
│   └── PTOTAL: torch.Tensor (Total pressure [dyne/cm^2], shape: (n_depth,))
│
├── radiation: RadiationField
│   ├── prad: torch.Tensor (Radiation pressure [dyne/cm^2], shape: (n_depth,))
│   ├── accrad: torch.Tensor (Accumulated rad. pressure [dyne/cm^2], shape: (n_depth,))
│   ├── abross: torch.Tensor (Rosseland abs. coefficient, shape: (n_depth,))
│   ├── tauros: torch.Tensor (Rosseland optical depth, shape: (n_depth,))
│   ├── pzero: float (Reference pressure [dyne/cm^2])
│   ├── pcon: float (Pressure correction factor)
│   ├── pradk: torch.Tensor (Rad. pressure constant, shape: (n_depth,))
│   ├── pradk0: float (Initial radiation pressure)
│   ├── pturb0: float (Initial turbulent pressure)
│   ├── edens: torch.Tensor (Electron density, shape: (n_depth,))
│   └── flux: float (Bolometric flux [erg cm^-2 s^-1])
│
├── abundances: ElementalAbundances
│   ├── abund: torch.Tensor (Log abundances relative to H [99 elements], shape: (99,))
│   ├── xabund: torch.Tensor (Fractional abundances [99 elements], shape: (99,))
│   ├── atmass: torch.Tensor (Atomic masses [99 elements, amu], shape: (99,))
│   └── wtmole: float (Mean molecular weight [g/mol])
│
├── turbulence: TurbulenceAndConvection
│   ├── vturb: torch.Tensor (Microturbulence [km/s], shape: (n_depth,))
│   ├── pturb: torch.Tensor (Turbulent pressure [dyne/cm^2], shape: (n_depth,))
│   ├── trbfdg, trbcon, trbpow, trbsnd: float (Turbulence parameters)
│   ├── ifturb: int (Turbulence flag: 0=off, 1=on)
│   ├── dltdlp: torch.Tensor (d(ln T)/d(ln P), shape: (n_depth,))
│   ├── velsnd: torch.Tensor (Sound velocity [cm/s], shape: (n_depth,))
│   ├── grdadb: torch.Tensor (Grad - adiabatic gradient, shape: (n_depth,))
│   ├── hscale: torch.Tensor (Scale height [cm], shape: (n_depth,))
│   ├── vconv: torch.Tensor (Convective velocity [cm/s], shape: (n_depth,))
│   ├── mixlth: float (Mixing length parameter)
│   └── ifconv: int (Convection flag: 0=off, 1=on)
│
├── opacity_flags: OpcityControlFlags
│   ├── ifcorr, ifpres, ifsurf, ifscat, ifmol, nlteon: int (Various flags)
│   └── ifop: torch.Tensor (20 opacity type flags, shape: (20,))
│
└── Other attributes:
    ├── title: str (Model title/description)
    ├── nlte_mode: bool (Non-LTE treatment active)
    └── max_iterations: int (Maximum iterations for calculation)
```

## Fortran COMMON Block Mapping

| COMMON Block | Python Class | Purpose |
|---|---|---|
| `/TEFF/` | `StellarParameters` | Effective temperature and gravity |
| `/TEMP/` | `TemperatureStructure` | Temperature in multiple units |
| `/STATE/` | `PressureAndDensity` | P, ρ, X_e, atomic density |
| `/RHOX/` | `DepthStructure` | Depth coordinate and height |
| `/ELEM/`, `/XABUND/` | `ElementalAbundances` | Element abundances and masses |
| `/TURBPR/` | `TurbulenceAndConvection` | Turbulence parameters |
| `/CONV/` | `TurbulenceAndConvection` | Convection-related quantities |
| `/RAD/`, `/PZERO/`, `/ABROSS/`, `/FLUX/` | `RadiationField` | Radiation, opacity, pressure |
| `/IF/` | `OpcityControlFlags` | Opacity control flags |

## Key Features

### 1. **Data Validation**
The `__post_init__` method validates that all depth-dependent arrays have consistent dimensions (NRHOX).

### 2. **Device Movement**
The `to_device(device)` method facilitates moving all tensors to CPU or CUDA for batch processing.

### 3. **Summary Information**
The `summary()` method provides a human-readable overview of the model:
```python
print(atmosphere.summary())
```

### 4. **Integration with Opacities**
The class is designed to work seamlessly with the existing `Opacities` class:
```python
opacities = Opacities()
atmosphere = Atmosphere(...)
# Use together for spectral synthesis
```

## Usage Example

```python
import torch
from python.kurucz.atmosphere import (
    Atmosphere, StellarParameters, TemperatureStructure, 
    PressureAndDensity, DepthStructure, RadiationField,
    ElementalAbundances, TurbulenceAndConvection, OpcityControlFlags
)
from python.kurucz.stellar_state import StellarParameters

# Create stellar parameters
stellar_params = StellarParameters(teff=5777, logg=4.44)

# Create depth structure (72 points as in ATLAS)
n_depth = 72
rhox = torch.logspace(-6, 2, n_depth)
depth = DepthStructure(RHOX=rhox, NRHOX=n_depth)

# Create temperature structure
T = torch.linspace(3000, 8000, n_depth)
temperature = TemperatureStructure(T=T)

# Create other components...
pressure = PressureAndDensity(
    P=torch.ones(n_depth) * 1e6,
    XNE=torch.ones(n_depth) * 1e12,
    XNATOM=torch.ones(n_depth) * 1e13,
    RHO=torch.ones(n_depth) * 1e-6,
    PTOTAL=torch.ones(n_depth) * 1e6,
)

# ... continue with other components ...

# Create atmosphere
atmosphere = Atmosphere(
    stellar_params=stellar_params,
    depth=depth,
    temperature=temperature,
    pressure=pressure,
    # ... other components ...
)

# Print summary
print(atmosphere.summary())

# Move to GPU if available
if torch.cuda.is_available():
    atmosphere = atmosphere.to_device('cuda:0')
```

## Notes

- All depth-dependent arrays have shape `(NRHOX,)` for 1D profiles
- Temperature is stored in multiple units to match ATLAS conventions
- The class uses PyTorch tensors for GPU compatibility
- Abundance data covers 99 elements (Z=1 to Z=99)
- Opacity flags control which physical processes are included in calculations
