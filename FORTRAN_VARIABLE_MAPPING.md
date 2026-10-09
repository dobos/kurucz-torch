# Fortran Variable Name Mapping

All Python class field names now exactly match the Fortran variable names from the ATLAS READIN subroutine's COMMON blocks. This ensures consistency and makes cross-referencing with the Fortran code straightforward.

## Capitalization Convention

Following Fortran convention, all variable names are **UPPERCASE**.

Examples:
- Fortran: `TEFF` → Python: `atm.TEFF`
- Fortran: `VTURB(kw)` → Python: `atm.VTURB` (array of shape `(n_depth,)`)
- Fortran: `RHOX(kw)` → Python: `atm.RHOX` (array of shape `(n_depth,)`)

## Complete Variable Mapping by COMMON Block

### /TEFF/ - Stellar Parameters
| Fortran | Python | Type | Units |
|---------|--------|------|-------|
| TEFF | `atm.TEFF` | float | K |
| GRAV | `atm.GRAV` | float | cm/s² |
| GLOG | `atm.GLOG` | float | log₁₀(cm/s²) |

### /RHOX/ - Depth Structure
| Fortran | Python | Type | Shape |
|---------|--------|------|-------|
| RHOX(kw) | `atm.RHOX` | torch.Tensor | (n_depth,) |
| NRHOX | `atm.NRHOX` | int | scalar |

### /HEIGHT/ - Height Structure
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| HEIGHT(kw) | `atm.HEIGHT` | torch.Tensor | (n_depth,) | cm |

### /TEMP/ - Temperature Structure
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| T(kw) | `atm.T` | torch.Tensor | (n_depth,) | K |
| TK(kw) | `atm.TK` | torch.Tensor | (n_depth,) | thousand K |
| TLOG(kw) | `atm.TLOG` | torch.Tensor | (n_depth,) | log₁₀(K) |
| TKEV(kw) | `atm.TKEV` | torch.Tensor | (n_depth,) | eV |
| HKT(kw) | `atm.HKT` | torch.Tensor | (n_depth,) | h·k_B·T/c (CGS) |
| HCKT(kw) | `atm.HCKT` | torch.Tensor | (n_depth,) | h·c/k_B/T (CGS) |
| ITEMP | `atm.ITEMP` | int | scalar | iteration index |

### /STATE/ - Pressure and Density Structure
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| P(kw) | `atm.P` | torch.Tensor | (n_depth,) | dyne/cm² |
| XNE(kw) | `atm.XNE` | torch.Tensor | (n_depth,) | cm⁻³ |
| XNATOM(kw) | `atm.XNATOM` | torch.Tensor | (n_depth,) | cm⁻³ |
| RHO(kw) | `atm.RHO` | torch.Tensor | (n_depth,) | g/cm³ |
| PTOTAL(kw) | `atm.PTOTAL` | torch.Tensor | (n_depth,) | dyne/cm² |

### /RAD/ & /ABROSS/ - Radiation and Opacity
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| PRAD(kw) | `atm.PRAD` | torch.Tensor | (n_depth,) | dyne/cm² |
| ACCRAD(kw) | `atm.ACCRAD` | torch.Tensor | (n_depth,) | dyne/cm² |
| ABROSS(kw) | `atm.ABROSS` | torch.Tensor | (n_depth,) | cm⁻¹ |
| TAUROS(kw) | `atm.TAUROS` | torch.Tensor | (n_depth,) | dimensionless |

### /PZERO/ - Pressure Reference and Radiation
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| PZERO | `atm.PZERO` | float | scalar | dyne/cm² |
| PCON | `atm.PCON` | float | scalar | - |
| PRADK0 | `atm.PRADK0` | float | scalar | dyne/cm² |
| PTURB0 | `atm.PTURB0` | float | scalar | dyne/cm² |
| PRADK(kw) | `atm.PRADK` | torch.Tensor | (n_depth,) | dyne/cm² |
| KNU(kw) | `atm.KNU` | torch.Tensor | (n_depth,) | cm⁻¹ |
| EDENS(kw) | `atm.EDENS` | torch.Tensor | (n_depth,) | erg/cm³ |

### /FLUX/ - Bolometric Flux
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| FLUX | `atm.FLUX` | float | scalar | erg cm⁻² s⁻¹ |
| FLXERR(kw) | `atm.FLXERR` | torch.Tensor | (n_depth,) | - |
| FLXDRV(kw) | `atm.FLXDRV` | torch.Tensor | (n_depth,) | - |
| FLXRAD(kw) | `atm.FLXRAD` | torch.Tensor | (n_depth,) | - |

### /ELEM/ & /XABUND/ - Elemental Abundances
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| ABUND(99) | `atm.ABUND` | torch.Tensor | (99,) | log(N/N_H) |
| ATMASS(99) | `atm.ATMASS` | torch.Tensor | (99,) | amu |
| XABUND(99) | `atm.XABUND` | torch.Tensor | (99,) | number fraction |
| WTMOLE | `atm.WTMOLE` | float | scalar | g/mol |

### /TURBPR/ - Turbulence
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| VTURB(kw) | `atm.VTURB` | torch.Tensor | (n_depth,) | km/s |
| PTURB(kw) | `atm.PTURB` | torch.Tensor | (n_depth,) | dyne/cm² |
| TRBFDG | `atm.TRBFDG` | float | scalar | fudge factor |
| TRBCON | `atm.TRBCON` | float | scalar | correction |
| TRBPOW | `atm.TRBPOW` | float | scalar | exponent |
| TRBSND | `atm.TRBSND` | float | scalar | sound velocity |
| IFTURB | `atm.IFTURB` | int | scalar | 0=off, 1=on |

### /CONV/ - Convection
| Fortran | Python | Type | Shape | Units |
|---------|--------|------|-------|-------|
| DLTDLP(kw) | `atm.DLTDLP` | torch.Tensor | (n_depth,) | d(ln T)/d(ln P) |
| HEATCP(kw) | `atm.HEATCP` | torch.Tensor | (n_depth,) | heat capacity |
| DLRDLT(kw) | `atm.DLRDLT` | torch.Tensor | (n_depth,) | d(ln ρ)/d(ln T) |
| VELSND(kw) | `atm.VELSND` | torch.Tensor | (n_depth,) | cm/s |
| GRDADB(kw) | `atm.GRDADB` | torch.Tensor | (n_depth,) | ∇ - ∇_ad |
| HSCALE(kw) | `atm.HSCALE` | torch.Tensor | (n_depth,) | cm |
| FLXCNV(kw) | `atm.FLXCNV` | torch.Tensor | (n_depth,) | flux |
| VCONV(kw) | `atm.VCONV` | torch.Tensor | (n_depth,) | cm/s |
| MIXLTH | `atm.MIXLTH` | float | scalar | mixing length |
| IFCONV | `atm.IFCONV` | int | scalar | 0=off, 1=on |

### /IF/ - Opacity Control Flags
| Fortran | Python | Type | Shape | Description |
|---------|--------|------|-------|-------------|
| IFCORR | `atm.IFCORR` | int | scalar | correction flag |
| IFPRES | `atm.IFPRES` | int | scalar | pressure flag |
| IFSURF | `atm.IFSURF` | int | scalar | surface flag |
| IFSCAT | `atm.IFSCAT` | int | scalar | scattering flag |
| IFMOL | `atm.IFMOL` | int | scalar | molecular opacities |
| NLTEON | `atm.NLTEON` | int | scalar | non-LTE flag |
| IFOP(20) | `atm.IFOP` | torch.Tensor | (20,) | opacity type flags |

## Usage Examples

### Creating an Atmosphere with Fortran variable names:
```python
from kurucz.atmosphere import Atmosphere
import torch

atm = Atmosphere(
    TEFF=5777,           # Solar effective temperature
    GRAV=2.74e4,         # Solar gravity (10^4.44 cm/s²)
    RHOX=torch.logspace(-6, 2, 72),
    NRHOX=72,
    T=torch.linspace(3000, 9000, 72),
    P=torch.ones(72) * 1e6,
    XNE=torch.ones(72) * 1e12,
    # ... other fields
)

print(f"Effective Temperature: {atm.TEFF} K")
print(f"Surface Gravity: {atm.GRAV} cm/s^2")
print(f"Temperature Profile Min/Max: {atm.T.min():.0f} - {atm.T.max():.0f} K")
```

### Accessing fields:
```python
# All access patterns are direct and use UPPERCASE names
temperature = atm.T          # Temperature array
pressure = atm.P             # Pressure array
turbulence = atm.VTURB       # Turbulence velocity
convection_on = atm.IFCONV   # Convection flag
opacity_flag = atm.IFMOL     # Molecular opacity flag
```

## Benefits of Exact Fortran Names

✓ **Direct correlation** with ATLAS code documentation and papers
✓ **Easier debugging** when comparing Python and Fortran outputs
✓ **Reduced confusion** when working across both languages
✓ **Consistent naming** throughout the project
✓ **Better maintainability** for future developers familiar with ATLAS

## Notes

- All variable names are UPPERCASE following Fortran convention
- Fortran array dimensions `(kw)` become PyTorch tensor dimensions `(n_depth,)` where `kw=99` typically
- Comments preserve units and physical meaning from Fortran code
- The `__post_init__()` method automatically derives temperature in multiple units from primary `T` array
