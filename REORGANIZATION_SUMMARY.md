# Code Reorganization: ATLAS Compatibility Layer

## Summary
Moved `CardReader` and `AtlasModelReader` classes under the `compat` namespace to better reflect their purpose as ATLAS compatibility layers.

## Changes

### File Moves
```
python/kurucz/card_reader.py        → python/kurucz/compat/card_reader.py
python/kurucz/model_reader.py       → python/kurucz/compat/model_reader.py
```

### Import Updates

**compat/model_reader.py**
- Changed: `from .atmosphere import Atmosphere`
- To: `from ..atmosphere import Atmosphere`

**compat/atlas7v.py**
- Removed: `sys.path.insert()` hack
- Changed to proper relative imports:
  ```python
  from .model_reader import AtlasModelReader
  from ..atmosphere import Atmosphere
  ```

**compat/__init__.py**
- Added proper package exports:
  ```python
  from .atlas7v import Atlas7v
  from .model_reader import AtlasModelReader
  from .card_reader import CardReader
  ```

**kurucz/__init__.py**
- Updated to import from compat:
  ```python
  from .atmosphere import Atmosphere
  from .compat.atlas7v import Atlas7v
  from .compat.card_reader import CardReader
  from .compat.model_reader import AtlasModelReader
  ```

## New Package Structure

```
kurucz/
├── atmosphere.py          # Core Atmosphere dataclass
├── __init__.py            # Main package (re-exports compat)
├── compat/                # ATLAS Compatibility Layer
│   ├── __init__.py
│   ├── atlas7v.py         # High-level wrapper
│   ├── card_reader.py     # 80-char card deck parser
│   ├── model_reader.py    # READIN implementation
│   └── ...
├── element_opacity.py     # Opacity modules
├── line_data.py
├── opacities.py
├── radiative_transfer_state.py
├── spectral_synthesis_config.py
├── opacity/               # Opacity implementations
└── ...
```

## Import Options

All of these work now:

```python
# Option 1: Convenience imports from main package
from kurucz import Atmosphere, Atlas7v, CardReader, AtlasModelReader

# Option 2: Explicit imports from compat
from kurucz.compat import Atlas7v, AtlasModelReader, CardReader

# Option 3: Direct submodule imports
from kurucz.compat.atlas7v import Atlas7v
from kurucz.compat.model_reader import AtlasModelReader
from kurucz.compat.card_reader import CardReader
```

## Benefits

1. **Better Organization**: ATLAS-specific compatibility code is grouped together
2. **Clear Intent**: `compat` namespace signals "ATLAS compatibility layer"
3. **Scalability**: Easy to add other compatibility layers (e.g., `synthe`, `turbospectrum`)
4. **Cleaner Main Package**: Core classes are clearly separated from compatibility wrappers
5. **No Import Hacks**: Removed sys.path manipulation, using clean relative imports

## Testing

✅ All imports working
✅ All functionality preserved
✅ Full test passes (Atlas7v reader still works correctly)
✅ Module compilation succeeds

## Verification

Test the reorganization:
```bash
python3 << 'EOF'
from kurucz import Atlas7v, Atmosphere
atlas = Atlas7v()
atm = atlas.read_model("tests/test_input_minimal.txt")
print(f"TEFF = {atm.TEFF} K")
EOF
```

Result:
```
TEFF = 5777.0 K
```

✅ Success!
