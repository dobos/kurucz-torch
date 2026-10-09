"""
Card Reader Module for ATLAS Input Decks

Provides utilities for parsing ATLAS "card deck" input files, which use
80-character fixed-format lines with keywords and parameters.

This module handles:
- Extracting keywords from card lines
- Parsing floating-point numbers in Fortran format (1.0e+02, 5777.0, etc.)
- Reading multiple lines of float arrays
- Converting to Python lists and torch.Tensor objects
"""

import re
from typing import List, Tuple, Optional, Union, TextIO

# Lazy import torch only when needed (to avoid hanging on slow systems)
torch = None

def _ensure_torch():
    global torch
    if torch is None:
        import torch
    return torch


class CardReader:
    """Parser for ATLAS input card files.
    
    ATLAS input files use 80-character "cards" (lines) with keywords
    followed by parameters. This class handles:
    - Reading lines sequentially
    - Extracting keywords (typically first 6-10 characters)
    - Parsing parameters (floating-point, integers, strings)
    - Handling multi-line arrays
    
    Typical usage:
        reader = CardReader("model.txt")
        keyword = reader.extract_keyword()  # e.g., "TEFF"
        value = reader.parse_float()        # e.g., 5777.0
        
        reader = CardReader("model.txt")
        values = reader.read_float_array(72)  # Read 72 floats
    """
    
    def __init__(self, filepath: Union[str, TextIO]):
        """Initialize CardReader.
        
        Args:
            filepath: Path to input file (str) or file object (TextIO)
        """
        if isinstance(filepath, str):
            self.file = open(filepath, 'r')
            self.should_close = True
        else:
            self.file = filepath
            self.should_close = False
        
        self.current_line = None
        self.line_number = 0
        self.position = 0  # Column position in current line for parsing
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the input file if we opened it."""
        if self.should_close and self.file:
            self.file.close()
    
    def next_line(self) -> Optional[str]:
        """Read the next line from the file.
        
        Returns:
            The next line (without trailing newline), or None at EOF
        """
        line = self.file.readline()
        if not line:
            return None
        
        self.line_number += 1
        self.current_line = line.rstrip('\n')
        self.position = 0
        return self.current_line
    
    def peek_line(self) -> Optional[str]:
        """Peek at the next line without consuming it.
        
        Returns:
            The next line without removing it from the stream
        """
        # This is not ideal for file objects; we'd need to buffer
        # For now, we recommend reading the line and using peek_keyword
        # This is a placeholder
        return None
    
    def extract_keyword(self, line: Optional[str] = None) -> str:
        """Extract the keyword from a card line.
        
        ATLAS keywords are typically 4-12 characters, followed by whitespace.
        Examples: "TEFF", "GRAVITY", "CHANGE RHOX", "READ T"
        
        Only keywords at the start of a line (with minimal leading whitespace)
        are recognized. Lines starting with multiple spaces followed by numbers
        are data lines, not keyword lines.
        
        Args:
            line: Line to parse (uses self.current_line if not provided)
        
        Returns:
            The keyword as a string (uppercase), or empty string if not a keyword line
        """
        if line is None:
            line = self.current_line
        
        if not line:
            return ""
        
        # If line starts with lots of whitespace, it's a data line, not a keyword
        if len(line) > 0 and line[0] in ' \t':
            return ""
        
        # Remove leading whitespace (should be minimal for keywords)
        stripped = line.lstrip()
        
        if not stripped:
            return ""
        
        # Match: one or more word chars or spaces, but stop at digit
        # But first check: if line starts with digit/minus, it's data not keyword
        if stripped[0].isdigit() or stripped[0] == '-':
            return ""
        
        match = re.match(r'^([A-Z][A-Z0-9\s]*?)(?=\s\s|[0-9\-]|$)', stripped, re.IGNORECASE)
        
        if match:
            keyword = match.group(1).strip().upper()
            return keyword
        
        # Fallback: just take first word
        words = stripped.split()
        return words[0].upper() if words else ""
    
    def parse_float(self, line: Optional[str] = None, start_pos: int = 0) -> Optional[float]:
        """Parse a floating-point number from a line.
        
        Handles Fortran-style floats:
        - 5777.0, 5777, 5.777e+3, 5.777E3, 1.0e-10, -2.5E-3
        - Also handles empty fields or "0" as 0.0
        
        Args:
            line: Line to parse (uses self.current_line if not provided)
            start_pos: Position in line to start parsing (default 0)
        
        Returns:
            Parsed float value, or None if parsing fails
        """
        if line is None:
            line = self.current_line
        
        if not line or start_pos >= len(line):
            return None
        
        # Extract substring starting at start_pos
        substring = line[start_pos:].lstrip()
        
        if not substring:
            return None
        
        # Match floating-point pattern (including scientific notation)
        # Pattern: [-+]? optional sign
        #          \d* optional leading digits
        #          \.? optional decimal point
        #          \d* optional trailing digits
        #          ([eE][-+]?\d+)? optional exponent
        match = re.match(r'^[-+]?(\d+\.?\d*|\d*\.\d+)([eE][-+]?\d+)?', substring)
        
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
        
        return None
    
    def parse_int(self, line: Optional[str] = None, start_pos: int = 0) -> Optional[int]:
        """Parse an integer from a line.
        
        Args:
            line: Line to parse (uses self.current_line if not provided)
            start_pos: Position in line to start parsing
        
        Returns:
            Parsed integer, or None if parsing fails
        """
        if line is None:
            line = self.current_line
        
        if not line or start_pos >= len(line):
            return None
        
        substring = line[start_pos:].lstrip()
        
        if not substring:
            return None
        
        match = re.match(r'^[-+]?\d+', substring)
        
        if match:
            try:
                return int(match.group(0))
            except ValueError:
                return None
        
        return None
    
    def read_float_array(self, n_values: int, values_per_line: Optional[int] = None) -> List[float]:
        """Read an array of N floating-point values from multiple lines.
        
        Handles arrays spread across multiple lines, with typical Fortran
        formatting (5 values per line, but this can vary).
        
        Args:
            n_values: Number of floats to read
            values_per_line: Expected values per line (auto-detect if None)
                           Typically 5 for standard Fortran format
        
        Returns:
            List of n_values floats
            
        Raises:
            ValueError: If unable to read the requested number of values
        """
        values = []
        lines_read = 0
        max_lines = (n_values + 4) // 5 + 2  # Upper bound on lines needed
        
        while len(values) < n_values and lines_read < max_lines:
            line = self.next_line()
            
            if line is None:
                break  # EOF
            
            # Skip empty lines and lines that look like keywords
            if not line.strip() or self.extract_keyword(line):
                # This might be the next keyword, so we need to be careful
                # For now, if it looks like a keyword, stop
                if self.extract_keyword(line):
                    # We encountered a keyword, stop reading
                    break
                else:
                    continue
            
            # Parse floats from this line using regex to find all floats
            float_pattern = r'[-+]?(\d+\.?\d*|\d*\.\d+)([eE][-+]?\d+)?'
            matches = re.finditer(float_pattern, line)
            
            for match in matches:
                if len(values) < n_values:
                    try:
                        value = float(match.group(0))
                        values.append(value)
                    except ValueError:
                        pass
            
            lines_read += 1
        
        if len(values) < n_values:
            raise ValueError(f"Could not read {n_values} values; got {len(values)}")
        
        return values[:n_values]
    
    def skip_lines(self, n: int = 1):
        """Skip the next n lines.
        
        Args:
            n: Number of lines to skip
        """
        for _ in range(n):
            if self.next_line() is None:
                break
    
    def read_until_keyword(self, keyword: str) -> List[str]:
        """Read lines until a specific keyword is encountered.
        
        Args:
            keyword: Keyword to search for (case-insensitive)
        
        Returns:
            List of lines read before the keyword (not including the keyword line)
        """
        lines = []
        keyword_upper = keyword.upper()
        
        while True:
            line = self.next_line()
            
            if line is None:
                break
            
            extracted_kw = self.extract_keyword(line)
            if extracted_kw == keyword_upper:
                break
            
            lines.append(line)
        
        return lines


def parse_float_safe(text: str) -> Optional[float]:
    """Standalone utility to parse a float from a string.
    
    Handles various formats:
    - 5777.0, 5777, 5.777e+3, -2.5E-3, 1.0e-10
    
    Args:
        text: String to parse
    
    Returns:
        Parsed float, or None if parsing fails
    """
    if not text or not text.strip():
        return None
    
    text = text.strip()
    
    match = re.match(r'^[-+]?(\d+\.?\d*|\d*\.\d+)([eE][-+]?\d+)?$', text)
    
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    
    return None


def extract_keyword_from_line(line: str) -> str:
    """Standalone utility to extract keyword from a line.
    
    Args:
        line: Card line to parse
    
    Returns:
        Keyword (uppercase), or empty string if no keyword found
    """
    if not line:
        return ""
    
    stripped = line.lstrip()
    
    if not stripped:
        return ""
    
    # Match: letters and spaces, but stop at digit or lots of spaces
    match = re.match(r'^([A-Z][A-Z0-9\s]*?)(?=\s\s|[0-9\-]|$)', stripped, re.IGNORECASE)
    
    if match:
        keyword = match.group(1).strip().upper()
        return keyword
    
    # Fallback: take first word
    words = stripped.split()
    return words[0].upper() if words else ""
