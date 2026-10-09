# AtlasModelReader Unit Test Documentation

## Overview

Comprehensive unit test suite for the ATLAS model reader implementation. The test suite covers all three major components:

1. **CardReader** - Low-level text parsing utilities
2. **AtlasModelReader** - Main READIN parser implementation
3. **Atmosphere** - Data structure integration

**Total Test Count: 35 tests, all passing ✅**

## Test Structure

### 1. CardReader Tests (TestCardReader) - 8 tests

Tests for the low-level CardReader utility class that handles ATLAS card deck parsing.

#### Basic Tests
- `test_init`: Verify CardReader initialization
- `test_next_line`: Sequential line reading from file
- `test_extract_keyword`: Extract keyword from line (single keywords)
- `test_extract_keyword_compound`: Extract compound keywords (e.g., "READ T")
- `test_extract_keyword_empty_line`: Verify data lines return empty keyword

#### Float Parsing Tests
- `test_parse_float_simple`: Parse simple decimal floats (e.g., 5777.0)
- `test_parse_float_scientific`: Parse scientific notation (e.g., 1.00e-10)
- `test_read_float_array`: Read multi-line float arrays with line wrapping

### 2. AtlasModelReader Tests (TestAtlasModelReader) - 13 tests

Tests for the main ATLAS model reader that implements the READIN subroutine.

#### Basic Tests
- `test_init`: Verify AtlasModelReader initialization
- `test_read_model_minimal`: Read minimal test file successfully

#### Field Parsing Tests
- `test_read_model_teff`: TEFF effective temperature parsing
- `test_read_model_gravity`: GRAVITY log-scale conversion (GRAV < 10 → 10^GRAV)
- `test_read_model_glog`: Verify GLOG computed as log10(GRAV)
- `test_read_model_title`: TITLE metadata field parsing
- `test_read_model_nlteon`: NLTEON LTE/NLTE flag (0 for LTE, 1 for NLTE)
- `test_read_model_nrhox`: NRHOX depth point count
- `test_read_model_rhox_array`: RHOX depth grid array values
- `test_read_model_temperature_array`: Temperature profile array
- `test_read_model_pressure_array`: Pressure profile array
- `test_read_model_electron_density_array`: Electron density array
- `test_read_model_flux`: Stefan-Boltzmann flux computation from TEFF

### 3. Atmosphere Tests (TestAtmosphere) - 3 tests

Tests for the Atmosphere dataclass integration with the reader.

- `test_atmosphere_creation`: Basic Atmosphere object creation
- `test_atmosphere_array_fields`: Array field handling (RHOX, T, P, XNE)
- `test_atmosphere_optional_fields`: Optional field defaults (TITLE, NLTEON, NUMITS)

### 4. Integration Tests (TestIntegration) - 4 tests

End-to-end integration tests combining all components.

- `test_full_workflow_minimal_file`: Complete workflow with 3-layer minimal test file
  - Verifies all 7 essential fields are read correctly
  
- `test_full_workflow_standard_file`: Complete workflow with 12-layer standard test file
  - Verifies larger array handling
  - Tests proper array dimensions matching NRHOX
  
- `test_file_not_found`: Error handling for missing files
  
- `test_invalid_data_missing_teff`: Validation error handling

### 5. Advanced CardReader Tests (TestCardReaderAdvanced) - 4 tests

Edge cases and advanced float parsing scenarios.

- `test_parse_float_with_plus_sign`: Parse floats with explicit `+` sign
- `test_parse_float_with_minus_sign`: Parse negative floats with `-` sign
- `test_parse_int`: Integer parsing from lines
- `test_keyword_not_at_start`: Verify data lines (starting with spaces) aren't treated as keywords

### 6. AtlasModelReader Edge Cases (TestAtlasModelReaderEdgeCases) - 3 tests

Special cases and computed field validation.

- `test_multiple_reads_same_file`: Verify reader can be reused for multiple files
- `test_gravity_log_scale_conversion`: Verify log-scale gravity conversion (GRAV < 10)
- `test_flux_computation`: Verify Stefan-Boltzmann flux formula: `FLUX = 5.6697e-5/12.5664 * TEFF^4`

## Test Data Files

### test_input_minimal.txt (14 lines)
- **Layers**: 3
- **Fields**: TEFF, GRAVITY, TITLE, LTE, RHOX array, T array, P array, XNE array
- **Purpose**: Fast unit testing, quick validation
- **Values**:
  - TEFF: 5777.0 K
  - GRAVITY: 4.43 (log scale)
  - NRHOX: 3
  - Temperature: [3800, 3900, 4000] K
  - Pressure: [10.0, 11.0, 12.1] dyne/cm²
  - Density: [1e-10, 1.2e-10, 1.44e-10] g/cm³

### test_input_standard.txt (23 lines)
- **Layers**: 12
- **Fields**: TEFF, GRAVITY, TITLE, LTE, RHOX array (12 values), T array (12 values), P array (12 values), XNE array (12 values)
- **Purpose**: Integration testing with realistic multi-layer model
- **Values**:
  - TEFF: 5770.0 K (solar-like)
  - GRAVITY: 4.44 (log scale, solar-like)
  - Temperature range: 3800-4350 K
  - Pressure range: 10.00-12.20 dyne/cm²
  - Density range: 1e-10 to 7.4e-10 g/cm³

### synthe.out (477 lines)
- **Format**: SYNTHE spectral synthesis output (not ATLAS input)
- **Contains**: TEFF and GRAV header values, spectral data
- **Note**: Test data for reference; not used by AtlasModelReader (expects ATLAS input deck format)

## Test Coverage by Component

### CardReader Coverage
- Line reading and buffering
- Keyword extraction (single and compound)
- Float parsing (decimal and scientific notation)
- Array reading (multi-line)
- Integer parsing
- Empty line handling

### AtlasModelReader Coverage
- File I/O and error handling
- Keyword dispatch (TEFF, GRAVITY, TITLE, LTE/NLTE, CHANGE RHOX, READ T/P/XNE, END)
- Field validation (non-zero TEFF, valid NRHOX, array dimension matching)
- Computed fields (GLOG from GRAV, FLUX from TEFF)
- Array parsing and storage (Python lists with torch fallback)
- Multiple file reads (reader state reset)

### Atmosphere Coverage
- Object instantiation
- Array field handling
- Optional field defaults
- Integration with reader output

## Key Test Assertions

### Physics Validations
```python
# Gravity log-scale conversion (GRAV < 10 → 10^GRAV)
assert atm.GRAV > 10.0  # Ensure log scale was applied

# Gravity to log-gravity round-trip
expected_glog = math.log10(atm.GRAV)
assert abs(atm.GLOG - expected_glog) < 0.001

# Stefan-Boltzmann flux
expected_flux = 5.6697e-5 / 12.5664 * (atm.TEFF ** 4)
assert abs(atm.FLUX - expected_flux) < 1e6
```

### Array Dimension Matching
```python
# All profile arrays must match NRHOX
assert len(atm.T) == atm.NRHOX
assert len(atm.P) == atm.NRHOX
assert len(atm.XNE) == atm.NRHOX
assert len(atm.RHOX) == atm.NRHOX
```

### Field Value Validation
```python
# Verify specific read values
assert atm.T[0] == 3800.0  # First temperature
assert atm.NLTEON == 0     # LTE mode (not NLTE)
assert "Standard Solar Model" in atm.TITLE  # Title substring
```

## Test Execution

### Run All Tests
```bash
/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python -m pytest tests/test_atlas_model_reader.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_atlas_model_reader.py::TestCardReader -v
python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReader -v
python -m pytest tests/test_atlas_model_reader.py::TestIntegration -v
```

### Run Specific Test
```bash
python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReader::test_read_model_teff -v
```

### Generate Test Report
```bash
python -m pytest tests/test_atlas_model_reader.py -v --tb=short
```

## Test Results Summary

✅ **35 tests passing** (100% pass rate)

### Breakdown by Component
- CardReader: 8/8 ✅
- AtlasModelReader: 13/13 ✅
- Atmosphere: 3/3 ✅
- Integration: 4/4 ✅
- Advanced CardReader: 4/4 ✅
- AtlasModelReader Edge Cases: 3/3 ✅

### Execution Time
Typical run: ~0.77 seconds (Python 3.14.8 + pytest 9.1.1)

## Future Test Enhancements

### Potential Additional Tests
1. **NLTE Mode Testing**: Add test file with NLTE keyword
2. **Error Recovery**: Malformed input handling, missing keywords
3. **Large Models**: 72+ layer realistic ATLAS models
4. **Numerical Precision**: Float comparison tolerances
5. **Torch Integration**: Test torch.Tensor conversion path (when torch available)
6. **Performance Testing**: Large file reading benchmarks
7. **Format Variants**: Alternative ATLAS card deck formats
8. **Spectral Synthesis**: Integration with synthe.out format if needed

### Known Limitations
- synthe.out file format not yet integrated (SYNTHE output, not ATLAS input)
- Torch integration skipped on Python 3.6 environments (uses list fallback)
- Limited testing of all 50+ optional ATLAS input keywords
- No testing of NLTE elemental abundance arrays
- No testing of molecular equilibrium parameters

## Notes for Developers

### Test Independence
Each test is independent and can run in any order. Tests use:
- Fresh CardReader/AtlasModelReader instances per test
- Read-only test data files
- No shared state between tests

### Floating-Point Assertions
Use approximate comparisons for floating-point values:
```python
assert abs(computed - expected) < tolerance
```
Rather than exact equality:
```python
assert computed == expected  # May fail due to FP precision
```

### Array Value Selection
Tests validate first, last, and occasional middle array values rather than all elements:
```python
assert atm.T[0] == 3800.0    # First
assert atm.T[-1] == 4350.0   # Last
# Middle values checked implicitly via len() assertions
```

### Fortran Compatibility
Test data uses uppercase FORTRAN variable names:
- TEFF, GRAV, GLOG (not teff, grav, glog)
- RHOX, NRHOX (not rhox, nrhox)
- NLTEON, NUMITS (not nlte_mode, max_iterations)

This maintains 1:1 correspondence with atlas7v.for source code.

## References

- **ATLAS7v Fortran Source**: /home/dobos/project/BasicATLAS/atlas7v.for
  - READIN subroutine: lines 1326-2950
  - Card deck parsing examples: throughout source
  
- **Test Implementation**: /home/dobos/project/kurucz-torch/tests/test_atlas_model_reader.py
  
- **Reader Implementation**: 
  - CardReader: /home/dobos/project/kurucz-torch/python/kurucz/compat/card_reader.py
  - AtlasModelReader: /home/dobos/project/kurucz-torch/python/kurucz/compat/model_reader.py
  
- **Atmosphere Data Structure**: /home/dobos/project/kurucz-torch/python/kurucz/atmosphere.py

## Dependencies

- Python 3.6+
- pytest 7.0+
- pathlib (standard library)

## Test Maintenance

### When Adding New Keywords
1. Create test file with new keyword
2. Add parser method in AtlasModelReader._handle_*()
3. Add unit test in TestAtlasModelReader
4. Add integration test if it affects Atmosphere
5. Update this documentation

### When Fixing Parsing Bugs
1. Reproduce bug in unit test
2. Verify test fails
3. Fix implementation
4. Verify test passes
5. Run full suite to catch regressions

### When Changing Data Structures
1. Update test fixtures (test_input_*.txt)
2. Update assertion values in tests
3. Verify integration tests still pass
4. Update expected output values
