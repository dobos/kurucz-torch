"""Reader for Fortran UNIT 10 continuum opacity files using scipy.io.FortranFile."""

from typing import Union
import torch
from scipy.io import FortranFile
import numpy as np

from ..opacity.continuum import ContinuumOpacity


class ContinuumOpacityReader:
    """
    Reads continuum opacity data from Fortran UNIT 10 binary files.
    
    Uses scipy.io.FortranFile to handle Fortran unformatted binary I/O directly.
    Implements lines 136-172 of spectrv.patched.for.
    
    All data arrays are REAL*8 (float64), matching Fortran specification:
        IMPLICIT REAL*8 (A-H,O-Z)
        DIMENSION FRQEDG(377), WLEDGE(377), CMEDGE(377), CONFRQ(1131)
        REAL*8 CONTABS(3,377,kw), CONTSCAT(3,377,kw)
        REAL*8 QCONTABS(1131), QCONTSCAT(1131)
    
    Example:
        >>> reader = ContinuumOpacityReader()
        >>> cont = reader.read("fort.10", nrhox=72)
    """
    
    def read(self, filepath: Union[str], nrhox: int) -> ContinuumOpacity:
        """Read continuum opacity data from Fortran UNIT 10 file.
        
        Args:
            filepath: Path to UNIT 10 file
            nrhox: Number of atmospheric depths
        
        Returns:
            ContinuumOpacity object with all fields populated
        """
        continuum = ContinuumOpacity(NRHOX=nrhox)
        
        with FortranFile(filepath, 'r') as f:
            # Record 1: Skip model parameters (mixed int/float types, not uniform)
            f.read_record('<u1')
            
            # Record 2: NEDGE (INTEGER*4), then interleaved FRQEDG/WLEDGE/CMEDGE
            # Layout: IN, FRQEDG(1), WLEDGE(1), CMEDGE(1), FRQEDG(2), ..., FRQEDG(IN), WLEDGE(IN), CMEDGE(IN), IDMOL, MOMASS
            # Read as bytes to handle mixed types
            rec_bytes = f.read_record('<u1')
            byte_data = rec_bytes.tobytes()
            
            # Extract NEDGE as INTEGER*4 at offset 0
            nedge = np.frombuffer(byte_data[:4], dtype='<i4')[0]
            continuum.NEDGE = int(nedge)
            
            # Extract REAL*8 arrays starting after the INTEGER*4
            offset = 4
            n_bytes = (len(byte_data[offset:]) // 8) * 8
            rec_array = np.frombuffer(byte_data[offset:offset+n_bytes], dtype='<f8')
            
            # Arrays are interleaved: FRQEDG(1), WLEDGE(1), CMEDGE(1), FRQEDG(2), WLEDGE(2), ...
            # Extract every 3rd element, starting at correct indices
            frqedg_py = rec_array[0::3][:nedge].tolist()
            wledge_py = rec_array[1::3][:nedge].tolist()
            cmedge_py = rec_array[2::3][:nedge].tolist()
            
            continuum.FRQEDG = torch.tensor(frqedg_py, dtype=torch.float64)
            continuum.WLEDGE = torch.tensor(wledge_py, dtype=torch.float64)
            continuum.CMEDGE = torch.tensor(cmedge_py, dtype=torch.float64)
            
            # Record 3: NCON (INTEGER*4), CONFRQ(NCON) (all REAL*8)
            rec_bytes = f.read_record('<u1')
            byte_data = rec_bytes.tobytes()
            
            # Extract NCON as INTEGER*4 at offset 0
            ncon = np.frombuffer(byte_data[:4], dtype='<i4')[0]
            continuum.NCON = int(ncon)
            
            # Extract CONFRQ as REAL*8 starting after the INTEGER*4
            offset = 4
            n_bytes = (len(byte_data[offset:]) // 8) * 8
            rec_array = np.frombuffer(byte_data[offset:offset+n_bytes], dtype='<f8')
            
            # Truncate to expected size (ncon), rest is padding
            rec_array = rec_array[:ncon]
            
            confrq_py = rec_array.tolist()
            continuum.CONFRQ = torch.tensor(confrq_py, dtype=torch.float64)
            
            # Record 4: Skip
            f.read_record('<u1')
            
            # Records 5+: Read NRHOX depth slices (4 records each)
            # Each depth slice: skip, QCONTABS(NCON), QCONTSCAT(NCON), skip
            contabs_py = []  # List of (NEDGE-1, 3) arrays
            contscat_py = []
            n_edges = nedge - 1
            
            for j in range(nrhox):
                # Skip empty record
                f.read_record('<u1')
                
                # Read QCONTABS(NCON) - read as bytes, interpret as float64
                rec_bytes = f.read_record('<u1')
                byte_data = rec_bytes.tobytes()
                n_bytes = (len(byte_data) // 8) * 8
                rec_array = np.frombuffer(byte_data[:n_bytes], dtype='<f8')
                qcontabs = rec_array[:ncon].tolist()  # Truncate to NCON (skip padding)
                
                # Read QCONTSCAT(NCON) - read as bytes, interpret as float64
                rec_bytes = f.read_record('<u1')
                byte_data = rec_bytes.tobytes()
                n_bytes = (len(byte_data) // 8) * 8
                rec_array = np.frombuffer(byte_data[:n_bytes], dtype='<f8')
                qcontscat = rec_array[:ncon].tolist()  # Truncate to NCON (skip padding)
                
                # Skip empty record
                f.read_record('<u1')
                
                # Reorganize QCONTABS/QCONTSCAT from flat NCON array to (NEDGE-1, 3)
                # Fortran original: NU=0; for IEDGE=1 to NEDGE-1: take 3 consecutive values
                contabs_depth = []
                contscat_depth = []
                nu = 0
                for iedge in range(n_edges):
                    contabs_edge = [qcontabs[nu], qcontabs[nu+1], qcontabs[nu+2]]
                    contscat_edge = [qcontscat[nu], qcontscat[nu+1], qcontscat[nu+2]]
                    contabs_depth.append(contabs_edge)
                    contscat_depth.append(contscat_edge)
                    nu += 3
                
                contabs_py.append(contabs_depth)
                contscat_py.append(contscat_depth)
        
        # Convert to tensors: shape (NRHOX, NEDGE-1, 3)
        contabs_np = np.array(contabs_py, dtype=np.float64)
        contscat_np = np.array(contscat_py, dtype=np.float64)
        
        # Transpose to (3, NEDGE-1, NRHOX) for output (Fortran column-major layout)
        contabs_np = np.transpose(contabs_np, (2, 1, 0))
        contscat_np = np.transpose(contscat_np, (2, 1, 0))
        
        continuum.CONTABS = torch.from_numpy(contabs_np)
        continuum.CONTSCAT = torch.from_numpy(contscat_np)
        
        # Compute interpolation coefficients (HALFEDGE, DELEDGE)
        continuum.update()
        
        return continuum

