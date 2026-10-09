# Fortran COMMON Blocks to Python Dataclasses Conversion

## Overview

This document describes the conversion of 40+ Fortran COMMON blocks from `spectrv.patched.for` into 5 modular Python dataclass modules. The conversion prioritizes:

1. **Type Safety**: Using Python type hints and PyTorch tensors
2. **Modularity**: Organizing related variables into semantic groups
3. **GPU Compatibility**: All arrays use `torch.Tensor` for GPU acceleration
4. **Documentation**: Every field includes meaning and physical units

## Project Structure

```
python/kurucz/
├── __init__.py                      # Module public API
├── stellar_state.py                 # Atmospheric structure (7 classes)
├── line_data.py                     # Spectral lines & abundances (10 classes)
├── radiative_transfer_state.py      # Opacity & RT quantities (8 classes)
├── spectral_synthesis_config.py     # Configuration & control (9 classes)
├── element_opacity.py               # Element-specific opacity (12 classes)
└── README_COMMON_BLOCKS.md          # Detailed mapping (legacy documentation)
```

## Module 1: stellar_state.py (202 lines)

Represents the physical structure of the stellar atmosphere.

### Classes:

#### 1. `StellarParameters`
**Corresponds to Fortran COMMON /TEFF/**

Effective temperature and gravity that define atmospheric structure.

| Field | Type | Meaning |
|-------|------|---------|
| `teff` | float | Effective temperature [K] |
| `logg` | float | Log10 gravity where g [cm/s^2] |
| `grav` | float (optional) | Linear gravity [cm/s^2], auto-computed from logg |

#### 2. `TemperatureStructure`
**Corresponds to Fortran COMMON /TEMP/**

Temperature at each depth point stored in multiple units for compatibility with Fortran code.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `T` | Tensor | (n_depth,) | Primary temperature [K] |
| `TK` | Tensor (auto) | (n_depth,) | Temperature in thousands [K], T/1000 |
| `TLOG` | Tensor (auto) | (n_depth,) | Log10(T) |
| `TKEV` | Tensor (auto) | (n_depth,) | Temperature [eV], T * k_B/e |
| `HKT` | Tensor (auto) | (n_depth,) | h*k_B*T/c [CGS] |
| `HCKT` | Tensor (auto) | (n_depth,) | h*c/k_B/T [CGS] |
| `ITEMP` | int | - | Iteration index (default: 1) |

**Note**: Fields `TK`, `TLOG`, `TKEV`, `HKT`, `HCKT` are auto-computed in `__post_init__()` from primary `T` array.

#### 3. `PressureAndDensity`
**Corresponds to Fortran COMMON /STATE/**

Gas pressure, densities, and related hydrodynamic quantities.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `P` | Tensor | (n_depth,) | Gas pressure [dyne/cm^2] |
| `XNE` | Tensor | (n_depth,) | Electron number density [cm^-3] |
| `XNATOM` | Tensor | (n_depth,) | Total atomic number density [cm^-3] |
| `RHO` | Tensor | (n_depth,) | Mass density [g/cm^3] |
| `PTOTAL` | Tensor | (n_depth,) | Total pressure incl. radiation [dyne/cm^2] |

#### 4. `DepthStructure`
**Corresponds to Fortran COMMON /RHOX/**

Depth coordinate and geometric properties.

| Field | Type | Meaning |
|-------|------|---------|
| `RHOX` | Tensor | Rosseland optical depth coordinate |
| `NRHOX` | int | Number of depth points (typically 72) |
| `HEIGHT` | Tensor (optional) | Height in atmosphere [cm or km] |

#### 5. `ConvectionZoneData`
**Corresponds to Fortran COMMON /CONV/**

Parameters describing convective zones.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `DLTDLP` | Tensor | (n_depth,) | dLnT/dLnP gradient |
| `HEATCP` | Tensor | (n_depth,) | Heat capacity related |
| `DLRDLT` | Tensor | (n_depth,) | Convective structure derivative |
| `VELSND` | Tensor | (n_depth,) | Sound velocity [cm/s] |
| `GRDADB` | Tensor | (n_depth,) | Adiabatic gradient |
| `HSCALE` | Tensor | (n_depth,) | Scale height [cm] |
| `FLXCNV` | Tensor | (n_depth,) | Convective flux [erg/cm^2/s] |
| `VCONV` | Tensor | (n_depth,) | Convective velocity [cm/s] |
| `MIXLTH` | float | - | Mixing length [cm] |
| `IFCONV` | int | - | Flag: 0=off, 1=on |

#### 6. `RadiationPressure`
**Corresponds to Fortran COMMON /RAD/**

Radiative pressure and acceleration.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `ACCRAD` | Tensor | (n_depth,) | Radiative acceleration [cm/s^2] |
| `PRAD` | Tensor | (n_depth,) | Radiation pressure [dyne/cm^2] |

#### 7. `AtmosphericState` (Composite)
**Root container for all atmospheric data**

Combines all 6 classes above plus optional convection/radiation.

| Field | Type | Meaning |
|-------|------|---------|
| `stellar_params` | StellarParameters | Teff, logg |
| `temperature` | TemperatureStructure | All temperature info |
| `pressure_density` | PressureAndDensity | P, ρ, n_e |
| `depth` | DepthStructure | Depth coordinate |
| `convection` | ConvectionZoneData (optional) | Convection data |
| `radiation` | RadiationPressure (optional) | Radiation data |

**Key Methods**:
- `n_depth`: Property returning number of depth points
- `device`: Property returning device (CPU/GPU)
- `to(device)`: Move all tensors to device (CPU/GPU migration)

---

## Module 2: line_data.py (108 lines)

Spectral line and elemental abundance information.

### Classes:

#### 1. `LineQuantumNumbers`
Quantum numbers identifying transition upper/lower states.

| Field | Type | Meaning |
|-------|------|---------|
| `NELION` | int | Ionization state (1=neutral, 2=singly ionized, ...) |
| `NBLO` | int | Lower level index |
| `NBUP` | int | Upper level index |
| `ISO1` | int | Lower state isotope code |
| `ISO2` | int | Upper state isotope code |

#### 2. `LineWavelength`
Wavelength and related intensity information.

| Field | Type | Meaning |
|-------|------|---------|
| `WL` | float | Air wavelength [Angstrom] |
| `WLVAC` | float | Vacuum wavelength [Angstrom] |
| `DWL` | float | Wavelength uncertainty [Angstrom] |
| `CENTER` | float (optional) | Line center intensity |
| `CONCEN` | float (optional) | Line wing intensity |

#### 3. `LineEnergy`
Energy levels of the transition.

| Field | Type | Meaning |
|-------|------|---------|
| `E` | float | Lower level energy [eV] |
| `EP` | float | Upper level energy [eV] |
| `ELO` | float | Excitation energy [eV] |

#### 4. `LineOscillatorStrength`
Oscillator strength and line strength.

| Field | Type | Meaning |
|-------|------|---------|
| `GFLOG` | float | Log10(g*f) where f = oscillator strength |
| `GF` | float | g*f product |
| `XJ` | float | Lower level total J |
| `XJP` | float | Upper level total J |
| `CODE` | float | Transition type code |

#### 5. `LineBroadening`
Quantum mechanical line broadening parameters.

| Field | Type | Meaning |
|-------|------|---------|
| `GAMMAR` | float | Radiative damping [s^-1] |
| `DGAMMAR` | float | Uncertainty in radiative damping |
| `GAMMAS` | float | Stark broadening [cm^3 s^-1] |
| `DGAMMAS` | float | Uncertainty in Stark |
| `GAMMAW` | float | Van der Waals broadening [cm^3 s^-1] |
| `DGAMMAW` | float | Uncertainty in vdW |

#### 6. `LineIdentification`
Labels and references.

| Field | Type | Meaning |
|-------|------|---------|
| `LABEL` | str | Lower term symbol |
| `LABELP` | str | Upper term symbol |
| `REF` | str | Reference code (vald, nist, kurucz) |

#### 7. `LineExtraData`
Additional parameters and isotope shifts.

| Field | Type | Meaning |
|-------|------|---------|
| `DGFLOG` | float | Uncertainty in log(gf) |
| `X1` | float | Lower isotope mass shift [Angstrom] |
| `X2` | float | Upper isotope mass shift [Angstrom] |

#### 8. `SpectralLine` (Composite)
**Complete line description** combining all above classes.

#### 9. `ElementalAbundance`
Single element's abundance and atomic mass.

| Field | Type | Meaning |
|-------|------|---------|
| `ELEM` | str | Element symbol (H, He, C, O, Fe, ...) |
| `Z` | int | Atomic number |
| `ABUND` | float | Abundance [dex] relative to solar |
| `ATMASS` | float | Atomic mass [amu] |

#### 10. `ElementalAbundances` (Composite)
Collection of all elemental abundances with dict interface.

---

## Module 3: radiative_transfer_state.py (100 lines)

Radiative transfer quantities and opacity data for specific wavelength.

### Classes:

#### 1. `FrequencyState`
Frequency-dependent Planck function and related.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `FREQ` | float | - | Frequency [Hz] |
| `FREQLG` | float | - | Log10(FREQ) |
| `BNU` | Tensor | (n_depth,) | Planck function [erg/cm^3/Hz/strad] |
| `EHVKT` | Tensor | (n_depth,) | exp(-hν/k_B T) |
| `STIM` | Tensor | (n_depth,) | Stimulated emission: 1 - EHVKT |

#### 2. `OpticalDepthAndSourceFunction`
τ_ν and S_ν along line of sight.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `TAUNU` | Tensor | (n_depth,) | Optical depth τ_ν |
| `SNU` | Tensor | (n_depth,) | Source function [erg/cm^3/Hz/strad] |
| `JNU` | Tensor | (n_depth,) | Mean intensity [erg/cm^3/Hz/strad] |
| `JMINS` | Tensor | (n_depth,) | Minimum intensity |

#### 3. `ContinuumOpacity`
Continuum opacity (electron scattering, bound-free).

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `ACONT` | Tensor | (n_depth,) | Absorption [cm^-1] |
| `SCONT` | Tensor | (n_depth,) | Scattering [cm^-1] |

#### 4. `LineOpacity`
Line opacity summed over all lines at this frequency.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `ALINE` | Tensor | (n_depth,) | Line absorption [cm^-1] |
| `SLINE` | Tensor | (n_depth,) | Line scattering [cm^-1] |

#### 5. `DetailedOpacitySources` (Optional)
Opacity decomposed by process (for diagnostics).

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `ACOOL` | Tensor | (n_depth,) | Cooling opacity |
| `AHOT` | Tensor | (n_depth,) | Hot opacity |
| `ALINES` | Tensor | (n_depth,) | Line blanketing |
| `SIGEL` | Tensor | (n_depth,) | Electron scattering cross-section |
| (+ 8 more for detailed decomposition) | | |

#### 6. `RadiativeTransferState` (Composite)
**Complete RT state** for current wavelength.

| Field | Type | Meaning |
|-------|------|---------|
| `frequency` | FrequencyState | Planck function info |
| `optical_depth` | OpticalDepthAndSourceFunction | τ_ν and S_ν |
| `continuum_opacity` | ContinuumOpacity | κ_c, σ_c |
| `line_opacity` | LineOpacity | κ_l, σ_l |
| `detailed_opacities` | DetailedOpacitySources (optional) | Process breakdown |

**Key Methods**:
- `total_absorption()`: κ_c + κ_l
- `total_scattering()`: σ_c + σ_l
- `total_opacity()`: κ + σ
- `albedo()`: ω = σ/(κ+σ)

---

## Module 4: spectral_synthesis_config.py (148 lines)

Configuration, control flags, and wavelength grid specification.

### Classes:

#### 1. `WavelengthGrid`
Wavelength/frequency grid for spectrum calculation.

| Field | Type | Meaning |
|-------|------|---------|
| `WBEGIN` | float | Starting wavelength [Angstrom] |
| `DELTAW` | float | Spectral resolution R = λ/Δλ |
| `WLBEG` | float | Beginning wavelength [Angstrom] |
| `WLEND` | float | Ending wavelength [Angstrom] |
| `NULO` | int | First wavelength point index (1-based) |
| `NUHI` | int | Last wavelength point index (1-based) |

#### 2. `SurfaceIntensityCalculation`
Configuration for angle-dependent intensity (limb darkening).

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `ANGLE` | Tensor | (n_angles,) | cos(θ), viewing angles |
| `SURFI` | Tensor | (n_angles,) | Surface intensity [erg/cm^2/Hz/strad] |
| `NMU` | int | - | Number of angles |

#### 3. `TurbulentVelocity`
Microturbulence parameters.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `VTURB` | Tensor | (n_depth,) | Microturbulent velocity [cm/s] |
| `PTURB` | Tensor | (n_depth,) | Turbulent pressure [dyne/cm^2] |
| `IFTURB` | int | - | Flag: 0=off, 1=on |

#### 4. `PartialRedistribution` (Optional)
Partial redistribution for scattering lines.

| Field | Type | Meaning |
|-------|------|---------|
| `PRDDOP` | float | Doppler width parameter [Angstrom] |
| `ITPRD` | int | PRD iteration type |
| `NITPRD` | int | Number of PRD iterations |

**Note**: Currently stubbed as disabled in SPECTRV.

#### 5. `ControlFlags`
Boolean flags controlling physics modules.

| Field | Type | Meaning |
|-------|------|---------|
| `IFSURF` | int | 1=flux, 2=intensity (multiple angles) |
| `IFSCAT` | int | Scattering flag: 0=off, 1=on |
| `IFMOL` | int | Molecular opacity: 0=atoms only, 1=molecules |
| `NLTEON` | int | Non-LTE flag: 0=LTE, 1=non-LTE |

#### 6. `IterationControl`
Iteration and output control.

| Field | Type | Meaning |
|-------|------|---------|
| `ITER` | int | Current iteration number |
| `NUMITS` | int | Total iterations |

#### 7. `VacuumAirWavelength`
Wavelength scale specification.

| Field | Type | Meaning |
|-------|------|---------|
| `IFVAC` | int | 0=air, 1=vacuum |

#### 8. `CoronaModel` (Optional)
Chromosphere/corona atmospheric extension.

| Field | Type | Shape | Meaning |
|-------|------|-------|---------|
| `RHOXCO` | Tensor | (42,) | Corona depth coordinate |
| `TCO` | Tensor | (42,) | Corona temperature [K] |
| `XNECO` | Tensor | (42,) | Corona electron density [cm^-3] |

#### 9. `SpectralSynthesisConfig` (Composite)
**Complete synthesis configuration**.

---

## Module 5: element_opacity.py (130 lines)

Element-specific bound-free opacity from photoionization.

### Classes:

#### Base: `ElementOpacity`
Abstract base for element opacity data.

#### Specific Elements (Hydrogen, Helium, Carbon, Oxygen, Magnesium, Silicon, Iron):

**HydrogenOpacity**: Most complex, 12+ arrays
- `BHYD`: Bound-free opacity levels (8 levels)
- `BMIN`: H-minus opacity
- `AHMIN`: H-minus absorption

**HeliumOpacity**: He and He+
- `BHE1`: Neutral He (29 levels)
- `BHE2`: He+ (6 levels)

**CarbonOpacity, OxygenOpacity, ..., IronOpacity**: Element-specific
- Each has BF1, BF2 opacity arrays with varying dimensions
- Element-specific absorption/scattering factors

#### 2. `DiatomicMolecularOpacity`
Diatomic molecules (CH, OH).

| Field | Type | Meaning |
|-------|------|---------|
| `XNFPCH` | Tensor | CH opacity/density |
| `XNFPOH` | Tensor | OH opacity/density |

#### 3. `AuxiliaryScaling`
Empirical correction factors.

| Field | Type | Meaning |
|-------|------|---------|
| `BONE` | Tensor | Auxiliary scaling (usually 1.0) |
| `BFUDGE` | Tensor | Opacity fudge factor |

#### 4. `FluxQuantities`
Flux-related quantities.

| Field | Type | Meaning |
|-------|------|---------|
| `FLUX` | float | Total flux [erg/cm^2/s] |

#### 5. `MiscellaneousData`
Metadata and auxiliary.

| Field | Type | Meaning |
|-------|------|---------|
| `TITLE` | str | Description (74 chars) |
| `FREQID` | str | Frequency ID (6 chars) |

---

## Design Principles

### 1. Modular Organization
Instead of flat 1:1 COMMON block mapping, organized into **5 semantic domains**:
- **stellar_state**: Atmospheric structure
- **line_data**: Spectral lines and abundances
- **radiative_transfer_state**: RT physics
- **spectral_synthesis_config**: Configuration
- **element_opacity**: Element opacities

**Rationale**: Future PyTorch implementation will work on these domains independently.

### 2. Composite Dataclasses
Higher-level containers aggregate related sub-dataclasses:
- `AtmosphericState` ← combines 6 lower-level classes
- `SpectralLine` ← combines 7 quantum/broadening classes
- `RadiativeTransferState` ← combines opacity and RT

**Rationale**: Prevents parameter explosion in function signatures; enables methods like `.to(device)`.

### 3. PyTorch Tensors Instead of NumPy
All depth-dependent arrays use `torch.Tensor`:
- Default device: CPU
- Can move to GPU via `.to(device)`
- Supports automatic differentiation (future)

**Trade-off**: Requires PyTorch as dependency, but essential for GPU acceleration.

### 4. Auto-Derived Quantities
Fields like `TK`, `TLOG`, `TKEV` are automatically computed in `__post_init__()`:
- Reduces redundancy
- Ensures consistency
- Matches Fortran behavior exactly

### 5. Optional Fields for Advanced Features
`DetailedOpacitySources`, `CoronaModel`, `PartialRedistribution` are `Optional`:
- Allows basic synthesis without them
- Gradual feature addition
- Cleaner basic usage

---

## Usage Examples

### Creating an Atmospheric State

```python
import torch
from kurucz import (
    AtmosphericState, StellarParameters, TemperatureStructure,
    PressureAndDensity, DepthStructure
)

n_depth = 72

# Stellar parameters
stellar = StellarParameters(teff=5777, logg=4.44)
# Automatically computes: grav = 10^4.44 ≈ 2.75e4 cm/s^2

# Temperature structure
temp = TemperatureStructure(
    T=torch.linspace(3500, 10000, n_depth)
)
# Automatically computes: TK, TLOG, TKEV, HKT, HCKT

# Pressure & density
pd = PressureAndDensity(
    P=torch.logspace(0.5, 4.5, n_depth),  # 1e0.5 to 1e4.5 dyne/cm^2
    XNE=torch.logspace(4, 14, n_depth),    # electron density
    XNATOM=torch.logspace(8, 18, n_depth),
    RHO=torch.logspace(-10, -2, n_depth),
    PTOTAL=torch.logspace(0.5, 4.5, n_depth)
)

# Depth structure
depth = DepthStructure(
    RHOX=torch.linspace(-6, 2, n_depth),
    NRHOX=n_depth
)

# Composite atmosphere
atm = AtmosphericState(
    stellar_params=stellar,
    temperature=temp,
    pressure_density=pd,
    depth=depth
)

print(f"Atmosphere at surface: T = {atm.temperature.T[0]:.0f} K")
print(f"Device: {atm.device}")
```

### Moving to GPU

```python
if torch.cuda.is_available():
    atm_gpu = atm.to(torch.device('cuda'))
    print(f"Moved to: {atm_gpu.device}")
```

### Creating a Spectral Line

```python
from kurucz import (
    SpectralLine, LineWavelength, LineEnergy,
    LineQuantumNumbers, LineOscillatorStrength,
    LineBroadening, LineIdentification, LineExtraData
)

line = SpectralLine(
    wavelength=LineWavelength(WL=5000.0, WLVAC=5001.2, DWL=0.01),
    energy=LineEnergy(E=0.0, EP=2.5, ELO=0.0),
    quantum_numbers=LineQuantumNumbers(NELION=1, NBLO=1, NBUP=2, ISO1=0, ISO2=0),
    oscillator_strength=LineOscillatorStrength(GFLOG=-1.5, GF=0.0316, XJ=0.5, XJP=1.5, CODE=1.0),
    broadening=LineBroadening(GAMMAR=1e7, DGAMMAR=0, GAMMAS=1e-12, DGAMMAS=0, ...),
    identification=LineIdentification(LABEL="1s 2S", LABELP="2p 2P", ...),
    extra_data=LineExtraData(DGFLOG=0.1, EXTRA1=0, ...)
)

print(f"Transition energy: {line.transition_energy_eV():.2f} eV")
```

---

## Migration Path: Rewriting SPECTRV

### Step 1: I/O Infrastructure
- Implement READIN: parse DECK6 format → populate `AtmosphericState`
- Implement file I/O: read fort.9, fort.10, spectrum.bin
- Unit tests: verify round-trip matches original Fortran

### Step 2: Core Physics
- Implement JOSH radiative transfer solver in PyTorch
- Solve dI_ν/dτ = I_ν - S_ν with boundary conditions
- Optimize for batched wavelength computation

### Step 3: Opacity Calculation
- Implement quadratic 3-point interpolation for opacity
- Line profile: Doppler, Stark, natural broadening
- Continuum: H-bound-free, H-minus, electron scattering

### Step 4: Advanced Features
- Partial redistribution (PRD)
- Corona model integration
- Non-LTE effects (NLTEON)

---

## File Mapping: Fortran COMMON → Python Classes

| Fortran COMMON | Python Class | Module |
|---|---|---|
| /TEFF/ | StellarParameters | stellar_state |
| /TEMP/ | TemperatureStructure | stellar_state |
| /STATE/ | PressureAndDensity | stellar_state |
| /RHOX/ | DepthStructure | stellar_state |
| /CONV/ | ConvectionZoneData | stellar_state |
| /RAD/ | RadiationPressure | stellar_state |
| Combination | AtmosphericState | stellar_state |
| /LINDAT/ | SpectralLine + LineQuantumNumbers | line_data |
| /WVLDAT/ | LineWavelength | line_data |
| /ENRGY/ | LineEnergy | line_data |
| /GFDAT/ | LineOscillatorStrength | line_data |
| /DAMP/ | LineBroadening | line_data |
| /ABUND/ | ElementalAbundance | line_data |
| /FREQVAL/ | FrequencyState | radiative_transfer_state |
| /ITAU/ | OpticalDepthAndSourceFunction | radiative_transfer_state |
| /ACONT/ | ContinuumOpacity | radiative_transfer_state |
| /ALINE/ | LineOpacity | radiative_transfer_state |
| Combination | RadiativeTransferState | radiative_transfer_state |
| /WAVE/ | WavelengthGrid | spectral_synthesis_config |
| /ANGLE/ | SurfaceIntensityCalculation | spectral_synthesis_config |
| /TURB/ | TurbulentVelocity | spectral_synthesis_config |
| /PRD/ | PartialRedistribution | spectral_synthesis_config |
| /FLAGS/ | ControlFlags | spectral_synthesis_config |
| /ITER/ | IterationControl | spectral_synthesis_config |
| /CORONA/ | CoronaModel | spectral_synthesis_config |
| Combination | SpectralSynthesisConfig | spectral_synthesis_config |
| /BHYD/, /BHE/, /BC/, etc. | HydrogenOpacity, HeliumOpacity, ... | element_opacity |
| /MOL/ | DiatomicMolecularOpacity | element_opacity |
| /SCALE/ | AuxiliaryScaling | element_opacity |
| /FLUX/ | FluxQuantities | element_opacity |
| /MISC/ | MiscellaneousData | element_opacity |

---

## Technical Notes

### Temperature Unit Conversions
Fortran stores temperature in 6 units for speed:
- T [K]
- TK [kK] = T / 1000
- TLOG = log₁₀(T)
- TKEV [eV] = T * k_B/e ≈ T * 8.617e-5
- HKT [CGS] = h*k_B*T/c ≈ 4.799e-11 * T
- HCKT [CGS] = h*c/k_B/T ≈ 5.050e-4 / T

Python automatically derives these from T in `__post_init__()`.

### Hydrogen Opacity Complexity
H has most complex opacity due to:
- Multiple bound levels (BHYD array)
- H-minus (H^-)
- Molecular H₂^+
- Line contributions
- Partial ionization (H⁰, H⁺)

### Fortran EQUIVALENCE Statements
Original Fortran used EQUIVALENCE to overlay REAL*8, REAL*4, and CHARACTER data in same memory.

Python equivalent: separate typed fields with no overlap (cleaner design).

### Fort.* File System
Binaries use symlinks fort.1, fort.2, ... for I/O:
- fort.9: Continuum opacity from SYNTHE
- fort.10: Line opacity from SYNTHE
- fort.11: Line data/parameters
- fort.17: Optional line-by-line output

Python implementation will read/write actual files directly.

