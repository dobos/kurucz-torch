# Flat Class Refactoring - Complete Summary

## Overview

All state classes have been refactored from nested dataclass structures to **single flat dataclasses**. This change simplifies the API while maintaining organization through comment groupings that correspond to Fortran COMMON blocks.

## Files Refactored

### 1. `stellar_state.py`

#### Before (Multiple Classes)
```python
from kurucz.stellar_state import StellarParameters, TemperatureStructure, PressureAndDensity, DepthStructure

stellar_params = StellarParameters(teff=5777, logg=4.44)
temp_struct = TemperatureStructure(T=T_grid)
pressure_struct = PressureAndDensity(P=P_grid, XNE=ne_grid, ...)
depth_struct = DepthStructure(RHOX=rhox_grid, NRHOX=72)

# Access: stellar_params.teff, temp_struct.T, pressure_struct.P
```

#### After (Single Flat Class)
```python
from kurucz.stellar_state import StellarAtmosphere

atm = StellarAtmosphere(
    teff=5777, logg=4.44,
    T=T_grid, P=P_grid, XNE=ne_grid,
    RHOX=rhox_grid, NRHOX=72, ...
)

# Access: atm.teff, atm.T, atm.P (all at same level)
```

#### Features Maintained
- ✓ `__post_init__()` - Computes `grav` from `logg` and derives temperature units
- ✓ Automatic conversion of temperature between units (K, kK, eV, log)

### 2. `radiative_transfer_state.py`

#### Before (Multiple Classes)
```python
from kurucz.radiative_transfer_state import (
    FrequencyState, OpticalDepthAndSourceFunction, 
    ContinuumOpacity, LineOpacity, DetailedOpacitySources,
    ReferenceDepthOpacity, OpaquenessMeasures
)

freq_state = FrequencyState(FREQ=1e15, BNU=bnu_grid, ...)
optical_state = OpticalDepthAndSourceFunction(TAUNU=tau_grid, SNU=s_grid, ...)
```

#### After (Single Flat Class)
```python
from kurucz.radiative_transfer_state import RadiativeTransferState

rt_state = RadiativeTransferState(
    FREQ=1e15, BNU=bnu_grid,
    TAUNU=tau_grid, SNU=s_grid,
    ACONT=acont_grid, ALINE=aline_grid, ...
)

# All fields accessible at same level: rt_state.FREQ, rt_state.TAUNU, etc.
```

#### Features Maintained
- ✓ `total_absorption()` - Returns continuum + line absorption
- ✓ `total_scattering()` - Returns continuum + line scattering
- ✓ `total_opacity()` - Returns total opacity (absorption + scattering)
- ✓ `albedo()` - Computes single-scattering albedo

### 3. `atmosphere.py`

#### Before (Multiple Classes)
```python
from kurucz.atmosphere import (
    Atmosphere, ElementalAbundances, TurbulenceAndConvection,
    RadiationField, OpcityControlFlags,
    StellarParameters, TemperatureStructure, 
    PressureAndDensity, DepthStructure
)

atm = Atmosphere(
    stellar_params=StellarParameters(teff=5777, logg=4.44),
    temperature=TemperatureStructure(T=T_grid),
    pressure=PressureAndDensity(P=P_grid, XNE=ne_grid, ...),
    radiation=RadiationField(prad=prad_grid, ...),
    abundances=ElementalAbundances(abund=abund_grid, ...),
    turbulence=TurbulenceAndConvection(vturb=vturb_grid, ...),
    opacity_flags=OpcityControlFlags(ifmol=1, ifop=ifop_flags),
)

# Access: atm.stellar_params.teff, atm.temperature.T, atm.radiation.prad
```

#### After (Single Flat Class)
```python
from kurucz.atmosphere import Atmosphere

atm = Atmosphere(
    teff=5777, logg=4.44,
    T=T_grid, P=P_grid, XNE=ne_grid, PTOTAL=ptotal_grid,
    prad=prad_grid, abross=abross_grid, tauros=tauros_grid,
    abund=abund_grid, vturb=vturb_grid,
    ifmol=1, ifop=ifop_flags, ...
)

# Access: atm.teff, atm.T, atm.prad (all at same level)
```

#### Comment Organization
```python
# Logical grouping via comments (no nested classes):

# ========== Stellar parameters (COMMON /TEFF/) ==========
teff, logg, grav

# ========== Temperature structure (COMMON /TEMP/) ==========
T, TK, TLOG, TKEV, HKT, HCKT, ITEMP

# ========== Radiation field (COMMON /RAD/, /PZERO/, /FLUX/, /ABROSS/) ==========
prad, accrad, abross, tauros, pzero, pcon, pradk, pradk0, pturb0, edens, flux

# ... (7 more comment sections)
```

#### Features Maintained
- ✓ `__post_init__()` - Derives temperature units and computes gravity
- ✓ `to_device(device)` - Moves all tensors to CPU/CUDA
- ✓ `summary()` - Generates human-readable model overview

## Benefits of Flat Structure

| Aspect | Benefit |
|--------|---------|
| **API Simplicity** | Direct field access: `atm.T` instead of `atm.temperature.T` |
| **PyTorch Compatibility** | Works naturally with autograd and tensor operations |
| **Serialization** | Easier to save/load with torch.save() or pickle |
| **Type Hints** | IDE autocomplete works on all fields directly |
| **Optimization** | Simpler gradient tracking for ML workflows |
| **Debugging** | Flat structure easier to inspect and log |

## Field Organization

All classes maintain logical grouping through comment headers that correspond to Fortran COMMON blocks:

```
========== Header ==========
field1: type  # description
field2: type  # description

========== Next Header ==========
field3: type  # description
```

This provides **documentation without creating nested classes**.

## Migration Guide

If you have existing code using the old nested structure:

### Old Code
```python
model = Atmosphere(
    stellar_params=StellarParameters(teff=5777, logg=4.44),
    temperature=TemperatureStructure(T=torch.tensor([...]))
)
temp = model.temperature.T
teff = model.stellar_params.teff
```

### New Code
```python
model = Atmosphere(
    teff=5777, logg=4.44,
    T=torch.tensor([...])
)
temp = model.T
teff = model.teff
```

## Testing

All refactored files pass Python syntax checking:
```
✓ stellar_state.py
✓ radiative_transfer_state.py
✓ atmosphere.py
```

## File Statistics

| File | Lines | Classes | Fields |
|------|-------|---------|--------|
| stellar_state.py | 76 | 1 | 15 |
| radiative_transfer_state.py | 97 | 1 | 50+ |
| atmosphere.py | 264 | 1 | 100+ |

## Notes

- All comment groupings map to Fortran COMMON block names for historical reference
- Shape annotations (e.g., `Shape: (n_depth,)`) help with tensor dimension validation
- Default values maintain ATLAS conventions (e.g., NRHOX=72)
- Physical units are documented inline for each field
