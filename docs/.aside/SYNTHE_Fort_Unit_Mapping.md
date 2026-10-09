# SYNTHE Fort Unit Mapping & File Generation

## Overview of Fort Units and File Mapping

FORTRAN's "fort.N" files are virtual I/O tapes that correspond to Fortran unit numbers. The SYNTHE pipeline uses these extensively. This document maps which executable creates/reads which files.

## Complete Fort Unit Mapping

### Input Symlinks (Created by `.com` script, read by executables)

| Fort # | Executable(s) | Input File | Purpose |
|--------|---------------|-----------|---------|
| fort.2 | xnfpelsyn, spectrv | molecules.dat | Molecular constants reference |
| fort.10 | xnfpelsyn | xnfpelsyn.dat (output) | Chemical equilibrium data (passed between executables) |
| fort.11 | rgfalllinesnew, rmolecasc (×16), rh2ofast | Line lists (*.asc, *.bin) | Atomic/molecular absorption line lists |
| fort.17 | xnfpelsyn | continua.dat | Continuum opacity data |
| fort.18 | synthe | he1tables.dat | Helium ionization tables |
| fort.25 | spectrv | Generated inline (fort.25) | Configuration parameters for spectral synthesis |

### Output Files (Created by executables, read by subsequent steps)

| Fort # | Created By | Output Name | Purpose | Size (sun_model) |
|--------|-----------|------------|---------|------------------|
| fort.7 | spectrv | spectrum.bin | Final synthetic spectrum (wavelength, flux) | 465 MB |
| fort.10 | xnfpelsyn | xnfpelsyn.dat | Chemical equilibrium for all atmospheric layers | 2.9 MB |
| fort.12 | synthe | fort.12 | Line opacity table (binary) | 324 MB |
| fort.14 | ? | fort.14 | Empty (0 bytes) | 0 |
| fort.19 | synbeg | fort.19 | Wavelength grid and configuration (binary) | 337 KB |
| fort.20 | synthe/spectrv | fort.20 | Empty (0 bytes) | 0 |
| fort.93 | synbeg | fort.93 | Binary wavelength/frequency array (unformatted) | 2.8 KB |

### Text Output Logs (Diagnostic files)

| File | Created By | Purpose |
|------|-----------|---------|
| synbeg.out | synbeg | Wavelength grid parameters |
| xnfpelsyn.out | xnfpelsyn | Chemical equilibrium results (human-readable) |
| rgfalllinesnew.out | rgfalllinesnew | Loaded atomic line data (54 MB for sun) |
| [molecule].out | rmolecasc (×16) | Molecular data loads (each ~322 bytes) |
| h2ofastfix.out | rh2ofast | Water line data load confirmation |
| synthe.out | synthe | Line opacity computation results |
| spectrv.out | spectrv | Final spectrum synthesis results |

---

## Executable Execution Chain & File Dependencies

### Step 1: xnfpelsyn.exe
**Input:**
- output_synthe.out (ATLAS model atmosphere from Phase 1)
- fort.2 ← molecules.dat (symlink)
- fort.17 ← continua.dat (symlink)

**Output:**
- fort.10 (binary) → moved to xnfpelsyn.dat
- xnfpelsyn.out (text log)

**Purpose:** Computes chemical equilibrium at each layer of the atmosphere

---

### Step 2: synbeg.exe
**Input:**
- Parameters via stdin: wavelength range, resolution, turbulent velocity, etc.

**Output:**
- fort.19 (binary) - Wavelength grid and frequency array
- fort.93 (binary) - Unformatted frequency array
- synbeg.out (text log)

**Purpose:** Initializes wavelength grid and spectral synthesis parameters

---

### Step 3: rgfalllinesnew.exe
**Input:**
- fort.11 ← BasicATLAS.dat (atomic line list) (symlink)

**Output:**
- rgfalllinesnew.out (text log, 54 MB) - Loaded lines and oscillator strengths

**Purpose:** Loads and processes atomic absorption line list

---

### Step 4: rmolecasc.exe (runs 16 times for different molecules)
**Input:**
- fort.11 ← Various molecular line lists (*.asc files) (symlink)
- For each run: different .asc file symlinked to fort.11

**Output:**
- [molecule].out (text log, ~322 bytes) - Confirmation of processed molecules

**Molecules processed:**
1. chmasseron_corrected.asc (internal reference state)
2. mgh_exomol.asc (MgH)
3. nh.asc (NH)
4. ohupdate.asc (OH)
5. sihax.asc (SiH)
6. h2.asc (H2)
7. h2xx.asc (H2 excited state)
8. hdxx.asc (HD)
9. c2ax.asc (C2 A-X)
10. c2ba.asc (C2 B-A)
11. c2dabrookek.asc (C2 D-A)
12. c2ea.asc (C2 E-A)
13. cnaxbrookek.asc (CN A-X)
14. cnbxbrookek.asc (CN B-X)
15. cnxx12brooke.asc (CN X-X)
16. coax.asc, coxx.asc, sioax.asc, sioex.asc, sioxx.asc (CO, SiO variants)

**Purpose:** Process molecular line opacity for each species

---

### Step 5: rh2ofast.exe
**Input:**
- fort.11 ← h2ofastfix.bin (water line list, binary) (symlink)

**Output:**
- h2ofastfix.out (text log, ~322 bytes)

**Purpose:** Specialized processor for high-resolution water (H2O) absorption bands

---

### Step 6: synthe.exe
**Input:**
- fort.10 ← xnfpelsyn.dat (chemical equilibrium from Step 1) (hardlink)
- fort.18 ← he1tables.dat (helium ionization tables) (symlink)
- fort.2 ← molecules.dat (symlink)
- All line opacity data from previous steps (fort.11, fort.19, fort.93)

**Output:**
- fort.12 (binary, 324 MB) - Complete line opacity table
- synthe.out (text log)

**Purpose:** Computes line opacities integrating all atomic/molecular contributions

---

### Step 7: spectrv.exe (THE FINAL STEP)
**Input:**
- output_synthe.out (ATLAS model atmosphere)
- fort.2 ← molecules.dat (symlink)
- fort.12 ← line opacities from synthe.exe
- fort.19 ← wavelength grid from synbeg.exe
- fort.93 ← frequency array from synbeg.exe
- fort.25 ← generated inline (configuration parameters)

**Output:**
- fort.7 (binary, 465 MB) → moved to spectrum.bin
- spectrv.out (text log)

**Purpose:** Final integration of radiative transfer equation to produce emergent spectrum

---

## Key Fort File Roles

### Binary Data Files (Unformatted Fortran Records)

**fort.19** (337 KB):
- Created by: synbeg.exe
- Used by: synthe.exe, spectrv.exe
- Contains: Wavelength grid, frequency points, integration weights
- Format: Unformatted binary (Fortran record structure)

**fort.93** (2.8 KB):
- Created by: synbeg.exe
- Used by: spectrv.exe
- Contains: Frequency array for final spectrum output
- Format: Unformatted binary

**fort.12** (324 MB):
- Created by: synthe.exe
- Used by: spectrv.exe
- Contains: Complete line opacity table for all wavelengths
- Format: Unformatted binary (Fortran record structure)

**fort.7** (465 MB) → spectrum.bin:
- Created by: spectrv.exe
- This is THE FINAL OUTPUT containing wavelength and flux

**xnfpelsyn.dat** (2.9 MB):
- Created by: xnfpelsyn.exe (as fort.10)
- Used by: synthe.exe (as fort.10 via hardlink)
- Contains: Chemical equilibrium abundances for each atmospheric layer
- Format: Likely binary with layer-by-layer data

---

## Processing Flow Diagram

```
INPUT: output_synthe.out (ATLAS model from Phase 1)
    DOWNWARD_ARROW
[xnfpelsyn.exe] 
    INPUT: output_synthe.out, molecules.dat, continua.dat
    OUTPUT: fort.10 -> xnfpelsyn.dat
    PURPOSE: Chemical equilibrium
    
[synbeg.exe]
    INPUT: Wavelength parameters (100-2850 nm, R=600000)
    OUTPUT: fort.19, fort.93
    PURPOSE: Wavelength grid initialization
    
[rgfalllinesnew.exe]
    INPUT: fort.11 <- atomic line list
    OUTPUT: fort.11 modified internally
    PURPOSE: Load atomic lines
    
[rmolecasc.exe x 16]
    INPUT: fort.11 <- molecular line lists (one per call)
    OUTPUT: Molecular opacities accumulated
    PURPOSE: Load molecular species (C2, CN, CO, SiO, TiO, MgH, NH, OH, etc.)
    
[rh2ofast.exe]
    INPUT: fort.11 <- h2ofastfix.bin
    OUTPUT: H2O opacities accumulated
    PURPOSE: Specialized water bands
    
[synthe.exe]
    INPUT: fort.10 (xnfpelsyn.dat), fort.18 (He tables), all accumulated opacities
    OUTPUT: fort.12 (complete line opacity table, 324 MB)
    PURPOSE: Integrate all opacities
    
[spectrv.exe] <- THE FINAL STEP
    INPUT: fort.2 (molecules), fort.12 (opacities), fort.19 (wavelengths), 
           fort.93 (frequencies), fort.25 (config)
    OUTPUT: fort.7 -> spectrum.bin (465 MB)
    PURPOSE: Solve radiative transfer -> emergent spectrum
    
OUTPUT: spectrum.bin (final synthetic spectrum)
```

---

## Special Notes

1. **Fort.10 (xnfpelsyn.dat)**: This file uses `ln xnfpelsyn.dat fort.10` (hardlink, not symlink) because it needs to be writable by synthe.exe but was created by xnfpelsyn.exe.

2. **Fort.11**: This is the "swap" fort number. Each executable that needs a line list (rgfalllinesnew, rmolecasc, rh2ofast) symlinks its input file to fort.11, runs, then deletes the symlink before the next executable runs.

3. **Fort.12 & Fort.19**: These are large binary files that persist through the entire SYNTHE pipeline, carrying accumulated opacity and wavelength data.

4. **Text output logs** (.out files): These are diagnostic/progress files that don't affect the computation, just provide information about what was processed.

5. **Fort.2 (molecules.dat)**: Symlinked multiple times (xnfpelsyn, spectrv) because multiple executables need it.

6. **Cleanup**: At the end, all fort.* files are deleted except fort.7, which is renamed to spectrum.bin. The xnfpelsyn.dat is also deleted.

---

## To Run spectrv.exe Directly

If you want to run spectrv.exe starting from existing SYNTHE output, you need:

```bash
cd synthe_1/

# Prepare required symlinks
ln -s /path/to/molecules.dat fort.2
ln -s /path/to/he1tables.dat fort.18

# Create configuration
cat > fort.25 << FORT_CONFIG
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
FORT_CONFIG

# Pre-existing files from synbeg and synthe (REQUIRED)
# fort.12 (from synthe.exe) - line opacity table (324 MB)
# fort.19 (from synbeg.exe) - wavelength grid (337 KB)
# fort.93 (from synbeg.exe) - frequency array (2.8 KB)
# output_synthe.out - ATLAS model (passed via stdin)

# Run spectrv
/path/to/spectrv.exe < /path/to/output_synthe.out > spectrv.out

# Output: fort.7 (rename to spectrum.bin)
mv fort.7 spectrum.bin
```

The critical files that spectrv.exe **requires** from previous steps are:
- **fort.12**: Line opacity table (324 MB) - generated by synthe.exe
- **fort.19**: Wavelength grid (337 KB) - generated by synbeg.exe  
- **fort.93**: Frequency array (2.8 KB) - generated by synbeg.exe

If any of these are missing, spectrv.exe will likely fail or produce incorrect results.
