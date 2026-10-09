# BasicATLAS Binary Execution Order for Stellar Spectrum Generation

## Overview
BasicATLAS is a Python wrapper for three Kurucz FORTRAN codes: ATLAS, SYNTHE, and DFSYNTHE. To generate a complete stellar spectrum, these binaries must be executed in a specific sequence.

## Complete Workflow

### Phase 1: Calculate Stellar Atmosphere Model (ATLAS)

This phase generates the temperature-pressure profile for the stellar atmosphere.

**Binary:** `atlas9mem.exe`

**Input:**
- Restart file (pre-computed model or gray atmosphere)
- ODF (Opacity Distribution Functions) files from Phase 2
- Rosseland mean opacities (from Phase 2)
- Stellar parameters (Teff, log g, vturb, abundances)

**Output:**
- `output_main.out` (detailed atmosphere structure)
- `output_summary.out` (condensed atmosphere model)

**Python Function:** `atlas()`

**Notes:**
- This phase must complete before Phase 3
- Phase 2 (ODF generation) only needs to run once for each set of chemical abundances
- Runs iteratively with convergence checking

---

### Phase 2: Calculate Opacity Distribution Functions (DFSYNTHE)

This phase is a prerequisite for Phase 1. It calculates opacity data needed by ATLAS. This phase only needs to be run once per set of chemical abundances, then can be reused for different Teff/log g values.

#### Step 1: Tabulate Number Densities
**Binaries (in sequence):**
1. `xnfdf.exe` - For each of 56 standard temperatures, tabulates atomic and molecular number densities

**Output:**
- `xnfpdf.dat`
- `xnfpdfmax.dat`

#### Step 2: Calculate Opacity Distribution Functions
**Binaries:**
1. `dfsynthe.exe` - Calculates opacity distribution functions (runs for each temperature)
2. `dfsortp.exe` - Sorts the opacity data (runs 5 times, once per turbulent velocity: 0, 1, 2, 4, 8 km/s)

**Output:** Multiple `dfp00t<temp>v<vturb>sortp.asc` files

#### Step 3: Merge ODF Files
**Binary:** `separatedf.exe` - Merges sorted data into single files per turbulent velocity

**Output:**
- `p00big<vturb>.bdf` (opacity distribution functions for each vturb)
- `p00lit<vturb>.bdf` (light opacity distribution functions)

#### Step 4: Calculate Rosseland Mean Opacities
**Binaries (in sequence, for each of 5 turbulent velocities):**
1. `kappa9.exe` - Computes Rosseland mean opacities for each vturb

**Output:** `kapm40k2.out` files

#### Step 5: Merge Rosseland Opacities
**Binary:** `kapreadts.exe` - Merges all turbulent velocity tables

**Output:** `kappa.ros` (final Rosseland mean opacity table)

**Python Function:** `dfsynthe()`

---

### Phase 3: Generate Synthetic Spectrum (SYNTHE)

This phase generates the final stellar spectrum given an ATLAS model atmosphere.

**Binaries (executed in this order):**

1. **`xnfpelsyn.exe`** - Computes chemical equilibrium at each atmospheric layer
   - Input: Model atmosphere from Phase 1
   - Output: Chemical composition data

2. **`synbeg.exe`** - Initializes spectral synthesis computation
   - Prepares wavelength grid and other parameters

3. **`rgfalllinesnew.exe`** - Processes atomic line data
   - Loads and processes atomic absorption line list

4. **`rmolecasc.exe`** - Processes molecular data (runs multiple times)
   - Called separately for each molecular species:
     - C2 (A-X, B-A, D-A, E-A bands)
     - CN (A-X, B-X, X-X)
     - CO (A-X, X-X)
     - SiH
     - SiO (A-X, E-A, X-X)
     - TiO
     - Chmasseron (internal reference state)
     - MgH, NH, OH

5. **`rh2ofast.exe`** - Processes water (H₂O) molecular data
   - Specialized for high-resolution water bands

6. **`synthe.exe`** - Computes line opacities
   - Combines all line opacity data
   - Integrates with continuum opacities

7. **`spectrv.exe`** - Final spectrum computation
   - Integrates radiative transfer equation
   - Produces emergent spectrum

**Output:**
- `spectrum.bin` (binary spectrum file with wavelength and flux)

**Python Function:** `synthe()`

**Notes:**
- Can be run multiple times for same ATLAS model with different parameters
- Handles wavelength ranges that exceed buffer size by splitting into batches
- Each batch runs through the complete SYNTHE pipeline sequentially

---

## Dependency Graph

```
Phase 2: DFSYNTHE Generation (must complete first, can be reused)
    xnfdf.exe
        ↓
    dfsynthe.exe → dfsortp.exe → separatedf.exe
        ↓              ↓
    (ODFs)         (sorted ODFs)
        ↓
    kappa9.exe → kapreadts.exe
        ↓
    (Rosseland mean opacities)
        ↓
    Creates: ODF directory with .bdf and .ros files
    
        ↓
        ↓ (required input)
        ↓

Phase 1: ATLAS Atmosphere Model
    atlas9mem.exe (uses ODFs from Phase 2)
        ↓
    Creates: Model atmosphere with T-P profile
    
        ↓
        ↓ (required input)
        ↓

Phase 3: SYNTHE Spectral Synthesis (can reuse Phase 1 output)
    xnfpelsyn.exe
        ↓
    synbeg.exe
        ↓
    rgfalllinesnew.exe
        ↓
    rmolecasc.exe (×16 for different molecules)
        ↓
    rh2ofast.exe
        ↓
    synthe.exe
        ↓
    spectrv.exe
        ↓
    spectrum.bin (final output)
```

---

## Typical Usage Pattern

```python
from atlas import *
from settings import Settings

# Step 1: Generate ODFs (only once per abundance set)
settings = Settings(teff=5777, logg=4.44)
dfsynthe('solar_ODF', settings)

# Step 2: Generate ATLAS model
atlas('solar_model', settings=settings, ODF='solar_ODF')

# Step 3: Generate spectrum (can reuse model)
synthe('solar_model', min_wl=300, max_wl=10000, res=600000)

# Step 4: Load and analyze spectrum
wl, flux = read_spectrum('solar_model')
```

---

## Key Points

1. **Two independent preliminary steps:**
   - DFSYNTHE (Phase 2) must complete first to generate ODFs
   - ATLAS (Phase 1) depends on ODFs but can use cached ODFs

2. **Linear pipeline for Phase 3:**
   - SYNTHE binaries execute strictly sequentially
   - Each binary processes the output of the previous one
   - Cannot skip or reorder these binaries

3. **Efficiency considerations:**
   - Phase 2 only needs to run once per chemical abundance mixture
   - Phase 1 model can be reused with different Phase 3 parameters
   - Multiple wavelength ranges can be processed in batches

4. **File types:**
   - ATLAS uses ASCII format files (.out, .dat)
   - DFSYNTHE uses both ASCII (.asc) and binary (.bdf, .ros)
   - SYNTHE uses binary output (spectrum.bin)

---

## References

- **Paper:** [Larkin et al. (2022)](https://arxiv.org/abs/2210.09185)
- **Kurucz References:**
  - ATLAS: [Kurucz (2005a)](https://ui.adsabs.harvard.edu/abs/2005MSAIS...8...14K/abstract)
  - SYNTHE: [Kurucz & Avrett (1981)](https://ui.adsabs.harvard.edu/abs/1981SAOSR.391.....K/abstract)
  - DFSYNTHE: [Castelli (2005)](https://ui.adsabs.harvard.edu/abs/2005MSAIS...8...34C/abstract)
