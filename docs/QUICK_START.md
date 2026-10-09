# Quick Start Guide: Kurucz Python Dataclasses

## Installation

Ensure PyTorch is installed:
```bash
pip install torch torchvision torchaudio
```

## Import

```python
from kurucz import (
    # Stellar atmosphere
    AtmosphericState, StellarParameters, TemperatureStructure,
    PressureAndDensity, DepthStructure,
    
    # Spectral lines
    SpectralLine, ElementalAbundance, ElementalAbundances,
    
    # Radiative transfer
    RadiativeTransferState, ContinuumOpacity, LineOpacity,
    
    # Configuration
    SpectralSynthesisConfig, WavelengthGrid, ControlFlags,
    
    # Element opacity
    HydrogenOpacity, HeliumOpacity, IronOpacity
)
import torch
```

## Creating an Atmospheric State

```python
import torch
from kurucz import AtmosphericState, StellarParameters, TemperatureStructure
from kurucz import PressureAndDensity, DepthStructure

# Number of depth points (typically 72 for ATLAS models)
n_depth = 72

# 1. Stellar parameters
stellar = StellarParameters(teff=5777.0, logg=4.44)
# Automatically computes: grav = 10^4.44 ≈ 2.751e4 cm/s^2

# 2. Temperature structure (K at each depth)
temp = TemperatureStructure(
    T=torch.linspace(3500, 10000, n_depth)
)
# Automatically computes:
#   - TK = T / 1000 [thousands K]
#   - TLOG = log10(T)
#   - TKEV = T * 8.617e-5 [eV]
#   - HKT = 4.799e-11 * T [CGS]
#   - HCKT = 5.050e-4 / T [CGS]

# 3. Pressure and density
pressure = PressureAndDensity(
    P=torch.logspace(0.5, 4.5, n_depth),     # 1e0.5 to 1e4.5 dyne/cm^2
    XNE=torch.logspace(4, 14, n_depth),      # electron density
    XNATOM=torch.logspace(8, 18, n_depth),   # atomic density
    RHO=torch.logspace(-10, -2, n_depth),    # mass density
    PTOTAL=torch.logspace(0.5, 4.5, n_depth) # total pressure
)

# 4. Depth structure
depth = DepthStructure(
    RHOX=torch.linspace(-6, 2, n_depth),
    NRHOX=n_depth
)

# 5. Composite atmospheric state
atm = AtmosphericState(
    stellar_params=stellar,
    temperature=temp,
    pressure_density=pressure,
    depth=depth
)

print(f"Effective temperature: {atm.stellar_params.teff} K")
print(f"Number of depth points: {atm.n_depth}")
print(f"Temperature range: {atm.temperature.T.min():.0f}-{atm.temperature.T.max():.0f} K")
print(f"Log10(T) range: {atm.temperature.TLOG.min():.2f}-{atm.temperature.TLOG.max():.2f}")
```

## GPU Migration

```python
# Check if GPU available
if torch.cuda.is_available():
    # Move to GPU (all tensors at once!)
    atm_gpu = atm.to(torch.device('cuda'))
    print(f"Running on: {atm_gpu.device}")
    
    # Move back to CPU
    atm_cpu = atm_gpu.to(torch.device('cpu'))
```

## Creating a Spectral Line

```python
from kurucz import SpectralLine, LineWavelength, LineEnergy
from kurucz import LineQuantumNumbers, LineOscillatorStrength
from kurucz import LineBroadening, LineIdentification, LineExtraData

line = SpectralLine(
    wavelength=LineWavelength(
        WL=5000.0,      # air wavelength [Angstrom]
        WLVAC=5001.2,   # vacuum wavelength [Angstrom]
        DWL=0.01        # uncertainty [Angstrom]
    ),
    energy=LineEnergy(
        E=0.0,      # lower level [eV]
        EP=2.5,     # upper level [eV]
        ELO=0.0     # excitation energy [eV]
    ),
    quantum_numbers=LineQuantumNumbers(
        NELION=1, NBLO=1, NBUP=2, ISO1=0, ISO2=0
    ),
    oscillator_strength=LineOscillatorStrength(
        GFLOG=-1.5, GF=0.0316, XJ=0.5, XJP=1.5, CODE=1.0
    ),
    broadening=LineBroadening(
        GAMMAR=1e7, DGAMMAR=0.0,
        GAMMAS=1e-12, DGAMMAS=0.0,
        GAMMAW=1e-14, DGAMMAW=0.0,
        GS=0.0, GR=0.0, GW=0.0
    ),
    identification=LineIdentification(
        LABEL="1s 2S", LABELP="2p 2P",
        OTHER1="", OTHER2="",
        REF="kurucz"
    ),
    extra_data=LineExtraData(
        DGFLOG=0.1, EXTRA1=0.0, EXTRA2=0.0, EXTRA3=0.0,
        X1=0.0, X2=0.0
    )
)

# Access computed properties
E_transition = line.transition_energy_eV()
print(f"Transition energy: {E_transition:.2f} eV")
print(f"Line center: {line.wavelength.WL:.2f} Angstrom")
```

## Creating Elemental Abundances

```python
from kurucz import ElementalAbundance, ElementalAbundances

# Create individual element abundances (relative to solar, in dex)
H = ElementalAbundance(ELEM="H", Z=1, ABUND=12.0, ATMASS=1.008)
He = ElementalAbundance(ELEM="He", Z=2, ABUND=10.93, ATMASS=4.003)
C = ElementalAbundance(ELEM="C", Z=6, ABUND=8.43, ATMASS=12.011)
N = ElementalAbundance(ELEM="N", Z=7, ABUND=7.83, ATMASS=14.007)
O = ElementalAbundance(ELEM="O", Z=8, ABUND=8.69, ATMASS=15.999)
Fe = ElementalAbundance(ELEM="Fe", Z=26, ABUND=7.50, ATMASS=55.845)

# Create collection
abundances = ElementalAbundances(
    abundances={
        1: H, 2: He, 6: C, 7: N, 8: O, 26: Fe
    },
    WTMOLE=1.3  # Mean molecular weight [amu]
)

# Access by Z
print(f"Carbon abundance: {abundances[6].ABUND:.2f} dex")
```

## Creating Radiative Transfer State

```python
from kurucz import RadiativeTransferState, FrequencyState
from kurucz import ContinuumOpacity, LineOpacity

rt_state = RadiativeTransferState(
    frequency=FrequencyState(
        FREQ=5.0e14,  # frequency [Hz]
        FREQLG=14.7,  # log10(FREQ)
        BNU=torch.logspace(-20, -15, n_depth),  # Planck function
        EHVKT=torch.linspace(1e-3, 1.0, n_depth),  # exp(-hν/k_B T)
        STIM=torch.linspace(0, 0.99, n_depth)   # 1 - EHVKT
    ),
    optical_depth=OpticalDepthAndSourceFunction(
        TAUNU=torch.logspace(-3, 2, n_depth),  # optical depth
        SNU=torch.logspace(-20, -15, n_depth),  # source function
        JNU=torch.logspace(-20, -15, n_depth),  # mean intensity
        JMINS=torch.logspace(-20, -15, n_depth) # min intensity
    ),
    continuum_opacity=ContinuumOpacity(
        ACONT=torch.logspace(-5, 0, n_depth),  # absorption [cm^-1]
        SCONT=torch.logspace(-8, -3, n_depth),  # scattering [cm^-1]
        SIGMAC=torch.logspace(-18, -13, n_depth) # cross-section
    ),
    line_opacity=LineOpacity(
        ALINE=torch.logspace(-6, -1, n_depth),  # line absorption
        SLINE=torch.logspace(-10, -5, n_depth),  # line scattering
        SIGMAL=torch.logspace(-20, -15, n_depth) # line cross-section
    )
)

# Compute useful quantities
kappa = rt_state.total_absorption()  # total absorption
sigma = rt_state.total_scattering()  # total scattering
tau = rt_state.total_opacity()       # total opacity
w = rt_state.albedo()                # single-scattering albedo

print(f"Total opacity range: {tau.min():.2e} to {tau.max():.2e} cm^-1")
print(f"Albedo range: {w.min():.4f} to {w.max():.4f}")
```

## Creating Spectral Synthesis Configuration

```python
from kurucz import SpectralSynthesisConfig, WavelengthGrid
from kurucz import SurfaceIntensityCalculation, TurbulentVelocity, ControlFlags

config = SpectralSynthesisConfig(
    wavelength_grid=WavelengthGrid(
        WBEGIN=4000.0,
        DELTAW=50000.0,  # Resolution R = lambda/delta_lambda
        WLBEG=3900.0,
        WLEND=10000.0,
        NULO=1,
        NUHI=100,
        NUMNU=100,
        IFWAVE=0
    ),
    surface_intensity=SurfaceIntensityCalculation(
        ANGLE=torch.tensor([0.2, 0.4, 0.6, 0.8, 1.0]),  # cos(theta)
        SURFI=torch.zeros(5),  # [computed in runtime]
        NMU=5  # 5 viewing angles
    ),
    turbulence=TurbulentVelocity(
        VTURB=torch.full((n_depth,), 1e5),  # 1 km/s constant
        PTURB=torch.zeros(n_depth),
        IFTURB=1,  # turbulence on
        TRBFDG=1.0,
        TRBCON=1.0,
        TRBPOW=1.0,
        TRBSND=1.0
    ),
    control_flags=ControlFlags(
        IFCORR=0,
        IFPRES=1,
        IFSURF=2,    # 2 = intensity (multiple angles)
        IFSCAT=1,    # 1 = include scattering
        IFMOL=1,     # 1 = include molecules
        NLTEON=0,    # 0 = LTE
        IFOP=torch.zeros(20, dtype=torch.int)
    )
)

print(f"Resolution R = {config.wavelength_grid.resolution}")
print(f"Number of angles: {config.surface_intensity.NMU}")
print(f"Scattering: {'ON' if config.control_flags.with_scattering else 'OFF'}")
print(f"Molecules: {'ON' if config.control_flags.with_molecules else 'OFF'}")
```

## Common Patterns

### Move Everything to GPU
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
atm = atm.to(device)
rt_state.frequency.BNU = rt_state.frequency.BNU.to(device)
# ... etc for all tensors
```

### Create Batch of Wavelengths
```python
n_waves = 1000
n_depth = 72

# Create array of RT states, one per wavelength
rt_states = []
for i in range(n_waves):
    freq = 1e14 * (1 + i / n_waves)
    rt = RadiativeTransferState(
        frequency=FrequencyState(FREQ=freq, FREQLG=np.log10(freq), ...),
        # ...
    )
    rt_states.append(rt)
```

### Access All Temperatures
```python
T_kelvin = atm.temperature.T
T_kilo = atm.temperature.TK
T_log = atm.temperature.TLOG
T_eV = atm.temperature.TKEV

# All automatically consistent!
assert torch.allclose(T_kilo, T_kelvin / 1000)
assert torch.allclose(T_eV, T_kelvin * 8.617333262e-5)
```

## Module Organization

- **stellar_state.py**: Atmosphere structure (T, P, ρ, depth)
- **line_data.py**: Spectral line data and abundances
- **radiative_transfer_state.py**: Opacity and RT quantities
- **spectral_synthesis_config.py**: Configuration and control flags
- **element_opacity.py**: Element-specific bound-free opacity

## Next Steps

1. **Read from DECK6 format** → populate `AtmosphericState`
2. **Read SYNTHE outputs** → populate `RadiativeTransferState`
3. **Implement JOSH solver** → compute radiative transfer in PyTorch
4. **Write spectrum** → output binary spectrum file

See `COMMON_BLOCKS_TO_PYTHON.md` for detailed documentation and migration path.
