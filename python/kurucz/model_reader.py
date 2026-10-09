"""
ATLAS Model Reader - Main Implementation

This module provides the read_model() method for the Atlas7v class,
implementing Phase 2-5 of the READIN reader:
- Array reading utilities
- Keyword handlers
- Main dispatcher
- Atmosphere object population
"""

# Removed for Python 3.6 compatibility
from typing import Optional, List, Union, TextIO
import math
from .card_reader import CardReader
from .atmosphere import Atmosphere

# Lazy import torch only when needed
# NOTE: On Python 3.6, torch import may hang indefinitely, so we skip it
torch = None
_torch_available = False

def _ensure_torch():
    """Try to ensure torch is available, but don't hang."""
    global torch, _torch_available
    if _torch_available or torch is not None:
        return torch
    
    # Don't try to import torch - it hangs on Python 3.6
    # Just return None and use fallback
    _torch_available = False
    return None

def _make_tensor(values, dtype_name="float64"):
    """Create a tensor, falling back to list if torch unavailable."""
    # For now, always use lists (torch import hangs on Python 3.6)
    return values


class AtlasModelReader:
    """Reads pre-computed ATLAS stellar atmosphere models from card decks."""
    
    def __init__(self):
        """Initialize the model reader."""
        self.current_atm: Optional[Atmosphere] = None
        self.reader: Optional[CardReader] = None
    
    def read_model(self, filepath: Union[str, TextIO]) -> Atmosphere:
        """Read a pre-computed ATLAS stellar atmosphere model.
        
        Reads an ATLAS input card deck and populates an Atmosphere object
        with the model parameters. This is read-only (no computation).
        
        Args:
            filepath: Path to input file (str) or file object (TextIO)
        
        Returns:
            Atmosphere object with parsed model data
        
        Raises:
            ValueError: If required fields are missing or parsing fails
            IOError: If file cannot be read
        """
        self.reader = CardReader(filepath)
        self.current_atm = Atmosphere(TEFF=0.0, GRAV=0.0, RHOX=None)
        
        try:
            # Main reading loop
            while True:
                line = self.reader.next_line()
                
                if line is None:
                    break  # EOF
                
                keyword = self.reader.extract_keyword(line)
                
                if not keyword:
                    continue  # Skip empty/data lines
                
                # Dispatch to appropriate handler
                if keyword == "TEFF":
                    self._handle_teff(line)
                elif keyword == "GRAVITY":
                    self._handle_gravity(line)
                elif keyword == "TITLE":
                    self._handle_title(line)
                elif keyword == "LTE":
                    self._handle_lte(line)
                elif keyword == "NLTE":
                    self._handle_nlte(line)
                elif keyword == "CHANGE RHOX":
                    self._handle_change_rhox()
                elif keyword.startswith("READ"):
                    self._handle_read(line)
                elif keyword == "END":
                    break  # Stop reading this model
                elif keyword in ["MOLECULES", "TURBULENCE", "CONVECTION"]:
                    self._handle_optional_flag(keyword, line)
                # Other keywords are ignored (FREQUENCIES, OPACITY, etc.)
            
            # Validate that essential fields were read
            self._validate_atmosphere()
            
            return self.current_atm
        
        finally:
            if self.reader:
                self.reader.close()
    
    # ========== Keyword Handlers ==========
    
    def _handle_teff(self, line: str):
        """Handle TEFF (Effective Temperature) keyword.
        
        Fortran code (line 100):
            TEFF=FREEFF(CARD)
            FLUX=5.6697D-5/12.5664*TEFF**4
        """
        # Extract value after keyword (find first non-space after "TEFF")
        keyword_end = line.find("TEFF") + len("TEFF")
        value = self.reader.parse_float(line, keyword_end)
        if value is not None:
            self.current_atm.TEFF = value
            # Compute Stefan-Boltzmann flux
            self.current_atm.FLUX = 5.6697e-5 / 12.5664 * value**4
    
    def _handle_gravity(self, line: str):
        """Handle GRAVITY keyword.
        
        Fortran code (line 200):
            GRAV=FREEFF(CARD)
            IF(GRAV.LT.10.)GRAV=EXP10(GRAV)
            GLOG=LOG10(GRAV)
        """
        # Extract value after keyword
        keyword_end = line.find("GRAVITY") + len("GRAVITY")
        value = self.reader.parse_float(line, keyword_end)
        if value is not None:
            # Check if it's in log scale (< 10)
            if value < 10.0:
                value = 10.0 ** value  # Convert from log scale
            
            self.current_atm.GRAV = value
            self.current_atm.GLOG = math.log10(value)
    
    def _handle_title(self, line: str):
        """Handle TITLE keyword.
        
        Fortran code (line 1800-1801):
            DO 1801 I=1,74
              TITLE(I)=CARD(I+6)
        """
        # Read 74 characters starting at position 6 (after "TITLE ")
        if len(line) > 6:
            title = line[6:80].rstrip()  # Pad to 80 total, then strip trailing spaces
            self.current_atm.TITLE = title
    
    def _handle_lte(self, line: str):
        """Handle LTE keyword (Local Thermodynamic Equilibrium).
        
        Fortran code (line 1200):
            NLTEON=0
            WLTE=WWLTE
        """
        self.current_atm.NLTEON = 0
    
    def _handle_nlte(self, line: str):
        """Handle NLTE keyword (Non-Local Thermodynamic Equilibrium).
        
        Fortran code (line 1300):
            NLTEON=1
            WLTE=WWNLTE
        """
        self.current_atm.NLTEON = 1
    
    def _handle_change_rhox(self):
        """Handle CHANGE RHOX keyword (Depth Grid).
        
        Fortran code (line 2100-2101):
            NRHOX=FREEFF(CARD)
            DO 2101 J=1,NRHOX
              RHOX(J)=FREEFF(CARD)
        """
        # Read next line for NRHOX
        line = self.reader.next_line()
        if line is None:
            raise ValueError("EOF while reading NRHOX")
        
        nrhox = self.reader.parse_int(line)
        if nrhox is None or nrhox <= 0:
            raise ValueError(f"Invalid NRHOX: {nrhox}")
        
        self.current_atm.NRHOX = nrhox
        
        # Read RHOX array
        try:
            rhox_values = self.reader.read_float_array(nrhox)
            self.current_atm.RHOX = _make_tensor(rhox_values)
        except ValueError as e:
            raise ValueError(f"Failed to read RHOX array: {e}")
    
    def _handle_read(self, line: str):
        """Handle READ keyword (dispatch to data readers).
        
        Handles: READ T, READ P, READ XNE, READ FREQUENCIES, etc.
        Reads the data from the following lines.
        """
        # Extract what type of data to read from the READ line
        # line is like "READ T" or "READ P" or "READ XNE"
        keyword = self.reader.extract_keyword(line)  # e.g., "READ T"
        
        # Get the data type (T, P, XNE, etc.)
        parts = keyword.split()
        if len(parts) < 2:
            return
        
        data_type = parts[1]  # "T", "P", "XNE", "FREQUENCIES", etc.
        
        if data_type == "T":
            self._read_temperature()
        elif data_type == "P":
            self._read_pressure()
        elif data_type == "XNE":
            self._read_electron_density()
        elif data_type == "FREQUENCIES":
            # Skip frequency data for now
            self._skip_frequencies()
        elif data_type == "COEFFICIENTS":
            # Skip departure coefficients for now
            pass
        else:
            # Unknown subsection, skip
            pass
    
    def _read_temperature(self):
        """Read temperature array from READ T section."""
        if self.current_atm.NRHOX is None or self.current_atm.NRHOX == 0:
            return  # Can't read without knowing NRHOX
        
        try:
            t_values = self.reader.read_float_array(self.current_atm.NRHOX)
            self.current_atm.T = _make_tensor(t_values)
        except ValueError:
            pass  # Silently ignore if we can't read
    
    def _read_pressure(self):
        """Read pressure array from READ P section."""
        if self.current_atm.NRHOX is None or self.current_atm.NRHOX == 0:
            return  # Can't read without knowing NRHOX
        
        try:
            p_values = self.reader.read_float_array(self.current_atm.NRHOX)
            self.current_atm.P = _make_tensor(p_values)
        except ValueError:
            pass
    
    def _read_electron_density(self):
        """Read electron density array from READ XNE section."""
        if self.current_atm.NRHOX is None or self.current_atm.NRHOX == 0:
            return
        
        try:
            xne_values = self.reader.read_float_array(self.current_atm.NRHOX)
            self.current_atm.XNE = _make_tensor(xne_values)
        except ValueError:
            pass
    
    def _skip_frequencies(self):
        """Skip FREQUENCIES section (not needed for reading)."""
        # Skip until we hit another keyword or END
        # For now, just read one line
        self.reader.next_line()
    
    def _handle_optional_flag(self, keyword: str, line: str):
        """Handle optional flag keywords (MOLECULES, TURBULENCE, CONVECTION)."""
        next_line = self.reader.next_line()
        if next_line is None:
            return
        
        next_kw = self.reader.extract_keyword(next_line)
        
        if keyword == "MOLECULES":
            if next_kw == "ON":
                self.current_atm.IFMOL = 1
            elif next_kw == "OFF":
                self.current_atm.IFMOL = 0
        
        elif keyword == "TURBULENCE":
            if next_kw == "ON":
                self.current_atm.IFTURB = 1
            elif next_kw == "OFF":
                self.current_atm.IFTURB = 0
        
        elif keyword == "CONVECTION":
            if next_kw == "ON":
                self.current_atm.IFCONV = 1
            elif next_kw == "OFF":
                self.current_atm.IFCONV = 0
    
    def _validate_atmosphere(self):
        """Validate that essential fields were read."""
        if self.current_atm.TEFF == 0.0:
            raise ValueError("TEFF not read or invalid")
        
        if self.current_atm.GRAV == 0.0:
            raise ValueError("GRAVITY not read or invalid")
        
        if self.current_atm.NRHOX is None or self.current_atm.NRHOX == 0:
            raise ValueError("NRHOX not read or invalid")
        
        if self.current_atm.RHOX is None:
            raise ValueError("RHOX array not read")
        
        if self.current_atm.T is None:
            raise ValueError("Temperature array (T) not read")
        
        if self.current_atm.P is None:
            raise ValueError("Pressure array (P) not read")
        
        if self.current_atm.XNE is None:
            raise ValueError("Electron density array (XNE) not read")
        
        # Verify array shapes (works with both lists and torch tensors)
        def get_array_length(arr):
            if hasattr(arr, 'shape'):
                return arr.shape[0]
            else:
                return len(arr)
        
        rhox_len = get_array_length(self.current_atm.RHOX)
        if rhox_len != self.current_atm.NRHOX:
            raise ValueError(f"RHOX length {rhox_len} != NRHOX {self.current_atm.NRHOX}")
        
        t_len = get_array_length(self.current_atm.T)
        if t_len != self.current_atm.NRHOX:
            raise ValueError(f"T length {t_len} != NRHOX {self.current_atm.NRHOX}")
        
        p_len = get_array_length(self.current_atm.P)
        if p_len != self.current_atm.NRHOX:
            raise ValueError(f"P length {p_len} != NRHOX {self.current_atm.NRHOX}")
        
        xne_len = get_array_length(self.current_atm.XNE)
        if xne_len != self.current_atm.NRHOX:
            raise ValueError(f"XNE length {xne_len} != NRHOX {self.current_atm.NRHOX}")
