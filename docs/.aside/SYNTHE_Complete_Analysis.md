# BasicATLAS/SYNTHE Pipeline: Complete Analysis Summary

## Document Overview

This directory contains three detailed analysis documents about the BasicATLAS code structure and how the SYNTHE spectrum synthesis pipeline works:

1. **BasicATLAS.md** - High-level overview of the three phases
2. **SYNTHE_Fort_Unit_Mapping.md** - Detailed Fortran I/O unit mapping
3. **SYNTHE_Executable_IO_Reference.md** - Quick reference for running each executable

---

## Quick Summary: Running spectrv.exe on sun_model Output

The user asked: "Run spectrv.exe first (starting from the end) on the output from the notebook sun_model."

### Answer

**spectrv.exe** is the FINAL executable that produces the synthetic spectrum. It requires:

**Pre-requisite files (from earlier steps):**
- `fort.12` (324 MB) - Complete line opacity table from synthe.exe
- `fort.19` (337 KB) - Wavelength grid from synbeg.exe
- `fort.93` (2.8 KB) - Frequency array from synbeg.exe
- `output_synthe.out` - The ATLAS model atmosphere

**To run spectrv.exe:**

```bash
cd ~/ATLAS_sun_model/synthe_1/

# Setup symlinks
ln -s /home/dobos/project/BasicATLAS/data/synthe_files/molecules.dat fort.2
cat > fort.25 << 'EOF'
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
EOF

# Run spectrv (if not already done)
/home/dobos/project/BasicATLAS/bin/spectrv.exe < output_synthe.out > spectrv.out

# Output
mv fort.7 spectrum.bin  # Contains the synthetic spectrum
```

---

## What Each Executable Does (in order)

| # | Executable | Input | Output | Size (sun) | Purpose |
|---|-----------|-------|--------|-----------|---------|
| 1 | xnfpelsyn.exe | output_synthe.out, molecules.dat, continua.dat | xnfpelsyn.dat | 2.9 MB | Chemical equilibrium |
| 2 | synbeg.exe | Wavelength parameters | fort.19, fort.93 | 340 KB | Wavelength grid setup |
| 3 | rgfalllinesnew.exe | BasicATLAS.dat | rgfalllinesnew.out | 54 MB | Load atomic lines |
| 4 | rmolecasc.exe × 16 | Molecular line files | [molecule].out | 322 B ea. | Load 16 molecular species |
| 5 | rh2ofast.exe | h2ofastfix.bin | h2ofastfix.out | 322 B | Load water bands |
| 6 | synthe.exe | xnfpelsyn.dat, He tables, all line data | fort.12 | 324 MB | Integrate line opacities |
| 7 | **spectrv.exe** | **fort.12, fort.19, fort.93, output_synthe.out** | **spectrum.bin** | **465 MB** | **FINAL: Radiative transfer** |

---

## File System: The Fort Unit Concept

FORTRAN uses "unit numbers" for I/O. The SYNTHE codes use:

- `fort.2` - molecules.dat (molecular constants)
- `fort.7` - Final spectrum output
- `fort.10` - Chemical equilibrium data (xnfpelsyn.dat)
- `fort.11` - Line list input (reused, symlinked per executable)
- `fort.12` - Line opacity table (324 MB)
- `fort.17` - continua.dat (continuum opacities)
- `fort.18` - he1tables.dat (helium ionization)
- `fort.19` - Wavelength/frequency grid (337 KB)
- `fort.25` - Configuration parameters
- `fort.93` - Frequency array for output (2.8 KB)

### The Fort.11 "Swap" Pattern

Multiple executables need different line lists. Since each reads from `fort.11`, the script:

```bash
ln -s specific_molecule.asc fort.11
rmolecasc.exe
rm fort.11
```

This is repeated 16 times with different molecule files.

---

## Key Discovery: Fort.12 is Critical

**fort.12** (324 MB) is the **line opacity table** that carries all the accumulated atomic and molecular opacity information through the pipeline:

```
xnfpelsyn.exe        Creates: chemical equilibrium data
    |
rgfalllinesnew.exe   Loads: atomic lines → accumulates in memory
    |
rmolecasc.exe (×16)  Loads: molecular lines → accumulates in memory
    |
rh2ofast.exe         Loads: water lines → accumulates in memory
    |
synthe.exe           Integrates ALL opacities → writes fort.12 (324 MB)
    |
spectrv.exe          Reads fort.12 → solves radiative transfer → spectrum.bin
```

Without `fort.12`, spectrv.exe cannot run. It contains the complete opacity cross-sections for all wavelengths and all species.

---

## Files in the sun_model/synthe_1 Directory

```
Directory: ~/ATLAS_sun_model/synthe_1/

INPUTS (symlinks):
  fort.2  →  molecules.dat (7.5 KB)
  fort.11 →  tiototo.asc (2.5 KB) [final state; changes during execution]
  
BINARY FILES (fort.* = Fortran units):
  fort.19        wavelength grid from synbeg (337 KB)
  fort.93        frequency array from synbeg (2.8 KB)
  fort.12        line opacity table from synthe (324 MB) - CRITICAL
  
LARGE OUTPUT FILE:
  xnfpelsyn.dat  chemical equilibrium (2.9 MB)
  
TEXT LOGS:
  synbeg.out              4 lines - wavelength grid info
  xnfpelsyn.out           2.0 MB - chemical species abundances
  rgfalllinesnew.out      54 MB - loaded atomic lines
  [16 molecule].out       322 B each - molecular processing logs
  h2ofastfix.out          322 B - water line log
  synthe.out              variable - line opacity computation
  spectrv.out             variable - spectrum computation (if run)
  
FINAL OUTPUT:
  spectrum.bin            synthetic spectrum (465 MB) - if spectrv.exe was run
  
CONFIGURATION:
  fort.93                 binary frequency array (2.8 KB)
  fort.25                 configuration file (if created for spectrv)
```

---

## Data Flow Diagram

```
output_synthe.out (ATLAS model, 9.4 MB)
    |
    v
xnfpelsyn.exe ─────> xnfpelsyn.dat (2.9 MB)
                         |
synbeg.exe ─────────────>| fort.19, fort.93
                         |
rgfalllinesnew.exe ─────>| atomic lines accumulated
                         |
rmolecasc.exe (16x) ────>| molecular lines accumulated
                         |
rh2ofast.exe ───────────>| water lines accumulated
                         |
synthe.exe ─────────────>| fort.12 (324 MB)
                         |
                    [Fort.12 carries ALL opacities]
                         |
spectrv.exe <───────────<| 
    + fort.19 (wavelengths)
    + fort.93 (frequencies)
    + fort.25 (config)
    + output_synthe.out (atmosphere)
    |
    v
spectrum.bin (465 MB) ─> FINAL SYNTHETIC SPECTRUM
```

---

## Executable-to-File Matrix

| Executable | Reads | Writes | Purpose |
|-----------|-------|--------|---------|
| xnfpelsyn | output_synthe.out, molecules.dat, continua.dat | xnfpelsyn.dat | Abundance structure |
| synbeg | stdin (parameters) | fort.19, fort.93 | Wavelength grid |
| rgfalllinesnew | BasicATLAS.dat | (internal state) | Load atomic lines |
| rmolecasc | molecule_*.asc | (internal state) | Load molecular lines |
| rh2ofast | h2ofastfix.bin | (internal state) | Load water bands |
| synthe | xnfpelsyn.dat, he1tables.dat, [all line data] | fort.12 | Compute opacities |
| spectrv | fort.12, fort.19, fort.93, output_synthe.out | spectrum.bin | Solve transfer equation |

---

## Running the Full Pipeline vs. Running spectrv Alone

### Full Pipeline (via Python)
```python
from atlas import atlas, synthe, Settings
settings = Settings()
atlas('sun_model', settings=settings)  # Phase 1: ATLAS
synthe('sun_model', min_wl=100, max_wl=2850)  # Phase 3: SYNTHE (includes all 7 steps)
```

### Just spectrv.exe (assuming synthe steps already ran)
```bash
cd sun_model/synthe_1/
/path/to/spectrv.exe < output_synthe.out > spectrv.out
mv fort.7 spectrum.bin
```

The second approach is faster if fort.12 already exists (skip synthe.exe).

---

## Files Generated by Each Executable (Detailed)

### xnfpelsyn.exe
**Creates:**
- `fort.10` (binary) → moved to `xnfpelsyn.dat`
- `xnfpelsyn.out` (text log)

**Input read from:**
- stdin: output_synthe.out (ATLAS model)

**File dependencies:**
- fort.2 (molecules.dat)
- fort.17 (continua.dat)

### synbeg.exe
**Creates:**
- `fort.19` (binary, 337 KB) - Wavelength grid with frequency points
- `fort.93` (binary, 2.8 KB) - Frequency array for output
- `synbeg.out` (text log)

**Input read from:**
- stdin: wavelength parameters

### rgfalllinesnew.exe
**Creates:**
- `rgfalllinesnew.out` (54 MB for sun - text log with all loaded lines)
- Internal state (opacities in memory)

**File dependencies:**
- fort.11 ← atomic line list (BasicATLAS.dat)

### rmolecasc.exe (runs 16 times)
**Creates:**
- `[molecule].out` (322 bytes each) - Text log
- Internal state (opacities in memory, accumulated)

**File dependencies:**
- fort.11 ← different molecular line file each time

### rh2ofast.exe
**Creates:**
- `h2ofastfix.out` (text log)
- Internal state (water opacities in memory)

**File dependencies:**
- fort.11 ← h2ofastfix.bin (water line list)

### synthe.exe
**Creates:**
- `fort.12` (binary, 324 MB) - Complete integrated line opacity table
- `synthe.out` (text log)

**File dependencies:**
- fort.10 ← xnfpelsyn.dat (chemical equilibrium)
- fort.18 ← he1tables.dat (helium ionization)
- fort.2 ← molecules.dat
- fort.19 (wavelength grid from synbeg)
- fort.93 (frequency array from synbeg)
- All accumulated line opacity data in memory

### spectrv.exe
**Creates:**
- `fort.7` (binary, 465 MB) → renamed to `spectrum.bin`
- `spectrv.out` (text log)

**File dependencies:**
- fort.2 ← molecules.dat
- fort.12 ← line opacity table from synthe (CRITICAL)
- fort.19 ← wavelength grid from synbeg
- fort.93 ← frequency array from synbeg
- fort.25 ← configuration (generated inline)
- stdin: output_synthe.out (ATLAS model atmosphere)

---

## Conclusion

The SYNTHE pipeline is a sophisticated chain of Fortran programs that:

1. **xnfpelsyn** - Computes what elements exist at each layer
2. **synbeg** - Sets up the wavelength grid
3. **rgfalllinesnew** - Loads atomic absorption lines
4. **rmolecasc (16x)** - Loads molecular species (C2, CN, CO, H2, H2O, OH, MgH, NH, SiH, SiO, TiO)
5. **rh2ofast** - Specialized water band processing
6. **synthe** - Integrates all line opacities into a complete opacity table (fort.12)
7. **spectrv** - Uses fort.12 to solve the radiative transfer equation and produce the final synthetic spectrum

The **fort.N files** are Fortran I/O units that carry data between executables. The key files are:
- `fort.12` - 324 MB opacity table (the "nerve center")
- `fort.19` - wavelength grid
- `xnfpelsyn.dat` - chemical abundances

To run spectrv.exe standalone on existing output, ensure these three files exist, then invoke spectrv.exe with the ATLAS model as stdin.
