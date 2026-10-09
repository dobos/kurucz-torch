# Complete ATLAS-SYNTHE Pipeline Documentation

## Overview

This document describes the complete pipeline for generating synthetic stellar spectra using the ATLAS-SYNTHE-DFSYNTHE suite from Kurucz. The process involves three major phases executed in strict dependency order:

1. **Phase 2: DFSYNTHE** (Opacity Distribution Functions) - Must run once per abundance set
2. **Phase 1: ATLAS** (Atmospheric Model) - Depends on Phase 2 outputs
3. **Phase 3: SYNTHE** (Spectral Synthesis) - Depends on Phase 1 outputs

---

## Phase 1: Calculate Stellar Atmosphere Model (ATLAS)

This phase generates the temperature-pressure profile for the stellar atmosphere using ATLAS code.

### Prerequisites
- ODF (Opacity Distribution Functions) files from Phase 2
- Rosseland mean opacities from Phase 2

### Binary: `atlas9mem.exe`

**Input:**
- Restart file (pre-computed model or gray atmosphere)
- ODF files from Phase 2
- Rosseland mean opacities from Phase 2
- Stellar parameters (Teff, log g, vturb, abundances)

**Output:**
- `output_main.out` (detailed atmosphere structure)
- `output_synthe.out` (condensed atmosphere model - used by Phase 3)

**Python Function:** `atlas()`

**Notes:**
- Runs iteratively with convergence checking
- Phase 3 (SYNTHE) depends on this output
- Phase 2 (DFSYNTHE) can be cached and reused for different Teff/log g values

---

## Phase 2: Calculate Opacity Distribution Functions (DFSYNTHE)

This phase is executed BEFORE Phase 1. It calculates opacity data needed by ATLAS. This phase only needs to run once per set of chemical abundances, then can be reused for different Teff/log g values.

**Python Function:** `dfsynthe()`

### Step 1: Tabulate Number Densities

**Binary:** `xnfdf.exe` (runs for each of 56 standard temperatures)

**Purpose:** Tabulates atomic and molecular number densities

**Output:**
- `xnfpdf.dat`
- `xnfpdfmax.dat`

### Step 2: Calculate Opacity Distribution Functions

**Binaries (in sequence):**

1. **`dfsynthe.exe`** - Calculates opacity distribution functions (runs for each temperature)
   
2. **`dfsortp.exe`** - Sorts the opacity data (runs 5 times, once per turbulent velocity: 0, 1, 2, 4, 8 km/s)

**Output:** Multiple `dfp00t<temp>v<vturb>sortp.asc` files

### Step 3: Merge ODF Files

**Binary:** `separatedf.exe` - Merges sorted data into single files per turbulent velocity

**Output:**
- `p00big<vturb>.bdf` (opacity distribution functions for each vturb)
- `p00lit<vturb>.bdf` (light opacity distribution functions)

### Step 4: Calculate Rosseland Mean Opacities

**Binary:** `kappa9.exe` (runs in sequence, for each of 5 turbulent velocities)

**Purpose:** Computes Rosseland mean opacities for each vturb

**Output:** `kapm40k2.out` files

### Step 5: Merge Rosseland Opacities

**Binary:** `kapreadts.exe` - Merges all turbulent velocity tables

**Output:** 
- `kappa.ros` (final Rosseland mean opacity table)
- ODF directory with all `.bdf` and `.ros` files

---

## Phase 3: Generate Synthetic Spectrum (SYNTHE)

This is the core spectral synthesis pipeline. All binaries execute in strict sequence within the working directory `~/ATLAS_sun_model/synthe_1/` (or equivalent).

### Prerequisites
- `output_synthe.out` (ATLAS model atmosphere from Phase 1)
- Supporting data files (molecules.dat, continua.dat, helium tables, atomic/molecular line lists)

### Complete Execution Sequence

#### Step 1: xnfpelsyn.exe - Chemical Equilibrium

**Purpose:** Computes chemical equilibrium at each atmospheric layer

**Input Files:**
- `output_synthe.out` (ATLAS model atmosphere) - via stdin
- `fort.2` ← symlink to `molecules.dat` (molecular constants)
- `fort.17` ← symlink to `continua.dat` (continuum opacities)

**Output Files:**
- `fort.10` (binary) - chemical equilibrium data
- `xnfpelsyn.out` (text log, ~2 MB)

**File Rename:** 
- `fort.10` → `xnfpelsyn.dat` (2.9 MB)

**Command Pattern:**
```bash
ln -s /path/to/molecules.dat fort.2
ln -s /path/to/continua.dat fort.17
/path/to/xnfpelsyn.exe < output_synthe.out > xnfpelsyn.out
mv fort.10 xnfpelsyn.dat
```

---

#### Step 2: synbeg.exe - Wavelength Grid Initialization

**Purpose:** Initializes spectral synthesis computation with wavelength grid and frequency parameters

**Input Files:**
- Parameters via stdin (wavelength range, resolution, turbulent velocity)

**Output Files:**
- `fort.19` (binary, 337 KB) - wavelength/frequency grid for integration
- `fort.93` (binary, 2.8 KB) - unformatted frequency array for output
- `synbeg.out` (text log, 254 bytes)

**File Usage:**
- `fort.19` persists through Steps 3-7 (used by synthe.exe and spectrv.exe)
- `fort.93` persists through Step 7 (used by spectrv.exe)

**Command Pattern:**
```bash
cat > synbeg_input.txt << 'EOF'
100.0    2850.0    600000    0.0
EOF
/path/to/synbeg.exe < synbeg_input.txt > synbeg.out
# Produces fort.19, fort.93
```

---

#### Step 3: rgfalllinesnew.exe - Load Atomic Lines

**Purpose:** Loads and processes atomic absorption line list

**Input Files:**
- `fort.11` ← symlink to `BasicATLAS.dat` (atomic line list)

**Output Files:**
- `rgfalllinesnew.out` (text log, 54 MB for sun)
- Internal memory accumulation (opacities)

**File Handling:**
```bash
ln -s /path/to/BasicATLAS.dat fort.11
/path/to/rgfalllinesnew.exe > rgfalllinesnew.out
rm fort.11  # Clean up for next step
```

---

#### Step 4: rmolecasc.exe - Load Molecular Lines (16 Invocations)

**Purpose:** Processes molecular line opacity for each of 16 molecular species

**Molecules Processed (in order):**
1. chmasseron_corrected.asc (internal reference state)
2. mgh_exomol.asc (MgH)
3. nh.asc (NH)
4. ohupdate.asc (OH)
5. sihax.asc (SiH)
6. h2.asc (H₂)
7. h2xx.asc (H₂ excited state)
8. hdxx.asc (HD)
9. c2ax.asc (C₂ A-X)
10. c2ba.asc (C₂ B-A)
11. c2dabrookek.asc (C₂ D-A)
12. c2ea.asc (C₂ E-A)
13. cnaxbrookek.asc (CN A-X)
14. cnbxbrookek.asc (CN B-X)
15. cnxx12brooke.asc (CN X-X)
16. coax.asc / coxx.asc / sioax.asc / sioex.asc / sioxx.asc (CO and SiO variants)

**Input Files (per invocation):**
- `fort.11` ← symlink to specific molecular line file (*.asc)

**Output Files (per invocation):**
- `[molecule].out` (text log, ~322 bytes each)
- Internal memory accumulation (opacities)

**File Handling Pattern (repeated 16 times):**
```bash
# For each molecule:
ln -s /path/to/molecule_file.asc fort.11
/path/to/rmolecasc.exe > [molecule].out
rm fort.11  # Clean up
# Repeat for next molecule
```

---

#### Step 5: rh2ofast.exe - Load Water Bands

**Purpose:** Specialized high-resolution processing for water (H₂O) absorption bands

**Input Files:**
- `fort.11` ← symlink to `h2ofastfix.bin` (binary water line list)

**Output Files:**
- `h2ofastfix.out` (text log, ~322 bytes)
- Internal memory accumulation (water opacities)

**File Handling:**
```bash
ln -s /path/to/h2ofastfix.bin fort.11
/path/to/rh2ofast.exe > h2ofastfix.out
rm fort.11  # Clean up
```

---

#### Step 6: synthe.exe - Integrate Line Opacities

**Purpose:** Computes complete line opacity table by integrating all atomic and molecular contributions

**Input Files:**
- `fort.10` ← hardlink to `xnfpelsyn.dat` (chemical equilibrium from Step 1)
- `fort.18` ← symlink to `he1tables.dat` (helium ionization tables)
- `fort.2` ← symlink to `molecules.dat` (molecular constants)
- `fort.19` (wavelength grid from Step 2 - persists)
- `fort.93` (frequency array from Step 2 - persists)
- Accumulated opacity data in memory (from Steps 3-5)

**Output Files:**
- `fort.12` (binary, 324 MB) - **CRITICAL**: Complete line opacity table
- `synthe.out` (text log, variable size)

**File Usage:**
- `fort.12` persists and is REQUIRED for Step 7 (spectrv.exe)
- This is the largest intermediate file and carries all integrated atomic and molecular opacities

**Command Pattern:**
```bash
ln /path/to/xnfpelsyn.dat fort.10  # hardlink (not symlink)
ln -s /path/to/he1tables.dat fort.18
ln -s /path/to/molecules.dat fort.2
# fort.19 and fort.93 already exist from Step 2
/path/to/synthe.exe > synthe.out
# fort.12 is output and must persist
```

---

#### Step 7: spectrv.exe - Final Radiative Transfer (THE FINAL STEP)

**Purpose:** Solves radiative transfer equation to produce emergent synthetic spectrum

**Input Files:**
- `output_synthe.out` (ATLAS model atmosphere) - via stdin
- `fort.2` ← symlink to `molecules.dat` (molecular constants)
- `fort.12` ← line opacity table from Step 6 (CRITICAL - 324 MB)
- `fort.19` ← wavelength grid from Step 2 (337 KB)
- `fort.93` ← frequency array from Step 2 (2.8 KB)
- `fort.25` ← configuration file (generated inline)

**Output Files:**
- `fort.7` (binary, 465 MB) - raw spectrum output
- `spectrv.out` (text log, variable size)

**File Rename:**
- `fort.7` → `spectrum.bin` (465 MB) - **FINAL SYNTHETIC SPECTRUM**

**Configuration File (fort.25):**
```
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
```

**Command Pattern:**
```bash
ln -s /path/to/molecules.dat fort.2
cat > fort.25 << 'EOF'
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
EOF
/path/to/spectrv.exe < output_synthe.out > spectrv.out
mv fort.7 spectrum.bin
```

---

## Complete Dependency Graph

```
Phase 2: DFSYNTHE (must complete first)
    xnfdf.exe
        ↓
    dfsynthe.exe → dfsortp.exe → separatedf.exe
        ↓
    kappa9.exe → kapreadts.exe
        ↓
    ODF directory: .bdf and .ros files
    
        ↓ (required for Phase 1)
        ↓

Phase 1: ATLAS Atmosphere Model
    atlas9mem.exe (uses ODFs from Phase 2)
        ↓
    output_synthe.out (ATLAS model atmosphere)
    
        ↓ (required for Phase 3)
        ↓

Phase 3: SYNTHE Spectral Synthesis (7-step sequence)
    output_synthe.out (from Phase 1)
        ↓
    Step 1: xnfpelsyn.exe
        ├─ INPUT: output_synthe.out, fort.2, fort.17
        ├─ OUTPUT: fort.10 → xnfpelsyn.dat
        └─ xnfpelsyn.out
        ↓
    Step 2: synbeg.exe
        ├─ INPUT: parameters (stdin)
        ├─ OUTPUT: fort.19, fort.93
        └─ synbeg.out
        ↓
    Step 3: rgfalllinesnew.exe
        ├─ INPUT: fort.11 ← BasicATLAS.dat
        ├─ OUTPUT: rgfalllinesnew.out
        └─ Accumulate atomic line opacities
        ↓
    Step 4: rmolecasc.exe (16 invocations)
        ├─ INPUT: fort.11 ← [molecule].asc (each iteration)
        ├─ OUTPUT: [molecule].out (per iteration)
        └─ Accumulate molecular line opacities
        ↓
    Step 5: rh2ofast.exe
        ├─ INPUT: fort.11 ← h2ofastfix.bin
        ├─ OUTPUT: h2ofastfix.out
        └─ Accumulate water line opacities
        ↓
    Step 6: synthe.exe
        ├─ INPUT: fort.10, fort.18, fort.2, fort.19, fort.93
        ├─ INPUT: Accumulated opacities (memory)
        ├─ OUTPUT: fort.12 (324 MB line opacity table) ← CRITICAL
        └─ synthe.out
        ↓
    Step 7: spectrv.exe ← THE FINAL STEP
        ├─ INPUT: output_synthe.out, fort.2, fort.12, fort.19, fort.93, fort.25
        ├─ OUTPUT: fort.7 → spectrum.bin (465 MB FINAL SPECTRUM)
        └─ spectrv.out
```

---

## Fortran Unit (Fort.N) System Explained

FORTRAN uses "unit numbers" for I/O operations. In the shell, these map to files named `fort.N`:

When a Fortran program does:
```fortran
OPEN(UNIT=12, FILE='opacity.dat', ...)
WRITE(12, ...) data
```

The shell creates/uses `fort.12` as the physical file.

**Common shell patterns for Fortran I/O control:**

| Pattern | Meaning |
|---------|---------|
| `ln -s input_file fort.11` | Create symbolic link (read-only) |
| `ln input_file fort.10` | Create hardlink (read-write) |
| `cat > fort.25 << EOF ... EOF` | Generate text file inline |
| `exe > stdout.log` | Capture standard output (separate from fort files) |
| `rm fort.11` | Clean up after use |

---

## Complete Fort Unit Mapping

### Input Symlinks (Created before execution)

| Fort # | Executable(s) | Input File | Purpose |
|--------|---------------|-----------|---------|
| fort.2 | xnfpelsyn, synthe, spectrv | molecules.dat | Molecular constants reference |
| fort.17 | xnfpelsyn | continua.dat | Continuum opacity data |
| fort.18 | synthe | he1tables.dat | Helium ionization tables |

### Files Generated During Phase 3

| Fort # | Step | Output File | Purpose | Size (sun_model) | Persistence |
|--------|------|------------|---------|------------------|-------------|
| fort.10 | 1 | xnfpelsyn.dat | Chemical equilibrium | 2.9 MB | Used in Step 6 |
| fort.11 | 3-5 | (symlink reuse) | Line list input | varies | Removed after each step |
| fort.19 | 2 | fort.19 | Wavelength grid | 337 KB | Persists to Step 7 |
| fort.93 | 2 | fort.93 | Frequency array | 2.8 KB | Persists to Step 7 |
| fort.12 | 6 | fort.12 | Line opacity table | 324 MB | **REQUIRED for Step 7** |
| fort.25 | 7 | fort.25 | Configuration | ~50 B | Created inline for Step 7 |
| fort.7 | 7 | spectrum.bin | Final spectrum | 465 MB | **FINAL OUTPUT** |

### Text Log Files (Diagnostic)

| File | Step | Purpose |
|------|------|---------|
| xnfpelsyn.out | 1 | Chemical equilibrium results |
| synbeg.out | 2 | Wavelength grid parameters |
| rgfalllinesnew.out | 3 | Loaded atomic line data (54 MB) |
| [molecule].out | 4 | Molecular data load confirmation (322 B each) |
| h2ofastfix.out | 5 | Water line data load confirmation |
| synthe.out | 6 | Line opacity computation results |
| spectrv.out | 7 | Final spectrum synthesis results |

---

## Data Flow Through the Pipeline

```
output_synthe.out (ATLAS model, 9.4 MB)
    |
    v
Step 1: xnfpelsyn.exe ──────> xnfpelsyn.dat (2.9 MB)
    |                              |
    v                              v
Step 2: synbeg.exe ───────────> fort.19 (337 KB)
    |                           fort.93 (2.8 KB)
    v                              |
Step 3: rgfalllinesnew.exe ────────> [Atomic lines accumulated in memory]
    |                                     |
    v                                     v
Step 4: rmolecasc.exe (16×) ───────> [Molecular lines accumulated in memory]
    |                                     |
    v                                     v
Step 5: rh2ofast.exe ───────────────> [Water lines accumulated in memory]
    |                                     |
    v                                     v
Step 6: synthe.exe ─────────────────> fort.12 (324 MB line opacity table)
    [Fort.12 carries ALL integrated atomic and molecular opacities]
    |
    | (fort.12 required here)
    v
Step 7: spectrv.exe
    + fort.19 (wavelengths)
    + fort.93 (frequencies)
    + fort.25 (config)
    + output_synthe.out (atmosphere)
    |
    v
spectrum.bin (465 MB) ──> FINAL SYNTHETIC SPECTRUM
```

---

## Running spectrv.exe Standalone

If you have an existing SYNTHE output directory and want to rerun just `spectrv.exe` (e.g., with different parameters):

### Required Pre-existing Files

These MUST already exist from previous pipeline runs:

1. **`fort.12`** (324 MB) - Line opacity table generated by synthe.exe
2. **`fort.19`** (337 KB) - Wavelength grid generated by synbeg.exe
3. **`fort.93`** (2.8 KB) - Frequency array generated by synbeg.exe
4. **`output_synthe.out`** (9 MB) - ATLAS model atmosphere

### Setup and Execution

```bash
cd ~/ATLAS_sun_model/synthe_1/

# Verify required files exist
ls -lh fort.12 fort.19 fort.93 output_synthe.out

# Create symlink for molecules.dat
ln -s /home/dobos/project/BasicATLAS/data/synthe_files/molecules.dat fort.2

# Create configuration file
cat > fort.25 << 'FORT_CONFIG'
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
FORT_CONFIG

# Run spectrv
/home/dobos/project/BasicATLAS/bin/spectrv.exe < output_synthe.out > spectrv.out

# Check output
ls -lh fort.7 spectrum.bin  # Should be ~465 MB

# Rename output
mv fort.7 spectrum.bin

# Optional cleanup
rm fort.* 2>/dev/null
```

---

## File Size Summary (for sun_model example)

| File | Size | Created By | Purpose |
|------|------|-----------|---------|
| output_synthe.out | 9.4 MB | Python wrapper (Phase 1) | Input: ATLAS model |
| xnfpelsyn.dat | 2.9 MB | Step 1: xnfpelsyn.exe | Chemical equilibrium |
| xnfpelsyn.out | 2.0 MB | Step 1: xnfpelsyn.exe | Log/diagnostics |
| synbeg.out | 254 B | Step 2: synbeg.exe | Log/diagnostics |
| fort.19 | 337 KB | Step 2: synbeg.exe | Wavelength grid |
| fort.93 | 2.8 KB | Step 2: synbeg.exe | Frequency array |
| rgfalllinesnew.out | 54 MB | Step 3: rgfalllinesnew.exe | Atomic lines log |
| [16 molecule].out | 322 B each | Step 4: rmolecasc.exe | Molecular data logs |
| h2ofastfix.out | 322 B | Step 5: rh2ofast.exe | Water line log |
| fort.12 | 324 MB | Step 6: synthe.exe | Line opacity table (CRITICAL) |
| synthe.out | variable | Step 6: synthe.exe | Log/diagnostics |
| spectrum.bin | 465 MB | Step 7: spectrv.exe | **FINAL OUTPUT** |
| spectrv.out | variable | Step 7: spectrv.exe | Log/diagnostics |

**Total intermediate disk usage: ~490 MB** (excluding diagnostic logs)

---

## Key Points Summary

1. **Execution Order is Critical:**
   - Phase 2 (DFSYNTHE) → Phase 1 (ATLAS) → Phase 3 (SYNTHE)
   - Within Phase 3, all 7 steps execute strictly sequentially
   - Cannot skip or reorder steps within Phase 3

2. **Fort.12 is the Pipeline Nexus:**
   - Created by synthe.exe (Step 6) with all accumulated opacities
   - REQUIRED by spectrv.exe (Step 7)
   - Largest intermediate file at 324 MB
   - Must persist between steps

3. **File Renaming Tracking:**
   - `fort.10` → `xnfpelsyn.dat` (Step 1 output)
   - `fort.7` → `spectrum.bin` (Step 7 output, FINAL)
   - All other fort.N files kept as-is

4. **Fort.11 "Swap" Pattern:**
   - Multiple executables need different line lists via fort.11
   - Pattern: `ln -s file fort.11` → run → `rm fort.11` → repeat
   - Ensures each executable reads correct input without conflicts

5. **Reusability:**
   - Phase 2 outputs (ODFs) can be cached and reused
   - Phase 1 ATLAS model can be reused with different Phase 3 parameters
   - Phase 3 can be run multiple times on same ATLAS model

6. **Running spectrv.exe Standalone:**
   - Requires fort.12, fort.19, fort.93, and output_synthe.out to already exist
   - Fastest way to regenerate spectrum.bin with different parameters
   - Skip Steps 1-6 if only parameters changed (not atmospheric model)

---

## Typical Usage Pattern

```python
from atlas import atlas, synthe, Settings

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

## References

- **Paper:** [Larkin et al. (2022)](https://arxiv.org/abs/2210.09185)
- **Kurucz ATLAS:** [Kurucz (2005a)](https://ui.adsabs.harvard.edu/abs/2005MSAIS...8...14K/abstract)
- **SYNTHE:** [Kurucz & Avrett (1981)](https://ui.adsabs.harvard.edu/abs/1981SAOSR.391.....K/abstract)
- **DFSYNTHE:** [Castelli (2005)](https://ui.adsabs.harvard.edu/abs/2005MSAIS...8...34C/abstract)
