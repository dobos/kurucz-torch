"""SPECTRV - Stellar spectrum synthesis from continuum and line opacities.

This module mimics the behavior of the original Fortran SPECTRV program.
It reads binary opacity files (fort.10, fort.9) and populates corresponding
data classes for spectrum calculation.

The approach follows the original Fortran code structure:
- SpectrvReader handles all file I/O operations
- Reads Fortran unformatted binary records
- Populates data classes (ContinuumOpacity, etc.) with the read values
"""

from typing import BinaryIO
import struct
import numpy as np
import torch

from .opacities import Opacities
from kurucz.opacity import ContinuumOpacity

class Spectrv:
    """Main interface for SPECTRV spectrum calculation.
    
    Reads continuum and line opacity files using SpectrvReader,
    computes synthetic stellar spectra.
    """
    
    def __init__(self):
        """Initialize SPECTRV with empty opacities."""
        self.opacities = Opacities()
        self.continuum_opacity = None
    
    def read_continuum_opacity(self, filepath: str, device: str = 'cpu') -> ContinuumOpacity:
        """Read continuum opacity from binary file.
        
        Args:
            filepath: Path to fort.10 file
            device: PyTorch device ('cpu' or 'cuda')
        
        Returns:
            ContinuumOpacity instance with populated tensors
        """
        self.continuum_opacity = SpectrvReader.read_continuum_opacity(filepath, device=device)
        return self.continuum_opacity

class SpectrvReader:
    """Reader for SPECTRV binary output files.
    
    Mimics the file I/O behavior of spectrv.patched.for.
    Reads Fortran unformatted binary files and populates data classes.
    """
    
    @staticmethod
    def _read_fortran_record(f: BinaryIO) -> bytes:
        """Read a single Fortran unformatted record.
        
        Fortran unformatted records have 4-byte integer record markers
        at the beginning and end containing the record length in bytes.
        
        Args:
            f: File handle opened in binary mode
        
        Returns:
            Byte data from the record (without length markers)
        
        Raises:
            EOFError: If unexpected end of file
            ValueError: If record length markers don't match
        """
        # Read leading record length marker (4 bytes, little-endian integer)
        marker_bytes = f.read(4)
        if len(marker_bytes) < 4:
            raise EOFError("Unexpected end of file while reading record marker")
        
        record_len = struct.unpack('<i', marker_bytes)[0]
        
        # Read actual data
        data = f.read(record_len)
        if len(data) < record_len:
            raise EOFError(f"Unexpected end of file: expected {record_len} bytes, got {len(data)}")
        
        # Read trailing record length marker (should match leading marker)
        trailing_marker = f.read(4)
        if len(trailing_marker) < 4:
            raise EOFError("Unexpected end of file while reading trailing marker")
        
        trailing_len = struct.unpack('<i', trailing_marker)[0]
        if trailing_len != record_len:
            raise ValueError(f"Record length mismatch: {record_len} != {trailing_len}")
        
        return data
    
    @staticmethod
    def _read_fortran_reals(data: bytes, count: int, dtype: str = 'float64') -> np.ndarray:
        """Read Fortran real numbers from byte data.
        
        Args:
            data: Byte array containing the data
            count: Number of reals to read
            dtype: 'float64' for REAL*8 (default), 'float32' for REAL*4
        
        Returns:
            NumPy array of real numbers
        
        Raises:
            ValueError: If not enough data or unknown dtype
        """
        if dtype == 'float64':
            fmt = f'<{count}d'  # Little-endian double precision
            expected_size = count * 8
        elif dtype == 'float32':
            fmt = f'<{count}f'  # Little-endian single precision
            expected_size = count * 4
        else:
            raise ValueError(f"Unknown dtype: {dtype}")
        
        if len(data) < expected_size:
            raise ValueError(f"Not enough data: expected {expected_size} bytes, got {len(data)}")
        
        return np.array(struct.unpack(fmt, data[:expected_size]))
    
    @staticmethod
    def _read_fortran_integers(data: bytes, count: int) -> np.ndarray:
        """Read Fortran integers from byte data.
        
        Args:
            data: Byte array containing the data
            count: Number of integers to read
        
        Returns:
            NumPy array of integers (dtype: int32)
        
        Raises:
            ValueError: If not enough data
        """
        fmt = f'<{count}i'  # Little-endian 4-byte integers
        expected_size = count * 4
        
        if len(data) < expected_size:
            raise ValueError(f"Not enough data: expected {expected_size} bytes, got {len(data)}")
        
        return np.array(struct.unpack(fmt, data[:expected_size]))
    
    @classmethod
    def read_continuum_opacity(cls, filepath: str, device: str = 'cpu') -> ContinuumOpacity:
        """Read continuum opacity from Fortran binary file (fort.10).
        
        Maps to UNIT 10 read operations in spectrv.patched.for (lines 136-167).
        Reads frequency grids and continuum absorption/scattering coefficients,
        populating a ContinuumOpacity instance.
        
        Args:
            filepath: Path to fort.10 file
            device: PyTorch device ('cpu' or 'cuda')
        
        Returns:
            ContinuumOpacity instance with populated tensors
        
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file format is invalid
        """
        cont = ContinuumOpacity()
        
        with open(filepath, 'rb') as f:
            # Line 137: Empty record (header marker)
            _header = cls._read_fortran_record(f)
            
            # Lines 138-139: Edge frequency grid
            record_data = cls._read_fortran_record(f)
            offset = 0
            
            # Read NEDGE (1 integer)
            nedge_bytes = record_data[offset:offset+4]
            cont.NEDGE = struct.unpack('<i', nedge_bytes)[0]
            offset += 4
            
            # Read arrays: FRQEDG, WLEDGE, CMEDGE (each is NEDGE REAL*8)
            frqedg_data = cls._read_fortran_reals(record_data[offset:], cont.NEDGE, 'float64')
            offset += cont.NEDGE * 8
            
            wledge_data = cls._read_fortran_reals(record_data[offset:], cont.NEDGE, 'float64')
            offset += cont.NEDGE * 8
            
            cmedge_data = cls._read_fortran_reals(record_data[offset:], cont.NEDGE, 'float64')
            
            # Apply absolute value to wavelengths and frequencies (Fortran lines 147-151)
            frqedg_data = np.abs(frqedg_data)
            wledge_data = np.abs(wledge_data)
            cmedge_data = np.abs(cmedge_data)
            
            cont.FRQEDG = torch.from_numpy(frqedg_data).to(device)
            cont.WLEDGE = torch.from_numpy(wledge_data).to(device)
            cont.CMEDGE = torch.from_numpy(cmedge_data).to(device)
            
            # Line 142: Continuum opacity frequencies
            record_data = cls._read_fortran_record(f)
            offset = 0
            
            # Read NCON (1 integer)
            ncon_bytes = record_data[offset:offset+4]
            cont.NCON = struct.unpack('<i', ncon_bytes)[0]
            offset += 4
            
            # Read CONFRQ array (NCON REAL*8)
            confrq_data = cls._read_fortran_reals(record_data[offset:], cont.NCON, 'float64')
            confrq_data = np.abs(confrq_data)
            cont.CONFRQ = torch.from_numpy(confrq_data).to(device)
            
            # Line 149: Empty record
            _sep1 = cls._read_fortran_record(f)
            
            # Lines 152-167: Loop over depths
            # Allocate storage for CONTABS and CONTSCAT
            all_contabs = []
            all_contscat = []
            
            depth_idx = 0
            try:
                while True:
                    # Line 152: Empty record before each depth
                    try:
                        _sep2 = cls._read_fortran_record(f)
                    except EOFError:
                        break
                    
                    # Line 153: QCONTABS (continuum absorption at this depth)
                    record_data = cls._read_fortran_record(f)
                    qcontabs = cls._read_fortran_reals(record_data, cont.NCON, 'float64')
                    
                    # Line 154: QCONTSCAT (continuum scattering at this depth)
                    record_data = cls._read_fortran_record(f)
                    qcontscat = cls._read_fortran_reals(record_data, cont.NCON, 'float64')
                    
                    # Line 155: Empty record after each depth
                    try:
                        _sep3 = cls._read_fortran_record(f)
                    except EOFError:
                        pass
                    
                    # Store absorption and scattering for this depth
                    all_contabs.append(qcontabs)
                    all_contscat.append(qcontscat)
                    depth_idx += 1
                    
            except EOFError:
                pass
            
            cont.NRHOX = depth_idx
            
            # Process absorption/scattering data
            # Read as per-depth arrays, convert to tensors
            if depth_idx > 0 and cont.NCON > 0:
                # Stack arrays: each element is (NCON,) -> result is (NRHOX, NCON)
                contabs_array = np.array(all_contabs)  # (NRHOX, NCON)
                contscat_array = np.array(all_contscat)  # (NRHOX, NCON)
                
                # Apply absolute value for physical validity (ensure non-negative opacities)
                contabs_array = np.abs(contabs_array)
                contscat_array = np.abs(contscat_array)
                
                # Transpose to (NCON, NRHOX) and convert to torch
                contabs_tensor = torch.from_numpy(contabs_array.T).to(device)
                contscat_tensor = torch.from_numpy(contscat_array.T).to(device)
                
                # Store with shape (NCON, NRHOX)
                # Note: Fortran code processes these into (3, NEDGE-1, NRHOX)
                # for absorption/scattering at 3 wavelength offsets per frequency bin
                cont.CONTABS = contabs_tensor
                cont.CONTSCAT = contscat_tensor
        
        return cont
