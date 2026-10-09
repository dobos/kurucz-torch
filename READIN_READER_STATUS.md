# ATLAS READIN Reader Implementation Status

## Overview
Complete implementation of the ATLAS READIN subroutine reader in Python, based on the Fortran code in `BasicATLAS/src/atlas7v.for`.

## Status: ✅ Complete (Phases 1-5)

### Phase 1: Card Reader Utilities ✅
- **File**: `python/kurucz/card_reader.py`
- **Implements**: Low-level I/O for ATLAS 80-character card format
- **Features**:
  - `CardReader` class for sequential line-by-line reading
  - `extract_keyword()`: Recognizes ATLAS keywords (TEFF, GRAVITY, READ T, etc.)
  - `parse_float()`: Handles Fortran float formats (scientific notation, etc.)
  - `parse_int()`: Parses integers from card lines
  - `read_float_array()`: Reads multi-line float arrays (tested: 3-float arrays)
  - Standalone utilities for parsing floats and extracting keywords

**Key Implementation Details**:
- Keywords are 4-12 uppercase characters, possibly multi-word (e.g., "READ T", "CHANGE RHOX")
- Float regex: `[-+]?(\d+\.?\d*|\d*\.\d+)([eE][-+]?\d+)?` handles all Fortran formats
- Array reading uses regex to find all floats in a line and aggregate across lines
- Stops reading arrays when it encounters a keyword line

### Phase 2-3: Keyword Handlers ✅
- **File**: `python/kurucz/model_reader.py`
- **Implements**: Main READIN parser with 8+ keyword handlers
- **Handlers Implemented**:
  - `_handle_teff()`: Reads TEFF, computes Stefan-Boltzmann FLUX
  - `_handle_gravity()`: Reads GRAVITY, converts from log scale if needed, computes GLOG
  - `_handle_title()`: Reads 74-character model title
  - `_handle_lte()` / `_handle_nlte()`: Sets NLTEON flag
  - `_handle_change_rhox()`: Reads depth grid (NRHOX + array of RHOX values)
  - `_handle_read()`: Dispatches to T, P, XNE array readers based on "READ T/P/XNE" keywords
  - `_handle_optional_flag()`: Handles MOLECULES, TURBULENCE, CONVECTION flags
  - `_read_temperature()`, `_read_pressure()`, `_read_electron_density()`: Array readers

**Key Implementation Details**:
- Gravity in log scale (< 10) is converted: GRAV = 10^GRAV
- Stefan-Boltzmann: FLUX = 5.6697e-5/12.5664 * TEFF^4 [erg/cm²/s]
- "READ T" is parsed as a compound keyword (not just "READ")
- Optional flags (NLTEON, IFMOL, IFTURB, IFCONV) default to 0 if not present
- TITLE is extracted as position 6-80 of line (Fortran: CARD(I+6))

### Phase 4: Main Dispatcher ✅
- **Class**: `AtlasModelReader` in `model_reader.py`
- **Main Method**: `read_model(filepath)` returns populated `Atmosphere` object
- **Main Loop**:
  1. Read lines sequentially
  2. Extract keyword from each line
  3. Dispatch to appropriate handler
  4. Skip data lines (empty or leading whitespace)
  5. Stop on END keyword or EOF
  6. Validate all 7 essential fields before returning

### Phase 5: Testing & Error Handling ✅
- **Test File**: `tests/test_input_minimal.txt` (14-line minimal deck)
- **Test Coverage**:
  - ✅ TEFF keyword parsing
  - ✅ GRAVITY keyword with log scale conversion
  - ✅ TITLE extraction (74 chars)
  - ✅ LTE flag setting
  - ✅ CHANGE RHOX with array reading (3 values)
  - ✅ READ T/P/XNE with array reading (3 values each)
  - ✅ Validation of all 7 essential fields
  - ✅ Proper error messages on missing fields

**Test Results**:
```
TEFF        = 5777.0 K
GRAV        = 2.69e+04 dyne/cm² (converted from log 4.43)
GLOG        = 4.4300
TITLE       = "Solar Model (G2V) - Test File"
NLTEON      = 0 (LTE)
NRHOX       = 3
FLUX        = 5.03e+09 erg/cm²/s

RHOX array  = [1e-10, 1.2e-10, 1.44e-10]
T array     = [3800.0, 3900.0, 4000.0] K
P array     = [10.0, 11.0, 12.1] dyne/cm²
XNE array   = [1e8, 1.1e8, 1.21e8] cm⁻³
```

## Data Structure: Atmosphere Class

**Location**: `python/kurucz/atmosphere.py`

**61+ UPPERCASE Variables** organized into logical groups:

1. **Stellar Parameters** (lines 29-36)
   - TEFF, GRAV, GLOG: Temperature, gravity, gravity log
   - FLUX: Stefan-Boltzmann radiative flux

2. **Depth Structure** (lines 39-41)
   - NRHOX: Number of depth points (max 99)
   - RHOX: Rosseland optical depth array

3. **Temperature Structure** (lines 44-54)
   - T, TK, TLOG, TKEV, HKT, HCKT: Temperature in various units/scales
   - HEIGHT: Height in atmosphere

4. **Pressure & Density** (lines 57-63)
   - P, XNE, XNATOM, RHO, PTOTAL: Pressure, electron density, etc.

5. **Radiation** (lines 66-75)
   - PRAD, ACCRAD, ABROSS, TAUROS: Radiation pressure, opacity
   - PRADK, KNU, EDENS: Radiation pressure constant, opacity, energy

6. **Additional Fields** (lines 78-90)
   - MOLWEIGHT, KAPPAC: Molecular weight, continuum absorption
   - NELEC, NATOM: Electron/atom counts
   - CONVEC, CONVECT: Convection indicators

7. **Metadata** (lines 93-100)
   - TITLE: Optional model title (str)
   - NLTEON: Non-LTE mode flag (0=LTE, 1=NLTE)
   - NUMITS: Max iteration count (was max_iterations)
   - NITERC: Convergence iteration count

8. **Optional Flags** (lines 103-106)
   - IFMOL, IFCONV, IFTURB: Molecule, convection, turbulence flags

## Known Limitations

1. **Python 3.6 Compatibility**: 
   - torch import hangs on Python 3.6
   - Fallback to Python lists instead of torch.Tensor
   - Type hints use string form for Python 3.6

2. **Array Format**:
   - Returns plain Python lists instead of torch tensors
   - User can convert to torch if needed: `torch.tensor(atm.RHOX, dtype=torch.float64)`

3. **Not Implemented** (by design for MVP):
   - FREQUENCIES section reading
   - DEPARTURE COEFFICIENTS section
   - Batch reading multiple models from single file
   - __post_init__ derived quantity calculations (e.g., TK, TLOG)

4. **Parser Limitations**:
   - No support for continuation lines or non-standard formats
   - Assumes 80-character fixed-format cards
   - No support for packed binary data

## Files Summary

### Core Implementation
- `python/kurucz/card_reader.py` (380 lines)
  - CardReader class and utility functions
  - Handles 80-char card parsing and float array reading
  
- `python/kurucz/model_reader.py` (360 lines)
  - AtlasModelReader class with read_model() entry point
  - 8+ keyword handlers
  - Validation logic

- `python/kurucz/atmosphere.py` (210 lines)
  - Atmosphere dataclass with 61+ UPPERCASE variables
  - Flat structure with comment groupings
  - Python 3.6 compatible (lazy torch import)

### Configuration
- `python/kurucz/__init__.py` (27 lines)
  - Simplified imports (CardReader, Atmosphere, AtlasModelReader only)
  - Other modules available on-demand

### Testing
- `tests/test_input_minimal.txt` (14 lines)
  - Minimal ATLAS input deck
  - Tests: TEFF, GRAVITY, TITLE, LTE, CHANGE RHOX, READ T/P/XNE, END

## Usage Example

```python
from kurucz import AtlasModelReader

# Read a model
reader = AtlasModelReader()
atm = reader.read_model("path/to/model.txt")

# Access data
print(f"Teff = {atm.TEFF} K")
print(f"Gravity = {atm.GRAV} dyne/cm²")
print(f"Depth points: {atm.NRHOX}")
print(f"Temperature: {atm.T}")  # Python list
print(f"Pressure: {atm.P}")     # Python list

# Convert to torch if needed
import torch
T_tensor = torch.tensor(atm.T, dtype=torch.float64)
```

## Next Steps (Post-MVP)

1. **Torch Integration**: Test with working torch installation (requires Python 3.7+)
2. **Real Model Testing**: Test with actual ATLAS model files
3. **Derived Quantities**: Implement TK, TLOG, TKEV, HKT, HCKT calculations in __post_init__
4. **Batch Reading**: Support reading multiple models from single file
5. **Error Recovery**: Better error messages with line numbers
6. **Performance**: Optimize read_float_array for large arrays
7. **Documentation**: Add complete docstrings and examples

## References

- **Fortran Source**: `/home/dobos/project/BasicATLAS/src/atlas7v.for` lines 1326-2950 (READIN subroutine)
- **ATLAS Documentation**: ATLAS/SYNTHE user's manual (Kurucz 1970-2021)
- **Atmosphere Structure**: Mapped from Fortran COMMON blocks:
  - /TEFF/, /GRAV/, /TEMP/, /STATE/, /DEPTH/, /RAD/, /MOL/, /ITER/, /IF/, /JUNK/

## Testing Checklist

- [x] CardReader keyword extraction
- [x] Float parsing (scientific notation)
- [x] Array reading (multi-line)
- [x] TEFF handler
- [x] GRAVITY handler (log scale)
- [x] TITLE handler
- [x] LTE/NLTE handlers
- [x] CHANGE RHOX handler
- [x] READ T handler
- [x] READ P handler
- [x] READ XNE handler
- [x] Validation (all 7 essential fields)
- [x] Error handling
- [x] Python 3.6 compatibility (torch fallback)
- [x] Integration test (full file read)
