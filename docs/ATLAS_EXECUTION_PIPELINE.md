# ATLAS Stellar Spectrum Generation Pipeline

## Overview

The ATLAS suite is a collection of Fortran binaries that generate synthetic stellar spectra from atmospheric models. When generating a spectrum from a restart file (pre-existing model), the process involves two main phases:

1. **ATLAS Phase**: Calculate the stellar atmosphere model (iterative)
2. **SYNTHE Phase**: Calculate the synthetic spectrum for that model

This document describes the execution order, input/output files, and the Fortran tape (fort.n) system used by these binaries.

---

## Part 1: ATLAS Atmosphere Calculation Phase

### Entry Point
```python
atlas.atlas(run_dir, settings, restart='auto', niter=450)
```

The ATLAS phase takes a restart file (initial temperature profile) and iteratively refines it to find an equilibrium atmospheric structure.

### Execution Sequence

#### Phase 1a: Setup (atlas_control_start.com)

**Purpose**: Create symbolic links (virtual "tapes") to required data files

```bash
cd {output_dir}
ln -s {kapparos} fort.1           # Rosseland mean opacity data
ln -s {ODF} fort.9                # Opacity Distribution Function data
ln -s {molecules} fort.2          # Molecular data
ln -s {initial_model} fort.3      # Starting model/restart file
```

**Input Files**:
- `fort.1`: Rosseland mean opacity (kappa.ros from DFSYNTHE run)
- `fort.2`: Molecular species data (molecules.dat)
- `fort.3`: Initial model atmosphere (restart.dat, generated from a restart file or gray atmosphere)
- `fort.9`: Opacity Distribution Function data (p00big{vturb}.bdf from DFSYNTHE)

#### Phase 1b: Main ATLAS Iteration (atlas_control.com)

**Binary**: `atlas9mem.exe`

**Input Format**: Control cards via stdin (heredoc)

```fortran
READ KAPPA                    ! Read Rosseland opacity (fort.1)
READ PUNCH                    ! Read initial model (fort.3)
MOLECULES {ON/OFF}            ! Enable/disable molecular formation
READ MOLECULES                ! Read molecular data (fort.2)
FREQUENCIES 337 1 337 BIG     ! Frequency grid specification
VTURB {vturb}                 ! Turbulent velocity [cm/s]
CONVECTION OVER 1.25 ...      ! Convection parameters
TITLE {title}                 ! Model title
SCALE ...                     ! Temperature scale, Teff, logg
ABUNDANCE SCALE ...           ! Metallicity and elemental abundances
{ITERATIONS ...}              ! Iteration control (groups of 15)
```

**What Happens**:
1. Reads initial model from fort.3
2. Calculates hydrostatic equilibrium for each temperature layer
3. Iteratively improves temperature structure through radiative equilibrium
4. Writes intermediate results during iterations
5. Outputs best result to fort.7 (when converged)

**Intermediate Files Created During Iterations**:
- `fort.4`: Temporary arrays (deleted after iteration)
- `fort.5`: Temporary work space (deleted after iteration)
- `fort.7`: Current best atmospheric model (updated after each iteration batch)
- `fort.10`: Temporary opacity data (deleted after iteration)

**Output Metrics** (written to stdout → output_main.out):
- Temperature profile at each layer
- Pressure structure
- Convergence errors at each iteration
- Line blanketing effects

#### Phase 1c: Cleanup (atlas_control_end.com)

**Purpose**: Extract final model and clean up temporary files

```bash
cd {output_dir}
mv fort.7 {output_2}          # Renamed to output_summary.out
rm fort.*                     # Remove all fort.* files
```

**Final ATLAS Output Files**:
- `output_main.out`: Detailed iteration history and final model (human-readable)
- `output_summary.out`: Final model in DECK6 format (input for SYNTHE)
  - Contains: Depth points (72), Temperature, Gas pressure, Electron density, continuous opacity, radiative acceleration, turbulent velocity, convective velocity, sound velocity

---

## Part 2: SYNTHE Spectral Synthesis Phase

### Entry Point
```python
atlas.synthe(run_dir, min_wl, max_wl, res=600000.0)
```

The SYNTHE phase generates the synthetic stellar spectrum using the atmospheric model from ATLAS.

### Execution Sequence

The SYNTHE run is split into multiple batches if the wavelength range is too large for the available buffer. Each batch creates a subdirectory `synthe_{batch_num}/`.

#### Phase 2a: Model Adaptation

**Purpose**: Prepare ATLAS model output for SYNTHE consumption

1. Read `output_summary.out`
2. Remove ATLAS turbulent velocity values (replace with zeros)
3. Write adapted model to `output_synthe.out` with SYNTHE-specific headers
4. Apply abundance adjustments if specified (via ATLAS-style abundance cards)

#### Phase 2b: Batch Preparation

Create directory structure:
```
synthe_{synthe_num}/
├── fort.2, fort.17, fort.11, fort.18, fort.25  (symlinks to data)
├── xnfpelsyn.out      (output from xnfpelsyn.exe)
├── synbeg.out         (output from synbeg.exe)
├── rgfalllinesnew.out (output from rgfalllinesnew.exe)
├── {molecule}_{type}.out     (outputs from rmolecasc.exe)
├── synthe.out         (output from synthe.exe)
├── spectrv.out        (output from spectrv.exe)
└── spectrum.bin       (final binary spectrum)
```

#### Phase 2c: Binary Execution Sequence

**Step 1: XNFPELSYN.EXE - Chemical Equilibrium**

```bash
ln -s {s_files}/molecules.dat fort.2
ln -s {s_files}/continua.dat fort.17
xnfpelsyn.exe < {output_synthe.out} > xnfpelsyn.out
mv fort.10 xnfpelsyn.dat
```

**Input**:
- `fort.2`: Molecular species data (molecules.dat)
- `fort.17`: Continuum opacity data (continua.dat)
- stdin: Atmospheric model from output_synthe.out

**Output**:
- `fort.10` (→ xnfpelsyn.dat): Chemical equilibrium data
  - Atomic and molecular number densities as function of depth

**Purpose**: Calculate ionization equilibrium and molecular abundance ratios using Saha equation and Guldberg-Waage law

---

**Step 2: SYNBEG.EXE - Wavelength Grid Initialization**

```bash
synbeg.exe << EOF > synbeg.out
{AIR_or_VAC}  {wlbeg}  {wlend}  {resolution}  {turbv}  {ifnlte}  {linout}  {cutoff}  {ifpred}  {nread}
EOF
```

**Input Parameters**:
- `AIR/VAC`: Wavelength scale (vacuum or air)
- `wlbeg`, `wlend`: Wavelength range (nm)
- `resolution`: Spectral resolution (λ/Δλ)
- `turbv`: Microturbulent velocity [km/s]
- `ifnlte`: Non-LTE flag (0 = LTE only)
- `linout`: Line output flag (-1 = no line output)
- `cutoff`: Line wing cutoff (Angstroms)
- `ifpred`: Prediction flag (1 = use wavelength predictions)
- `nread`: Number of read operations (0 = normal)

**Output**: 
- `fort.6` (stdout): Wavelength grid information
- Internal state set up in memory

**Purpose**: Initialize the wavelength grid and resolution parameters for spectrum calculation

**Cleanup**: `rm fort.*`

---

**Step 3: RGFALLLINESNEW.EXE - Atomic Line Data**

```bash
ln -s {linelist} fort.11
rgfalllinesnew.exe > rgfalllinesnew.out
```

**Input**:
- `fort.11`: Atomic line list (e.g., BasicATLAS.dat)
  - Format: Wavelength, species identification, line strength data, line broadening coefficients

**Output**:
- `fort.16`: Processed atomic line data in memory-efficient format
- Internal radiative transfer data

**Purpose**: Read and process atomic spectral line data

**Cleanup**: `rm fort.11`

---

**Step 4: RMOLECASC.EXE - Molecular Line Data (Multiple Runs)**

This binary is called multiple times, once for each molecular species.

```bash
ln -s {s_files}/{molecule}.asc fort.11
rmolecasc.exe > {molecule}.out
rm fort.11
```

**Molecular Species Processed** (in order):
1. chmasseron_corrected.asc → CH bands
2. mgh_exomol.asc → MgH bands
3. nh.asc → NH bands
4. ohupdate.asc → OH bands
5. sihax.asc → SiH bands
6. h2.asc → H₂ bands
7. h2xx.asc → H₂ excited states
8. hdxx.asc → HD bands
9. c2ax.asc → C₂ bands (A-X transition)
10. c2ba.asc → C₂ bands (B-A transition)
11. c2dabrookek.asc → C₂ bands (D-A transition)
12. c2ea.asc → C₂ bands (E-A transition)
13. cnaxbrookek.asc → CN bands (A-X transition)
14. cnbxbrookek.asc → CN bands (B-X transition)
15. cnxx12brooke.asc → CN bands (X-X transition)
16. coax.asc → CO bands (A-X transition)
17. coxx.asc → CO bands (X-X transition)
18. sioax.asc → SiO bands (A-X transition)
19. sioex.asc → SiO bands (E-X transition)
20. sioxx.asc → SiO bands (X-X transition)
21. tiototo.asc → TiO bands

**Input**:
- `fort.11`: Molecular band data (ASCII format)
  - Each file contains: Wavelength, band head data, line strength, broadening data

**Output**:
- `fort.16` (appended): Molecular line and band data merged with atomic data

**Purpose**: Load molecular band systems into the radiative transfer calculation

**Cleanup after each**: `rm fort.11`

---

**Step 5: RH2OFAST.EXE - H₂O Water Bands (Binary Format)**

```bash
ln -s {d_files}/h2ofastfix.bin fort.11
rh2ofast.exe > h2ofastfix.out
rm fort.11
```

**Input**:
- `fort.11`: Water vapor band data (binary format, pre-computed opacity tables)

**Output**:
- `fort.16` (appended): H₂O opacity data

**Purpose**: Add high-resolution water vapor opacity (binary format for efficiency)

---

**Step 6: SYNTHE.EXE - Line Opacity Calculation**

```bash
ln xnfpelsyn.dat fort.10
ln -s {s_files}/he1tables.dat fort.18
synthe.exe > synthe.out
```

**Input**:
- `fort.10`: Chemical equilibrium data from XNFPELSYN
- `fort.16`: All atomic and molecular line/band data (built by previous steps)
- `fort.18`: Helium-I opacity tables (he1tables.dat)
- stdin: Model atmosphere (output_synthe.out)

**Output**:
- `fort.7`: Radiative transfer arrays with computed opacities
  - Internal format binary file
- Output log in synthe.out

**Purpose**: Calculate line-by-line radiative transfer and opacity at each wavelength point

**Key Calculations**:
- Line broadening (Doppler, natural, pressure broadening)
- Opacity depth-by-depth
- Source function
- Radiative transfer through atmosphere layers

**Cleanup**: `rm xnfpelsyn.dat` and all temporary fort.* except fort.7

---

**Step 7: SPECTRV.EXE - Spectrum Calculation**

```bash
ln -s {s_files}/molecules.dat fort.2
cat << EOF > fort.25
0.0  0.0  1.0  0.0  0.0  0.0  0.0  0.0
0.
EOF
spectrv.exe < "{output_synthe.out}" > spectrv.out
```

**Input**:
- `fort.2`: Molecular data
- `fort.7`: Radiative transfer arrays with opacities
- `fort.25`: Specification file with parameters:
  - Row 1: Macroturbulent velocity, limb darkening coefficients (not used: all zeros/1.0)
  - Row 2: Radial velocity
- stdin: Model atmosphere file

**Output**:
- `fort.7` (overwritten): Binary spectrum
  - Header (418 bytes):
    - Starting wavelength (log10)
    - Number of wavelength points
    - Spectral resolution (λ/Δλ)
    - Model atmosphere metadata
  - Data (3×8 bytes per wavelength point):
    - Wavelength-integrated flux
    - Continuum flux
    - Unknown parameter
  - Format: IEEE 32-bit or 64-bit floats (machine-specific)

**Purpose**: Integrate radiative transfer results to produce emergent spectrum

**Key Output**:
- `fort.7`: Final spectrum in binary format

#### Phase 2d: Cleanup and Output Organization

```bash
mv fort.7 spectrum.bin       # Rename to final spectrum
rm fort.*                    # Remove all other fort.* files
rm xnfpelsyn.dat            # Remove chemical equilibrium data
```

---

## Final Output Files and Their Meanings

### Files Created by ATLAS Phase

| File | Type | Contents | Usage |
|------|------|----------|-------|
| `output_main.out` | Text | Detailed iteration history, convergence data, final T(τ) profile | Analysis, troubleshooting |
| `output_summary.out` | Text (DECK6) | Final atmospheric model in ATLAS format with 72 depth points | Input to SYNTHE |

### Files Created by SYNTHE Phase

| File | Type | Contents | Usage |
|------|------|----------|-------|
| `output_synthe.out` | Text (DECK6) | ATLAS model adapted for SYNTHE (turbulent velocity zeroed) | Input data file |
| `synthe_1/spectrum.bin` | Binary | Final synthetic spectrum | Data analysis |
| `synthe_1/synbeg.out` | Text | Wavelength grid information | Debugging |
| `synthe_1/rgfalllinesnew.out` | Text | Atomic line data processing log | Debugging |
| `synthe_1/chmasseron.out` | Text | CH band processing log | Debugging |
| `synthe_1/*.out` | Text | Processing logs for each molecular species | Debugging |
| `synthe_1/synthe.out` | Text | Radiative transfer calculation log | Debugging |
| `synthe_1/spectrv.out` | Text | Spectrum calculation log | Debugging |

**Multiple SYNTHE Batches**: If wavelength range is large, additional `synthe_2/`, `synthe_3/`, etc. directories are created.

---

## Binary Spectrum Format Details

**File**: `synthe_N/spectrum.bin`

**Header** (418 bytes, unformatted Fortran record):
```fortran
IMPLICIT DOUBLE PRECISION (A-H,O-Z)
DIMENSION X(20), NHEAD(10)
! Position in file
! 1-4: Record length marker (Fortran)
! 5: Starting wavelength (log10, double precision)
! 13: Number of wavelength points (integer)
! 17: Spectral resolution λ/Δλ (double precision)
! ... additional model atmosphere parameters (20 doubles, 10 ints)
! 415-418: Record length marker (Fortran)
```

**Data Records** (per wavelength point):
```fortran
! For each of n_wl points:
!   Wavelength-integrated flux (8 bytes, double)
!   Continuum flux (8 bytes, double)
!   Parameter 3 (8 bytes, double)
! Total: n_wl * 24 bytes
```

**Reading the Spectrum** (Python example from atlas.py):
```python
wl = 10^(log10(wl_start) + arange(n_wl) * log10(1 + 1/resolution)) * 10  # Convert to Å
flux = 4.0 * data * c * 1e10 / wl^2  # Convert to CGS units [erg s⁻¹ cm⁻² Å⁻¹ strad⁻¹]
```

---

## Fort File System (Fortran Tape) Reference

The Fortran tape system uses numbered fort.* files for I/O:

| Fort # | Type | Purpose | Lifecycle |
|--------|------|---------|-----------|
| fort.1 | Input | Rosseland opacity (ATLAS only) | Created at start, removed at end |
| fort.2 | Input | Molecular data (ATLAS & SYNTHE) | Symlinked repeatedly, removed after use |
| fort.3 | Input | Initial model/restart (ATLAS only) | Created at start, removed at end |
| fort.4-5 | Working | Temporary arrays (ATLAS only) | Created/destroyed each iteration |
| fort.7 | Output | Current model (ATLAS) / Final spectrum (SYNTHE) | Overwritten, moved to final filename at end |
| fort.9 | Input | ODF data (ATLAS only) | Created at start, removed at end |
| fort.10 | Working | Chemical equilibrium (SYNTHE) | Created by XNFPELSYN, read by SYNTHE |
| fort.11 | Input | Line/band data (SYNTHE) | Symlinked for each species, removed after |
| fort.16 | Working | Accumulated line/band data (SYNTHE) | Built up by multiple binaries, read by SYNTHE |
| fort.17 | Input | Continuum opacity (SYNTHE) | Symlinked, removed after XNFPELSYN |
| fort.18 | Input | He-I opacity tables (SYNTHE) | Symlinked, removed after SYNTHE |
| fort.25 | Input | Spectrum parameters (SYNTHE) | Created as text, read by SPECTRV |

**Key Insight**: Fortran 77 reads/writes unformatted (binary) records. The `ln` and `ln -s` commands create symlinks, which Fortran treats transparently as normal files. After a binary finishes, unused fort.* files are deleted via `rm fort.*` to clean the namespace for the next binary.

---

## Execution Time Estimates

| Phase | Typical Duration | Notes |
|-------|------------------|-------|
| ATLAS (450 iterations) | 10-60 minutes | Depends on temperature profile complexity |
| SYNTHE/XNFPELSYN | 1-10 seconds | Quick chemical equilibrium calculation |
| SYNTHE/SYNBEG | < 1 second | Grid initialization |
| SYNTHE/Line Loading | 1-5 minutes | Depends on number of lines and molecules |
| SYNTHE/Radiative Transfer | 5-30 minutes | Main computational step (depth × wavelength) |
| SYNTHE/SPECTRV | 1-10 minutes | Integration step |
| **Total SYNTHE per batch** | 10-50 minutes | Longer for large wavelength ranges |

---

## Error Handling and Diagnostics

**Common Issues**:

1. **ATLAS doesn't converge**: 
   - Check convergence criteria in output_main.out
   - Temperature oscillations indicate insufficient damping
   - Line blanketing may be too weak/strong

2. **SYNTHE fails on missing data**:
   - Ensure all fort.11 symlinks point to valid files
   - Check molecular data completeness
   - Verify he1tables.dat exists

3. **Spectrum has NaN values**:
   - May indicate numerical issues in radiative transfer
   - Check for very high optical depths
   - Verify abundance values are reasonable

4. **Buffer overflow in SYNTHE**:
   - Wavelength range too large for buffer size (2010001 default)
   - Reduce max resolution or split into multiple batches (automatic)

---

## References and Further Reading

- Kurucz, R. L. (1970). "SAO Special Report", No. 309
- Kurucz, R. L. (1992). "Synthe" in The Stellar Populations of Galaxies, IAU Symp. 149
- Castelli & Kurucz (2003). "New Grids of ATLAS9 Model Atmospheres"
- BasicATLAS repository documentation
