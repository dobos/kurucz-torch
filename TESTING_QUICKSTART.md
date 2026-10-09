# Testing QuickStart Guide

## Run All Tests

Using the test runner script:
```bash
cd /home/dobos/project/kurucz-torch
./run_tests.sh
```

Or with Python directly:
```bash
export PYTHONPATH=/home/dobos/project/kurucz-torch/python
python -m unittest discover tests/kurucz -v
```

## Run Specific Test Module

```bash
# CardReader tests only
./run_tests.sh kurucz.compat.test_card_reader -v

# AtlasModelReader tests only
./run_tests.sh kurucz.compat.test_model_reader -v

# Atmosphere tests only
./run_tests.sh kurucz.test_atmosphere -v
```

## Run Specific Test Class

```bash
./run_tests.sh kurucz.compat.test_card_reader.CardReaderTests -v
./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderTests -v
./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderIntegrationTests -v
```

## Run Single Test

```bash
# Test TEFF field parsing
./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderTests.test_read_model_teff -v

# Test gravity conversion
./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderEdgeCaseTests.test_gravity_log_scale_conversion -v
```

## View Test Results Summary

```bash
./run_tests.sh kurucz 2>&1 | tail -5
```

## Test Your Changes

After modifying the reader implementation:
```bash
./run_tests.sh kurucz
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

## Test Directory Structure

```
tests/
├── kurucz/                           # Matches python/kurucz/
│   ├── compat/                       # Matches python/kurucz/compat/
│   │   ├── test_card_reader.py      # Tests for card_reader.py
│   │   ├── test_model_reader.py     # Tests for model_reader.py
│   │   └── __init__.py
│   ├── test_atmosphere.py            # Tests for atmosphere.py
│   └── __init__.py
├── test_input_minimal.txt            # 3-layer test fixture
└── test_input_standard.txt           # 12-layer test fixture
```

## Common Patterns

### Test a new keyword handler

1. Add test input to test_input_minimal.txt or create new file
2. Add test method to appropriate class in test_model_reader.py:
   ```python
   def test_read_model_my_keyword(self):
       reader = AtlasModelReader()
       atm = reader.read_model("tests/test_input_minimal.txt")
       self.assertEqual(atm.MY_FIELD, expected_value)
   ```
3. Run: `./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderTests.test_read_model_my_keyword -v`

### Debug a failing test

```bash
# Run with verbose output
./run_tests.sh kurucz.compat.test_model_reader -v

# Run specific failing test with full output
./run_tests.sh kurucz.compat.test_model_reader.AtlasModelReaderTests.test_name -v 2>&1
```

## Expected Output

### Success (all tests pass)
```
Ran 54 tests in 4.923s

OK
```

### Failure
```
FAIL: test_read_model_teff (kurucz.compat.test_model_reader.AtlasModelReaderTests)
Test that TEFF is correctly read
----------------------------------------------------------------------
Traceback (most recent call last):
  File "tests/kurucz/compat/test_model_reader.py", line XX, in test_read_model_teff
    self.assertEqual(atm.TEFF, 5777.0)
AssertionError: 5777.0 != 5777.1

----------------------------------------------------------------------
Ran 54 tests in 4.923s

FAILED (failures=1)
```

## Test Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 54 |
| Pass Rate | 100% |
| Execution Time | ~4.9s |
| AtlasModelReader Tests | 35 |
| Other Tests | 19 |
| Test Modules | 3 |
| Lines of Test Code | ~600 |
| Test Data Files | 2 |

## What's Tested

✅ **CardReader** (tests/kurucz/compat/test_card_reader.py)
- Line reading and buffering
- Keyword extraction (single/compound)
- Float parsing (decimal/scientific)
- Array reading (multi-line)
- Integer parsing
- Empty line handling

✅ **AtlasModelReader** (tests/kurucz/compat/test_model_reader.py)
- File I/O and error handling
- Keyword dispatch
- Field validation
- Computed values (GLOG, FLUX)
- Array parsing and storage
- Reader reusability

✅ **Atmosphere** (tests/kurucz/test_atmosphere.py)
- Object creation
- Array fields
- Optional defaults

✅ **Physics**
- Gravity log-scale conversion (GRAV < 10 → 10^GRAV)
- Log-gravity round-trip (GLOG = log₁₀(GRAV))
- Stefan-Boltzmann flux (FLUX = 5.6697e-5/12.5664 * TEFF⁴)
- Array dimension matching

## Environment Setup

The test runner script automatically handles PYTHONPATH setup.

To verify unittest is working:
```bash
python -m unittest --version
```

## Troubleshooting

### "No module named kurucz"
Make sure PYTHONPATH includes the python directory:
```bash
export PYTHONPATH=/home/dobos/project/kurucz-torch/python
```

Or use the provided test runner:
```bash
./run_tests.sh
```

### "Permission denied" on run_tests.sh
Make the script executable:
```bash
chmod +x run_tests.sh
```

### Test hangs or takes too long
- Use minimal test file: `tests/test_input_minimal.txt`
- Run specific test module: `./run_tests.sh kurucz.compat.test_card_reader`

### Floating-point assertion errors
unittest's assertAlmostEqual handles this:
```python
self.assertAlmostEqual(value, expected, places=2)
```

## Framework Comparison: unittest vs pytest

| Feature | unittest | pytest |
|---------|----------|--------|
| Standard Library | ✅ Yes | ❌ No |
| Matchers | Limited | Extensive |
| Fixtures | `setUp`/`tearDown` | `@pytest.fixture` |
| Parametrization | Limited | `@pytest.mark.parametrize` |
| Plugins | Few | Many |
| Async Support | ✅ Yes | ✅ Yes |

We chose **unittest** for:
1. Part of Python standard library (no external dependencies)
2. Class-based structure matching namespace hierarchy
3. Familiar to Java developers (JUnit-like)
4. Strong type checking support with IDE integration

## References

- **Full Documentation**: `UNIT_TEST_DOCUMENTATION.md`
- **Test Implementations**: 
  - `tests/kurucz/compat/test_card_reader.py`
  - `tests/kurucz/compat/test_model_reader.py`
  - `tests/kurucz/test_atmosphere.py`
- **Source Code**: 
  - `python/kurucz/compat/card_reader.py`
  - `python/kurucz/compat/model_reader.py`
  - `python/kurucz/atmosphere.py`
- **Test Runner**: `run_tests.sh`

## Quick Links

```bash
# View test files
cat tests/kurucz/compat/test_card_reader.py
cat tests/kurucz/compat/test_model_reader.py
cat tests/kurucz/test_atmosphere.py

# View test data
cat tests/test_input_minimal.txt
cat tests/test_input_standard.txt

# View documentation
cat UNIT_TEST_DOCUMENTATION.md
```
