# SPECTRV COMMON Blocks → Python Classes

## Overview

This document describes the conversion of Fortran COMMON blocks from `spectrv.patched.for` into Python dataclasses. The original SPECTRV program uses COMMON blocks for global variable sharing; the Python equivalent uses dataclasses and composite objects for type-safe, organized data management.

## File Organization

The COMMON block variables are organized into 5 Python modules by domain:

| Module | File | Domain | Key Classes |
|--------|------|--------|-----------|
| **Stellar State** | `stellar_state.py` | Atmospheric structure | `StellarParameters`, `TemperatureStructure`, `PressureAndDensity`, `DepthStructure`, `AtmosphericState` |
| **Line Data** | `line_data.py` | Spectral lines & abundances | `SpectralLine`, `LineQuantumNumbers`, `LineBroadening`, `ElementalAbundances` |
| **Radiative Transfer** | `radiative_transfer_state.py` | Radiative transfer state | `RadiativeTransferState`, `OpticalDepthAndSourceFunction`, `ContinuumOpacity`, `LineOpacity` |
| **Synthesis Config** | `spectral_synthesis_config.py` | Configuration & control | `SpectralSynthesisConfig`, `WavelengthGrid`, `ControlFlags`, `CoronaModel` |
| **Element Opacity** | `element_opacity.py` | Element-specific opacities | `HydrogenOpacity`, `HeliumOpacity`, `CarbonOpacity`, etc. |

---

## Mapping: COMMON Blocks → Python Classes

### 1. stellar_state.py

#### COMMON /TEFF/
```fortran
COMMON /TEFF/ TEFF, GRAV, GLOG
```
↓
```python
@dataclass
class StellarParameters:
    teff: float          # Effective temperature [K]
    logg: float          # Surface gravity [log10(g)]
    grav: Optional[float]  # Linear gravity [cm/s^2]
```

---

#### COMMON /TEMP/
```fortran
COMMON /TEMP/ T(kw), TKEV(kw), TK(kw), HKT(kw), TLOG(kw), HCKT(kw), ITEMP
```
↓
```python
@dataclass
class TemperatureStructure:
    T: torch.Tensor      # Temperature [K]
    TK: torch.Tensor     # Temperature / 1000 [kK]
    TLOG: torch.Tensor   # Log10(T)
    TKEV: torch.Tensor   # Temperature [eV]
    HKT: torch.Tensor    # h*k_B*T/c [CGS]
    HCKT: torch.Tensor   # h*c/k_B/T [CGS]
    ITEMP: int           # Iteration index
```

---

#### COMMON /STATE/
```fortran
COMMON /STATE/ P(kw), XNE(kw), XNATOM(kw), RHO(kw), PTOTAL(kw)
```
↓
```python
@dataclass
class PressureAndDensity:
    P: torch.Tensor      # Gas pressure [dyne/cm^2]
    XNE: torch.Tensor    # Electron density [cm^-3]
    XNATOM: torch.Tensor # Total atomic density [cm^-3]
    RHO: torch.Tensor    # Mass density [g/cm^3]
    PTOTAL: torch.Tensor # Total + radiation pressure [dyne/cm^2]
```

---

#### COMMON /RHOX/
```fortran
COMMON /RHOX/ RHOX(kw), NRHOX
```
↓
```python
@dataclass
class DepthStructure:
    RHOX: torch.Tensor   # Depth coordinate
    NRHOX: int           # Number of depth points
    HEIGHT: Optional[torch.Tensor]  # Height [cm]
```

---

#### COMMON /CONV/
```fortran
COMMON /CONV/ DLTDLP(kw), HEATCP(kw), DLRDLT(kw), VELSND(kw), 
              GRDADB(kw), HSCALE(kw), FLXCNV(kw), VCONV(kw), MIXLTH, IFCONV
```
↓
```python
@dataclass
class ConvectionZoneData:
    DLTDLP: torch.Tensor   # Temperature gradient dLnT/dLnP
    HEATCP: torch.Tensor   # Heat capacity parameter
    VELSND: torch.Tensor   # Sound velocity [cm/s]
    HSCALE: torch.Tensor   # Scale height [cm]
    FLXCNV: torch.Tensor   # Convective flux [erg/cm^2/s]
    VCONV: torch.Tensor    # Convective velocity [cm/s]
    MIXLTH: float          # Mixing length [cm]
    IFCONV: int            # Convection flag (0/1)
```

---

#### COMMON /RAD/
```fortran
COMMON /RAD/ ACCRAD(kw), PRAD(kw)
```
↓
```python
@dataclass
class RadiationPressure:
    ACCRAD: torch.Tensor   # Radiative acceleration [cm/s^2]
    PRAD: torch.Tensor     # Radiation pressure [dyne/cm^2]
```

---

#### Composite: AtmosphericState
```python
@dataclass
class AtmosphericState:
    stellar_params: StellarParameters
    temperature: TemperatureStructure
    pressure_density: PressureAndDensity
    depth: DepthStructure
    convection: Optional[ConvectionZoneData] = None
    radiation: Optional[RadiationPressure] = None
```
**Combines all atmosphere data into single container**

---

### 2. line_data.py

#### COMMON /LINDAT/
```fortran
COMMON /LINDAT/ WL, E, EP, LABEL, LABELP, OTHER1, OTHER2, WLVAC, CENTER, CONCEN, 
                NELION, GAMMAR, GAMMAS, GAMMAW, REF, NBLO, NBUP, ISO1, X1, ISO2, X2, 
                GFLOG, XJ, XJP, CODE, ELO, GF, GS, GR, GW, DWL, DGFLOG, ...
```
↓ (Split into multiple focused classes):

```python
@dataclass
class LineWavelength:
    WL: float              # Air wavelength [Å]
    WLVAC: float           # Vacuum wavelength [Å]
    DWL: float             # Wavelength uncertainty [Å]

@dataclass
class LineEnergy:
    E: float               # Lower energy [eV]
    EP: float              # Upper energy [eV]
    ELO: float             # Excitation energy [eV]

@dataclass
class LineQuantumNumbers:
    NELION: int            # Ionization state (1=neutral, 2=singly ionized, etc.)
    NBLO: int              # Lower level number
    NBUP: int              # Upper level number
    ISO1: int              # Isotope code (lower)
    ISO2: int              # Isotope code (upper)

@dataclass
class LineOscillatorStrength:
    GFLOG: float           # log10(g*f)
    GF: float              # g*f (statistical weight × oscillator strength)
    XJ: float              # Lower J
    XJP: float             # Upper J
    CODE: float            # Transition code

@dataclass
class LineBroadening:
    GAMMAR: float          # Radiative damping [s^-1]
    GAMMAS: float          # Stark broadening [cm^3 s^-1]
    GAMMAW: float          # Van der Waals broadening [cm^3 s^-1]
    GR: float              # Radiative factor
    GS: float              # Stark factor
    GW: float              # VdW factor

@dataclass
class LineIdentification:
    LABEL: str             # Lower term symbol
    LABELP: str            # Upper term symbol
    REF: str               # Reference code

@dataclass
class SpectralLine:
    wavelength: LineWavelength
    energy: LineEnergy
    quantum_numbers: LineQuantumNumbers
    oscillator_strength: LineOscillatorStrength
    broadening: LineBroadening
    identification: LineIdentification
    # ... plus methods for transition properties
```

---

#### COMMON /ELEM/ and /XABUND/
```fortran
COMMON /ELEM/ ABUND(99), ATMASS(99), ELEM(99)
COMMON /XABUND/ XABUND(99), WTMOLE
```
↓
```python
@dataclass
class ElementalAbundance:
    ELEM: str              # Element symbol (H, He, C, ...)
    Z: int                 # Atomic number
    ABUND: float           # Abundance [dex]
    ATMASS: float          # Atomic mass [amu]
    XABUND: Optional[float]  # Alternative scale

@dataclass
class ElementalAbundances:
    abundances: dict       # Dict[Z: int, ElementalAbundance]
    WTMOLE: float          # Mean molecular weight [amu]
```

---

### 3. radiative_transfer_state.py

#### COMMON /FREQ/
```fortran
COMMON /FREQ/ FREQ, FREQLG, EHVKT(kw), STIM(kw), BNU(kw), WAVENO
```
↓
```python
@dataclass
class FrequencyState:
    FREQ: float            # Frequency [Hz]
    FREQLG: float          # Log10(frequency)
    BNU: torch.Tensor      # Planck function [erg/cm^3/Hz/strad]
    EHVKT: torch.Tensor    # exp(-hν/k_B*T)
    STIM: torch.Tensor     # 1 - EHVKT (stimulated emission)
```

---

#### COMMON /TAUSHJ/
```fortran
COMMON /TAUSHJ/ TAUNU(kw), SNU(kw), HNU(kw), JNU(kw), JMINS(kw)
```
↓
```python
@dataclass
class OpticalDepthAndSourceFunction:
    TAUNU: torch.Tensor    # Optical depth τ_ν
    SNU: torch.Tensor      # Source function S_ν
    HNU: torch.Tensor      # H-moment (Eddington flux)
    JNU: torch.Tensor      # Mean intensity J_ν
    JMINS: torch.Tensor    # Min intensity (auxiliary)
```

---

#### COMMON /OPTOT/
```fortran
COMMON /OPTOT/ ACONT(kw), SCONT(kw), ALINE(kw), SLINE(kw), SIGMAC(kw), SIGMAL(kw)
```
↓
```python
@dataclass
class ContinuumOpacity:
    ACONT: torch.Tensor    # Continuum absorption [cm^2/g]
    SCONT: torch.Tensor    # Continuum scattering
    SIGMAC: torch.Tensor   # Continuum cross-section [cm^2]

@dataclass
class LineOpacity:
    ALINE: torch.Tensor    # Line absorption
    SLINE: torch.Tensor    # Line scattering
    SIGMAL: torch.Tensor   # Line cross-section
```

---

#### COMMON /OPS/
```fortran
COMMON /OPS/ ACOOL(kw), ALUKE(kw), AHOT(kw), SIGEL(kw), ALINES(kw), 
             SIGLIN(kw), AXLINE(kw), SIGXL(kw), AXCONT(kw), SIGX(kw), 
             SXLINE(kw), SXCONT(kw)
```
↓
```python
@dataclass
class DetailedOpacitySources:
    ACOOL: torch.Tensor    # Cooling opacity
    AHOT: torch.Tensor     # Hot opacity
    ALINES: torch.Tensor   # Line blanketing
    SIGEL: torch.Tensor    # Electron scattering
    AXLINE: torch.Tensor   # X-ray line opacity
    AXCONT: torch.Tensor   # X-ray continuum
    # ... plus 6 more fields
```

---

#### Composite: RadiativeTransferState
```python
@dataclass
class RadiativeTransferState:
    frequency: FrequencyState
    optical_depth: OpticalDepthAndSourceFunction
    continuum_opacity: ContinuumOpacity
    line_opacity: LineOpacity
    detailed_opacities: Optional[DetailedOpacitySources] = None
    # ... plus methods for total opacity, albedo, etc.
```

---

### 4. spectral_synthesis_config.py

#### COMMON /FRESET/
```fortran
COMMON /FRESET/ FRESET(500), RCOSET(500), NULO, NUHI, NUMNU, IFWAVE, WBEGIN, DELTAW
```
↓
```python
@dataclass
class WavelengthGrid:
    WBEGIN: float          # Starting wavelength [Å]
    DELTAW: float          # Resolution (λ/Δλ)
    NULO: int              # First wavelength index
    NUHI: int              # Last wavelength index
    NUMNU: int             # Number of points
    # ... plus properties
```

---

#### COMMON /MUS/
```fortran
COMMON /MUS/ ANGLE(20), SURFI(20), NMU
```
↓
```python
@dataclass
class SurfaceIntensityCalculation:
    ANGLE: torch.Tensor    # Viewing angles μ = cos(θ)
    SURFI: torch.Tensor    # Surface intensity [erg/cm^2/Hz/strad]
    NMU: int               # Number of angles
```

---

#### COMMON /TURBPR/
```fortran
COMMON /TURBPR/ VTURB(kw), PTURB(kw), TRBFDG, TRBCON, TRBPOW, TRBSND, IFTURB
```
↓
```python
@dataclass
class TurbulentVelocity:
    VTURB: torch.Tensor    # Microturbulent velocity [cm/s]
    PTURB: torch.Tensor    # Turbulent pressure [dyne/cm^2]
    TRBFDG: float          # Fudge factor
    TRBCON: float          # Constant
    TRBPOW: float          # Power law exponent
    IFTURB: int            # Flag (0/1)
```

---

#### COMMON /IF/
```fortran
COMMON /IF/ IFCORR, IFPRES, IFSURF, IFSCAT, IFMOL, NLTEON, IFOP(20)
```
↓
```python
@dataclass
class ControlFlags:
    IFPRES: int            # Pressure flag
    IFSURF: int            # Surface type (1=flux, 2=intensity)
    IFSCAT: int            # Scattering (0/1)
    IFMOL: int             # Molecules (0/1)
    NLTEON: int            # Non-LTE (0/1)
    IFOP: torch.Tensor     # 20 opacity control flags
    # ... plus properties for boolean checks
```

---

#### COMMON /CORONO/
```fortran
COMMON /CORONO/ RHOXCO(42), TCO(42), XNECO(42), SCO(42), TCOLOG(42), 
                VCO(42), ACORON(42), SCORON(42), IFCORO, NCORO
```
↓
```python
@dataclass
class CoronaModel:
    RHOXCO: torch.Tensor   # Corona depth coordinate
    TCO: torch.Tensor      # Corona temperature [K]
    XNECO: torch.Tensor    # Corona electron density [cm^-3]
    VCO: torch.Tensor      # Corona velocity [cm/s]
    IFCORO: int            # Corona flag (0/1)
    NCORO: int             # Number of corona points (42)
```

---

#### Composite: SpectralSynthesisConfig
```python
@dataclass
class SpectralSynthesisConfig:
    wavelength_grid: WavelengthGrid
    surface_intensity: SurfaceIntensityCalculation
    turbulence: TurbulentVelocity
    control_flags: Optional[ControlFlags] = None
    corona: Optional[CoronaModel] = None
    # ... plus properties for checking calculation mode
```

---

### 5. element_opacity.py

#### COMMON /BHYD/ (Hydrogen)
```fortran
COMMON /BHYD/ BHYD(kw,8), AHYD(kw), SHYD(kw), AH2P(kw), BMIN(kw), 
              AHMIN(kw), SHMIN(kw), SIGH(kw), SIGH2(kw), AHLINE(kw),
              SHLINE(kw), XNFPH(kw,2), XNFH(kw)
```
↓
```python
@dataclass
class HydrogenOpacity(ElementOpacity):
    element: str = "H"
    BHYD: torch.Tensor     # Bound-free opacity [shape: (n_depth, 8)]
    AHYD: torch.Tensor     # Absorption
    SHYD: torch.Tensor     # Scattering
    AH2P: torch.Tensor     # H2+ opacity
    BMIN: torch.Tensor     # H-minus opacity
    AHMIN: torch.Tensor    # H-minus absorption
    XNFPH: torch.Tensor    # Neutral/ionized number densities [shape: (n_depth, 2)]
    XNFH: torch.Tensor     # Total H density
```

---

#### Similar classes for other elements:
- `HeliumOpacity` (COMMON /BHE/, 29 + 6 opacity levels)
- `CarbonOpacity` (COMMON /BC/, 14 + 6 levels)
- `OxygenOpacity` (COMMON /BO/, 13 + 4 levels)
- `MagnesiumOpacity` (COMMON /BMG/, 11 + 6 levels)
- `SiliconOpacity` (COMMON /BSI/, 11 + 10 levels)
- `IronOpacity` (COMMON /BFE/, 15 levels)
- Plus aluminum, boron, calcium, sodium, potassium, etc.

---

#### COMMON /CHOH/ (Diatomic molecules)
```fortran
COMMON /CHOH/ XNFPCH(kw), XNFPOH(kw)
```
↓
```python
@dataclass
class DiatomicMolecularOpacity:
    XNFPCH: torch.Tensor   # CH number density [shape: (n_depth,)]
    XNFPOH: torch.Tensor   # OH number density
```

---

#### COMMON /BONE/ (Auxiliary)
```fortran
COMMON /BONE/ BONE(kw)
```
↓
```python
@dataclass
class AuxiliaryScaling:
    BONE: torch.Tensor     # Scaling factor [shape: (n_depth,)]
    BFUDGE: torch.Tensor   # Fudge factor for opacity correction
```

---

## Usage Examples

### Creating an Atmospheric State

```python
import torch
from kurucz import (
    StellarParameters, TemperatureStructure, PressureAndDensity,
    DepthStructure, AtmosphericState
)

# Create stellar parameters
stellar = StellarParameters(teff=5777.0, logg=4.438)

# Create temperature structure
T = torch.linspace(3500, 10000, 72)  # 72 depth points
temp = TemperatureStructure(T=T)  # Other arrays auto-computed

# Create pressure/density
P = torch.linspace(1e0, 1e4, 72)
XNE = torch.linspace(1e6, 1e9, 72)
RHO = torch.linspace(1e-7, 1e-3, 72)
pd = PressureAndDensity(
    P=P, XNE=XNE, XNATOM=XNE*10, RHO=RHO, 
    PTOTAL=P * 1.1  # With radiation pressure
)

# Create depth structure
RHOX = torch.linspace(0.01, 100, 72)
depth = DepthStructure(RHOX=RHOX, NRHOX=72)

# Combine into complete atmospheric state
atmosphere = AtmosphericState(
    stellar_params=stellar,
    temperature=temp,
    pressure_density=pd,
    depth=depth
)

# Move to GPU if available
atmosphere = atmosphere.to(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
```

---

### Creating Spectral Line Data

```python
from kurucz import (
    SpectralLine, LineWavelength, LineEnergy, LineQuantumNumbers,
    LineOscillatorStrength, LineBroadening, LineIdentification,
    LineExtraData
)

line = SpectralLine(
    wavelength=LineWavelength(WL=6562.79, WLVAC=6562.80, DWL=0.001),
    energy=LineEnergy(E=0.0, EP=1.89, ELO=0.0),
    quantum_numbers=LineQuantumNumbers(NELION=1, NBLO=2, NBUP=3, ISO1=0, ISO2=0),
    oscillator_strength=LineOscillatorStrength(
        GFLOG=-0.723, GF=0.189, XJ=1.0, XJP=2.0, CODE=0.0
    ),
    broadening=LineBroadening(
        GAMMAR=1e8, GAMMAS=1e-12, GAMMAW=1e-12,
        GR=1.0, GS=1.0, GW=1.0
    ),
    identification=LineIdentification(
        LABEL="3p", LABELP="3d", OTHER1="", OTHER2="", REF="NIST"
    ),
    extra_data=LineExtraData(DGFLOG=0.01, EXTRA1=0, EXTRA2=0, EXTRA3=0, X1=0, X2=0)
)

# Access properties
print(f"Transition energy: {line.transition_energy_eV()} eV")
print(f"Wavelength (vacuum): {line.wavelength.WLVAC} Å")
```

---

### Creating Radiative Transfer State

```python
from kurucz import (
    RadiativeTransferState, FrequencyState, OpticalDepthAndSourceFunction,
    ContinuumOpacity, LineOpacity
)

n_depth = 72

rt_state = RadiativeTransferState(
    frequency=FrequencyState(
        FREQ=5.0e14,  # Hz
        FREQLG=14.7,
        BNU=torch.ones(n_depth),  # Will compute
        EHVKT=torch.ones(n_depth) * 0.5,
        STIM=torch.ones(n_depth) * 0.5
    ),
    optical_depth=OpticalDepthAndSourceFunction(
        TAUNU=torch.linspace(0.01, 10, n_depth),
        SNU=torch.ones(n_depth),  # Source function
        HNU=torch.ones(n_depth) * 0.8,
        JNU=torch.ones(n_depth) * 0.5,
        JMINS=torch.zeros(n_depth)
    ),
    continuum_opacity=ContinuumOpacity(
        ACONT=torch.ones(n_depth) * 1e-8,
        SCONT=torch.ones(n_depth) * 1e-10,
        SIGMAC=torch.ones(n_depth) * 1e-24
    ),
    line_opacity=LineOpacity(
        ALINE=torch.ones(n_depth) * 1e-9,
        SLINE=torch.ones(n_depth) * 1e-11,
        SIGMAL=torch.ones(n_depth) * 1e-25
    )
)

# Compute derived quantities
total_opacity = rt_state.total_opacity
albedo = rt_state.albedo
```

---

## Key Design Principles

1. **Modular Organization**: Related variables grouped into focused dataclasses
2. **Type Safety**: Using `torch.Tensor` with explicit shapes for numpy-like arrays
3. **Optional Fields**: Uncommon or advanced features marked as Optional
4. **Composite Objects**: Small classes composed into larger ones (e.g., `AtmosphericState`)
5. **Documentation**: Every field has docstring explaining its physical meaning, units, and typical values
6. **Methods & Properties**: Derived quantities computed from primary data (e.g., `transition_energy_eV()`, `total_opacity`)
7. **PyTorch Native**: Uses PyTorch tensors for GPU acceleration compatibility

---

## Comparison: Fortran vs Python

| Aspect | Fortran COMMON | Python Dataclass |
|--------|----------------|-----------------|
| **Scope** | Global (entire program) | Explicit parameter passing |
| **Type Safety** | Minimal (REAL*8, REAL*4, INTEGER) | Strong (torch.Tensor, float, int) |
| **Organization** | Flat namespace | Hierarchical (nested dataclasses) |
| **Documentation** | Comments only | Type hints + docstrings |
| **Memory Layout** | Fixed at compile time | Dynamic, type-checked |
| **Debugging** | Implicit global state | Explicit, traceable data flow |

---

## Migration Path: Fortran → Python

To rewrite SPECTRV in Python/PyTorch:

1. **Read Input** → Use `AtmosphericState` + `ElementalAbundances` + `SpectralSynthesisConfig`
2. **Main Loop** → Iterate over wavelengths with `WavelengthGrid`
3. **Compute Opacities** → Update `RadiativeTransferState` with element-specific `Opacity` classes
4. **Radiative Transfer** → Implement `JOSH` using PyTorch (vectorized depth, batched wavelengths)
5. **Output** → Populate `RadiativeTransferState.optical_depth.HNU` and write spectrum

---

## Files Reference

- `stellar_state.py` (287 lines): Atmospheric structure
- `line_data.py` (328 lines): Spectral lines & abundances
- `radiative_transfer_state.py` (300 lines): Radiative transfer physics
- `spectral_synthesis_config.py` (369 lines): Configuration & control
- `element_opacity.py` (377 lines): Element-specific opacities
- `__init__.py` (130 lines): Module exports

**Total: ~1,791 lines of well-documented Python code**
