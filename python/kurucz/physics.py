"""
Physics Calculations for Stellar Atmosphere Models

This module provides physics-based calculations used by the Atmosphere class.
All calculations use numpy for numerical operations to avoid dependency on math module.
"""

import numpy as np
from typing import Optional


class Physics:
    """Static physics calculations for stellar atmosphere models.
    
    Contains true physics calculations. Data manipulation and simple math
    operations are handled elsewhere.
    
    Fortran references:
    - atlas7v.for: Main ATLAS stellar atmosphere code
    """
    
    @staticmethod
    def stefan_boltzmann(teff: float) -> Optional[float]:
        """Compute bolometric flux from effective temperature.
        
        Uses Stefan-Boltzmann law: F = σ * T^4, but in the form used by ATLAS:
        FLUX = 5.6697e-5 / 12.5664 * TEFF^4
        
        Where 5.6697e-5 is Stefan-Boltzmann constant in CGS units and
        12.5664 ≈ 4π (geometric factor for spherical star).
        
        Args:
            teff: Effective temperature [K]
        
        Returns:
            Bolometric flux [erg cm^-2 s^-1], or None if input invalid
        
        References:
            Fortran (atlas7v.for line 100): FLUX=5.6697D-5/12.5664*TEFF**4
        """
        if teff is None or teff <= 0:
            return None
        
        return float(5.6697e-5 / 12.5664 * np.power(teff, 4.0))

