# Testing QuickStart Guide

## Run All Tests
```bash
cd /home/dobos/project/kurucz-torch
/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python -m pytest tests/test_atlas_model_reader.py -v
```

## Run Specific Test Class
```bash
# CardReader tests only
python -m pytest tests/test_atlas_model_reader.py::TestCardReader -v

# AtlasModelReader tests only
python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReader -v

# Integration tests only
python -m pytest tests/test_atlas_model_reader.py::TestIntegration -v
```

## Run Single Test
```bash
# Test TEFF field parsing
python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReader::test_read_model_teff -v

# Test gravity conversion
python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReaderEdgeCases::test_gravity_log_scale_conversion -v
```

## View Test Results Summary
```bash
python -m pytest tests/test_atlas_model_reader.py -v --tb=line
```

## Test Your Changes
After modifying the reader implementation:
```bash
python -m pytest tests/test_atlas_model_reader.py -v
```

If any test fails, the output shows:
- Which test failed
- Expected vs. actual values
- Line number in test file
- Line number in implementation

## Test Data Files

### Minimal Test File (3 layers)
```
tests/test_input_minimal.txt
- Fast testing (~0.01s per test)
- Covers all essential fields
- Good for debugging
```

### Standard Test File (12 layers)
```
tests/test_input_standard.txt
- Realistic solar-like model
- Full atmospheric profiles
- Integration testing
```

## Common Patterns

### Test a new keyword handler
1. Add test input to test_input_minimal.txt or create new file
2. Add test method to TestAtlasModelReader class:
   ```python
   def test_read_model_my_keyword(self):
       reader = AtlasModelReader()
       atm = reader.read_model("tests/test_input_minimal.txt")
       assert atm.MY_FIELD == expected_value
   ```
3. Run: `python -m pytest tests/test_atlas_model_reader.py::TestAtlasModelReader::test_read_model_my_keyword -v`

### Debug a failing test
```bash
# Run with detailed output
python -m pytest tests/test_atlas_model_reader.py::ClassName::test_name -vv

# Run with full traceback
python -m pytest tests/test_atlas_model_reader.py::ClassName::test_name -vv --tb=long
```

### Profile test performance
```bash
# Time individual tests
python -m pytest tests/test_atlas_model_reader.py -v --durations=10
```

## Expected Output

### Success (all 35 tests pass)
```
============================== 35 passed in 0.76s ==============================
```

### Failure
```
FAILED tests/test_atlas_model_reader.py::TestClass::test_name
AssertionError: assert 5777.0 == 5777.1
  +  where 5777.0 = atm.TEFF
```

## Test Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 35 |
| Pass Rate | 100% |
| Execution Time | ~0.76 seconds |
| Test Classes | 6 |
| Lines of Test Code | 413 |
| Test Data Files | 2 |

## What's Tested

✅ **CardReader**
- Line reading and buffering
- Keyword extraction (single/compound)
- Float parsing (decimal/scientific)
- Array reading (multi-line)
- Integer parsing
- Empty line handling

✅ **AtlasModelReader**
- File I/O and error handling
- Keyword dispatch
- Field validation
- Computed values (GLOG, FLUX)
- Array parsing and storage
- Reader reusability

✅ **Atmosphere**
- Object creation
- Array fields
- Optional defaults

✅ **Physics**
- Gravity log-scale conversion (GRAV < 10 → 10^GRAV)
- Log-gravity round-trip (GLOG = log₁₀(GRAV))
- Stefan-Boltzmann flux (FLUX = 5.6697e-5/12.5664 * TEFF⁴)
- Array dimension matching

## Environment Setup

If pytest is not installed:
```bash
/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python -m pip install pytest
```

Verify pytest:
```bash
/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python -m pytest --version
```

## Troubleshooting

### "No module named pytest"
```bash
/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python -m pip install pytest
```

### "No module named kurucz"
```bash
cd /home/dobos/project/kurucz-torch
# Ensure python path includes the project directory
```

### Test hangs or takes too long
- Comment out torch imports in atmosphere.py (torch may hang on Python 3.6)
- Use minimal test file: `tests/test_input_minimal.txt`

### Floating-point assertion errors
Use approximate comparison:
```python
# Instead of:
assert value == expected  # May fail due to FP precision

# Use:
assert abs(value - expected) < tolerance
```

## References

- **Full Documentation**: `UNIT_TEST_DOCUMENTATION.md`
- **Test Implementation**: `tests/test_atlas_model_reader.py`
- **CardReader**: `python/kurucz/compat/card_reader.py`
- **AtlasModelReader**: `python/kurucz/compat/model_reader.py`
- **Atmosphere**: `python/kurucz/atmosphere.py`

## Quick Links

```bash
# View test file
cat tests/test_atlas_model_reader.py

# View test data
cat tests/test_input_minimal.txt
cat tests/test_input_standard.txt

# View documentation
cat UNIT_TEST_DOCUMENTATION.md
```
