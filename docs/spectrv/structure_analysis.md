# SPECTRV Fortran Source Code Analysis

## Overview

**SPECTRV** is the final stage of the ATLAS/SYNTHE spectral synthesis pipeline. It computes the emergent stellar spectrum by integrating the radiative transfer equations through the stellar atmosphere.

**Source File**: `/home/dobos/project/BasicATLAS/src/spectrv.patched.for`  
**Language**: Fortran 77 with some Fortran 90 extensions  
**Lines of Code**: 504 lines total  
**Program Units**: 1 PROGRAM + 3 SUBROUTINE stubs

---

## Program Structure

### Main Program Unit

#### `PROGRAM SPECTRV` (lines 1-495)

The main program performs the following high-level operations:

```
SPECTRV
├── Read fort.25 input parameters (wavelength range, resolution, etc.)
├── CALL READIN(20)          [Read input model atmosphere from stdin]
├── Read fort.10 (radiative transfer data)
│   ├── Edge frequencies and wavelengths (FRQEDG, WLEDGE)
│   ├── Continuum frequency grid (CONFRQ)
│   └── Depth-dependent opacity data (CONTABS, CONTSCAT)
│
├── Load optional mask file (mask.bin) for skipping wavelengths
│
├── Main wavelength loop (NU = NULO to NUHI)
│   ├── For each wavelength:
│   │   ├── Interpolate continuum opacity (CONTABS, CONTSCAT)
│   │   ├── Calculate frequency and Planck function
│   │   ├── CALL JOSH(IFSCAT, IFSURF)  [Radiative transfer integration]
│   │   ├── Read line opacity data from fort.9 (ASYNTH)
│   │   ├── CALL JOSH(1, IFSURF)        [Final radiative transfer]
│   │   ├── Output spectrum point to fort.7
│   │   └── Process masking if enabled
│   │
│   └── (Loop ~2 million times for high-resolution spectra)
│
├── Line processing loop (ILINE = 1 to NLINES)
│   ├── Read line data from fort.9
│   ├── Calculate line opacity
│   ├── CALL JOSH(1, IFSURF)             [Line radiative transfer]
│   ├── Integrate line profile
│   └── Write line results to fort.7
│
├── Additional line processing loop (ILINE = 1 to N10)
│   ├── Read pre-computed line data from fort.20
│   ├── CALL LINCEN                      [Line center calculation]
│   ├── CALL CORINT  [if IFCORO.EQ.1]    [Corona integration]
│   └── Write results to fort.7
│
└── CALL EXIT
```

---

## Subroutines Defined in SPECTRV.FOR

### 1. `SUBROUTINE LINCEN` (lines 496-498)

**Status**: Empty stub (just returns)

**Purpose** (Likely): Would compute line center depths and source functions

**Expected Functionality**: 
- Calculate properties specific to resonance line centers
- Compute line center optical depth tau(center)
- Compute line center source function

**Parameters**: None currently (stub only)

---

### 2. `SUBROUTINE CORINT` (lines 499-501)

**Status**: Empty stub (just returns)

**Purpose** (Likely): Handle corona/chromosphere integration

**Expected Functionality**:
- Extend radiative transfer calculations into the corona
- Handle additional temperature layers above the photosphere
- Integrate radiative transfer with corona parameters

**Parameters**: None currently (stub only)

---

### 3. `SUBROUTINE PRDJNU` (lines 502-504)

**Status**: Empty stub (just returns)  
**Status in Main Program**: Commented out (line 259)

**Purpose** (Likely): Partial redistribution Doppler calculation

**Expected Functionality**:
- Handle partial redistribution (PRD) effects for strong absorption lines
- Compute frequency redistribution functions
- Apply PRD corrections to line opacity

**Parameters**: `RHOXJ` (depth parameter for PRD calculation)

---

## External Subroutine Calls (Library Functions)

### 1. `CALL READIN(20)` (line 130)

**Function**: Reads input stellar atmosphere model from standard input (stdin)

**Input**:
- stdin: Atmospheric structure in DECK6 format
  - Contains: T(τ), P(τ), ρ(τ), electron density, opacities at 72 depth points

**Output**:
- Populates COMMON blocks:
  - `/TEMP/`: Temperature arrays T(kw), TLOG(kw), HKT(kw), HCKT(kw)
  - `/STATE/`: P(kw), XNE(kw), RHO(kw), PTOTAL(kw)
  - `/RHOX/`: RHOX(kw) [depth variable], NRHOX [number of depth points]
  - `/TEFF/`: TEFF, GRAV, GLOG [stellar parameters]
  - `/ELEM/`: ABUND(99), ATMASS(99)

**Source**: Likely defined in a separate library file (READIN.FOR or similar)

---

### 2. `CALL W('FSCAT ', FSCAT, NRHOX)` (line 216)

**Function**: Write binary data to fort unit

**Parameters**:
- String identifier for data type (6 chars)
- FSCAT array (scattering fraction at each depth)
- NRHOX (number of depth points)

**Output**:
- Written to current fort unit (Fortran I/O)

**Note**: This is part of a binary I/O library, possibly custom-built for ATLAS/SYNTHE

**Similar calls**:
```fortran
CALL W('FSCAT ', FSCAT, NRHOX)
CALL W('BFUDGE', BFUDGE, NRHOX)
```

---

### 3. `CALL JOSH(IFSCAT, IFSURF)` (lines 308, 329, 397, 408, 470, 475)

**Function**: Core radiative transfer integration routine

**Parameters**:
- `IFSCAT`: Scattering control flag
  - 0 = No scattering
  - 1 = With scattering
- `IFSURF`: Output type flag
  - 1 = Surface flux
  - 2 = Surface intensity (for multiple angles)

**Input COMMON blocks** (read by JOSH):
- `/TEMP/`: Temperature structure
- `/STATE/`: Pressure, electron density, density
- `/TAUSHJ/`: TAUNU(kw) [optical depth], SNU(kw) [source function]
- `/OPS/`: Opacity arrays (ACOOL, ALUKE, AHOT, ALINES, etc.)
- `/OPTOT/`: Total opacity (ACONT, SCONT, ALINE, SLINE)
- `/PZERO/`: KNU array, PRADK (radiation pressure)
- `/MUS/`: ANGLE(20), NMU [number of angles for intensity]

**Output COMMON blocks** (written by JOSH):
- `/TAUSHJ/`: TAUNU(kw), SNU(kw), HNU(kw) [Eddington flux], JNU(kw) [mean intensity]
- `/MUS/`: SURFI(MU) [surface intensity at angle MU]

**Algorithm** (Likely):
1. Solve radiative transfer equation: dI_ν/dτ = I_ν - S_ν
2. For each angle μ (cos of angle to normal):
   - Integrate from top to bottom (for upward rays)
   - Integrate from bottom to top (for downward rays)
3. Apply boundary conditions:
   - Top: No incoming radiation (free boundary)
   - Bottom: Thermal radiation from deep photosphere
4. Compute moments (flux, mean intensity)
5. Output emergent intensity or flux

**Source**: Defined in a separate library file (likely JOSH.FOR)

---

## Common Block Variables Reference

### Key COMMON Blocks Used

| COMMON Block | Key Variables | Purpose |
|--------------|---------------|---------|
| `/TEMP/` | T(kw), TK(kw), HKT(kw) | Temperature at each depth, in different units (K, eV, etc.) |
| `/STATE/` | P(kw), XNE(kw), RHO(kw) | Pressure, electron density, mass density |
| `/RHOX/` | RHOX(kw), NRHOX | Depth coordinate, number of depth points |
| `/TEFF/` | TEFF, GRAV, GLOG | Stellar effective temperature, gravity, log10(g) |
| `/FREQ/` | FREQ, FREQLG, BNU(kw) | Current frequency, log(frequency), Planck function |
| `/OPS/` | ACOOL, ALUKE, AHOT, ALINES | Opacity from various atomic processes |
| `/OPTOT/` | ACONT(kw), SCONT(kw), ALINE(kw), SLINE(kw) | Total continuum/line opacity & scattering |
| `/TAUSHJ/` | TAUNU(kw), SNU(kw), HNU(kw), JNU(kw) | Optical depth, source function, Eddington flux, mean intensity |
| `/MUS/` | ANGLE(20), SURFI(20), NMU | Angles for intensity calc, surface intensity, number of angles |
| `/PZERO/` | KNU(kw), PRADK(kw) | Opacity, radiation pressure |
| `/HEIGHT/` | HEIGHT(kw) | Height in atmosphere (km or cm) |
| `/BHYD/` | BHYD(kw,8), XNFPH, XNFH | Hydrogen bound-free opacity, number densities |
| `/BHE/` | BHE1, BHE2, XNFPHE | Helium opacity arrays |
| `/BAL/`, `/BB/`, `/BC/`, etc. | Element-specific opacity data | Opacity for individual chemical elements |

---

## Data Flow and I/O Files

### Input Files

| Unit | File | Format | Contents |
|------|------|--------|----------|
| 5 (stdin) | `output_synthe.out` | Text (DECK6) | Stellar atmosphere model input |
| 9 | `fort.9` (from synthe.exe) | Binary | Line opacity, radiative transfer data from previous stage |
| 10 | `fort.10` (from synthe.exe) | Binary | Continuum opacity edges and scattering data |
| 20 | `fort.20` | Binary | Pre-computed line data (optional) |
| 25 | `fort.25` | Text | Parameters (RHOXJ, R1, R101, spectrum params) |
| 99 | `mask.bin` | Binary | Wavelength mask (optional, added by patch) |

### Output Files

| Unit | File | Format | Contents |
|------|------|--------|----------|
| 6 | stdout | Text | Status messages, debug output, spectrum values |
| 7 | `fort.7` (spectrum.bin) | Binary | Final synthetic spectrum |
| 17 | `fort.17` | Text | Detailed line-by-line output (optional) |

---

## Key Computational Loops

### 1. Continuum Spectrum Loop (lines 223-275)

```fortran
DO 25 NU=NULO,NUHI              ! Loop over each wavelength point
    WAVE = WBEGIN * RATIO**(NU-1)
    
    ! Find which frequency edge this wavelength is between
    DO WHILE (WAVE > WLEDGE(IEDGE+1))
        IEDGE = IEDGE + 1
    END DO
    
    ! Quadratic interpolation of continuum opacity
    C1 = (WAVE - HALFEDGE)*(WAVE - WLEDGE(IEDGE+1)) / DELEDGE
    C2 = (WLEDGE(IEDGE) - WAVE)*(WAVE - WLEDGE(IEDGE+1))*2 / DELEDGE
    C3 = (WAVE - WLEDGE(IEDGE))*(WAVE - HALFEDGE) / DELEDGE
    
    ACONT(J) = 10^(C1*CONTABS(1,...) + C2*CONTABS(2,...) + C3*CONTABS(3,...))
    
    ! Calculate frequency and Planck function
    FREQ = 2.99792458D17 / WAVE
    BNU(J) = 1.47439D-02 * (FREQ/1D15)^3 * EXP(-FREQ*HKT(J)) / (1 - EXP(-FREQ*HKT(J)))
    
    ! Integrate radiative transfer (main computation)
    CALL JOSH(IFSCAT, IFSURF)
    
    ! Read line contribution
    READ(9) ASYNTH
    
    ! If masked, skip this wavelength
    IF (.NOT. KEEP(NU) .AND. NU > 1) CYCLE
    
    ! Add line opacity
    ALINE(J) = ASYNTH(J) * (1 - FSCAT(J))
    
    ! Integrate with line opacity
    CALL JOSH(1, IFSURF)
    
    ! Output result
    WRITE(7) HNU, Surface intensities
END DO
```

**Wavelength Points**: Logarithmically spaced over requested range
- Default: ~2 million points (limited by buffer size)
- Spacing: λ × Δλ = constant (constant resolution)

---

### 2. Line Processing Loop (lines 358-393)

```fortran
DO 90 ILINE=1,NLINES
    ! Read line data: wavelength, oscillator strength, damping, etc.
    READ(9) LINDAT8I, LABEL, LABELP, OTHER1, OTHER2, &
            LINDAT8II, LINDAT4I, REF, LINDAT4II, ALINEC
    
    WAVE = WLVAC          ! Vacuum wavelength of line
    
    ! Interpolate continuum opacity at line wavelength
    ! (same as above using C1, C2, C3 interpolation)
    
    ! Calculate Planck function at line wavelength
    ! (same as above)
    
    ! Compute line opacity ALINEC and radiative transfer
    CALL JOSH(1, IFSURF)
    CONCEN = HNU(1)       ! Flux at line wing
    
    ! Output line core intensity/flux
    CALL JOSH(1, IFSURF)
    CENTER = HNU(1)       ! Flux at line core
    
    RESID = CENTER / CONCEN   ! Line depth
    
    ! Write output
    WRITE(7) Line data and intensity
END DO
```

---

## Opacity Calculation

### Continuum Opacity Sources

Within COMMON blocks, multiple opacity types are tracked:

```fortran
COMMON /OPS/
    ACOOL(kw)      ! Cooling (e.g., from free-free)
    ALUKE(kw)      ! Luke's opacity contribution
    AHOT(kw)       ! Hot opacity (high energy)
    ALINES(kw)     ! Atomic line blanketing opacity
    SIGEL(kw)      ! Electron scattering cross section
    AXLINE(kw)     ! X-ray line opacity
    SIGXL(kw)      ! X-ray line scattering
    AXCONT(kw)     ! X-ray continuum opacity
    SIGX(kw)       ! X-ray scattering
    SXLINE(kw)     ! Additional X-ray line scattering
    SXCONT(kw)     ! Additional X-ray continuum scattering
END

COMMON /OPTOT/
    ACONT(kw)      ! Total continuum opacity
    SCONT(kw)      ! Continuum scattering
    ALINE(kw)      ! Total line opacity
    SLINE(kw)      ! Line scattering
    SIGMAC(kw)     ! Continuum scattering cross section (per particle)
    SIGMAL(kw)     ! Line scattering cross section
END
```

### Element-Specific Opacity

Individual chemical elements have dedicated COMMON blocks for bound-free opacity:

```fortran
COMMON /BHYD/    ! Hydrogen:    BHYD(kw,8), XNFPH(kw,2)
COMMON /BHE/     ! Helium:      BHE1(kw,29), XNFPHE(kw,3)
COMMON /BB/      ! Boron:       BB1(kw,7), XNFPB(kw,1)
COMMON /BC/      ! Carbon:      BC1(kw,14), XNFPC(kw,2)
COMMON /BMG/     ! Magnesium:   BMG1(kw,11), XNFPMG(kw,2)
COMMON /BSI/     ! Silicon:     BSI1(kw,11), XNFPSI(kw,2)
COMMON /BO/      ! Oxygen:      BO1(kw,13), XNFPO(kw,1)
COMMON /BNA/     ! Sodium:      BNA1(kw,8), XNFPNA(kw,1)
COMMON /BAL/     ! Aluminum:    BAL1(kw,9), XNFPAL(kw,2)
COMMON /BFE/     ! Iron:        BFE1(kw,15), XNFPFE(kw,1)
COMMON /BCA/     ! Calcium:     BCA1(kw,8), XNFPCA(kw,2)
COMMON /BK/      ! Potassium:   BK1(kw,8), XNFPK(kw,1)
```

These are populated by earlier stages (synthe.exe, rmolecasc.exe, etc.) and read/reused by SPECTRV.

---

## Parameters Read from fort.25

The following parameters are read from `fort.25` (lines 125-126):

```fortran
READ(25,1) RHOXJ, R1, R101, PH1, PC1, PSI1, PRDDOP, PRDPOW
1 FORMAT(8F10.5)
```

| Parameter | Meaning | Typical Value |
|-----------|---------|---------------|
| RHOXJ | Depth for line source function (RHOX units) | 0.0 (unused in patched version) |
| R1 | Residual intensity at plot bottom | 0.0 |
| R101 | Residual intensity at plot top | 1.0 |
| PH1 | Hydrogen opacity adjustment factor | 0.0 |
| PC1 | Carbon opacity adjustment factor | 0.0 |
| PSI1 | Silicon opacity adjustment factor | 0.0 |
| PRDDOP | Partial redistribution Doppler width | 0.0 (unused, PRDJNU commented out) |
| PRDPOW | Partial redistribution power law | 0.0 (unused) |

---

## Masking Feature (Added by Patch)

Lines 260-271 implement optional wavelength masking:

```fortran
INQUIRE(FILE='mask.bin', EXIST=EXISTS)
IF (EXISTS) THEN
    OPEN(UNIT=99, FILE='mask.bin', STATUS='OLD', ...)
    READ(99) MASKBYTE(1:NBYTES)
    DO NU = 1, NBYTES
        KEEP(NU) = (MASKBYTE(NU) .NE. 0)
    END DO
ELSE
    ! If no mask, process all wavelengths
    DO NU = 1, NBYTES
        KEEP(NU) = .TRUE.
    END DO
END IF
```

**Usage**: Allows skipping certain wavelength regions (e.g., telluric regions) during computation.

**Format**: `mask.bin` - binary file with one BYTE per wavelength point (0 = skip, non-zero = compute)

---

## Summary: External Dependencies

### Subroutines Called (External Library Functions)

| Subroutine | Source | Criticality | Complexity |
|------------|--------|-------------|-----------|
| READIN(20) | Library (likely READIN.FOR) | CRITICAL | High - Complex format parsing |
| W(...) | Custom I/O Library | MEDIUM | Low - Simple array write |
| JOSH(IFSCAT, IFSURF) | Library (JOSH.FOR) | CRITICAL | Very High - Core radiative transfer solver |
| EXIT | System (intrinsic) | REQUIRED | Trivial - Program termination |

### Stubs (Currently Empty, In This File)

| Subroutine | Purpose | Criticality | Status |
|------------|---------|-------------|--------|
| LINCEN | Line center calculations | LOW | Disabled (placeholder) |
| CORINT | Corona integration | LOW | Disabled (placeholder) |
| PRDJNU | Partial redistribution | LOW | Disabled (commented out) |

---

## Algorithm Complexity

### Time Complexity

For a spectrum with **N_wl** wavelength points, **N_depth** atmospheric layers, and **N_lines** spectral lines:

- **Continuum spectrum**: O(N_wl × N_depth) due to JOSH radiative transfer integration
- **Line spectrum**: O(N_lines × N_depth) for line opacity calculations
- **Total**: O((N_wl + N_lines) × N_depth)

**Typical values**:
- N_wl ~ 2,000,000 (limited by buffer)
- N_depth = 72
- N_lines ~ 100,000 to 1,000,000

**Estimated total operations**: ~10^8 to 10^11 floating-point operations

### Memory Requirements

```
Arrays with kw=99 dimensions (depth points):
  - T(99), P(99), etc.               ~100 × 8 bytes = 800 B per array
  - CONTABS(3,377,99)               ~3,500 × 8 bytes = 28 KB
  - CONTSCAT(3,377,99)              ~28 KB
  - Element-specific opacity arrays ~500 KB total
  - KEEP(2,010,001)                 ~2 MB for full spectrum
  
Total: ~5-10 MB baseline + data loaded from files
```

---

## Key Differences: Patched vs Original

The `.patched.for` version includes:

1. **Masking feature** (lines 260-271): Skip wavelength regions
2. **Progress output**: Print statements for tracking computation
3. **Byte format for mask**: Uses INTEGER*1 MASKBYTE array instead of logical directly

---

## Python/PyTorch Rewrite Considerations

### Critical Functions to Implement

1. **JOSH Radiative Transfer Integration** (Most Complex)
   - Solve differential equations
   - Handle boundary conditions
   - Compute moments (flux, mean intensity)
   - Support multiple angles

2. **Opacity Interpolation**
   - 3-point quadratic interpolation for continuum
   - Doppler broadening for lines
   - Temperature/density dependent opacity

3. **Line Profile Convolution**
   - Doppler broadening: exp(-(v/v_D)^2)
   - Natural broadening: Lorentzian
   - Stark broadening: pressure-dependent

4. **Radiative Transfer Solver**
   - Second-order ODE solver (tau parameter)
   - Boundary value problem with depth integration
   - Vectorized implementation for thousands of wavelengths

### Rewrite Strategy

**Phase 1: Direct Translation**
- Port READIN functionality (read DECK6 format)
- Port JOSH to PyTorch (vectorize depth dimension)

**Phase 2: Optimization**
- Use PyTorch batching for all wavelengths simultaneously
- GPU acceleration for JOSH iterations

**Phase 3: Enhancement**
- Implement full LINCEN, CORINT, PRDJNU
- Add improved opacity interpolation schemes
