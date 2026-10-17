import torch
from typing import Optional, Tuple, Union, TextIO, BinaryIO

from ..fortran.binaryfile import BinaryFile
from ..linelist import LineList
from .fileio import BaseFileIO

class LineListReader(BaseFileIO):
    """Reader for line list data from Fortran tape 9."""

    def __init__(self, file_source: Union[str, TextIO, BinaryIO]):
        super().__init__(file_source)

        self.legacy_alinec_length = 99
    
    def read_line_list(
        self,
        nrhox: Optional[int] = 99,
    ) -> LineList:
        """Read line list data from tape 9.
        
        Args:
            nrhox: Number of depth points (default 99)
            
        Returns:
            LineList object containing the line data
        """

        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)
        
        # Read the second record which contains NLINES (the number of lines)
        # The second record contains header data followed by NLINES
        # We'll read the first 4 bytes as an integer to get NLINES
        binary_file.start_record()
        nlines = binary_file.read_int()
        binary_file.skip_record()
        
        # Create empty tensors for all the data
        # LINDAT8I (3 REAL*8): WL, E, EP
        wl_tensor = torch.zeros(nlines, dtype=torch.float64)
        e_tensor = torch.zeros(nlines, dtype=torch.float64)
        ep_tensor = torch.zeros(nlines, dtype=torch.float64)
        
        # Character data (LABEL, LABELP, OTHER1, OTHER2) - 10-character strings
        label_tensor = [''] * nlines
        labelp_tensor = [''] * nlines
        other1_tensor = [''] * nlines
        other2_tensor = [''] * nlines
        
        # LINDAT8II (3 REAL*8): WLVAC, CENTER, CONCEN
        wlvac_tensor = torch.zeros(nlines, dtype=torch.float64)
        center_tensor = torch.zeros(nlines, dtype=torch.float64)
        concen_tensor = torch.zeros(nlines, dtype=torch.float64)
        
        # LINDAT4I (4 REAL*4): NELION, GAMMAR, GAMMAS, GAMMAW
        nelion_tensor = torch.zeros(nlines, dtype=torch.float32)
        gammar_tensor = torch.zeros(nlines, dtype=torch.float32)
        gammas_tensor = torch.zeros(nlines, dtype=torch.float32)
        gammaw_tensor = torch.zeros(nlines, dtype=torch.float32)
        
        # Character data (REF) - 4-character string
        ref_tensor = [''] * nlines
        
        # LINDAT4II (23 REAL*4): NBLO, NBUP, ISO1, X1, ISO2, X2, GFLOG, XJ, XJP, CODE, ELO, GF, GS, GR, GW, DWL, DGFLOG, DGAMMAR, DGAMMAS, DGAMMAW, EXTRA1, EXTRA2, EXTRA3
        nblo_tensor = torch.zeros(nlines, dtype=torch.float32)
        nbup_tensor = torch.zeros(nlines, dtype=torch.float32)
        iso1_tensor = torch.zeros(nlines, dtype=torch.float32)
        x1_tensor = torch.zeros(nlines, dtype=torch.float32)
        iso2_tensor = torch.zeros(nlines, dtype=torch.float32)
        x2_tensor = torch.zeros(nlines, dtype=torch.float32)
        gflog_tensor = torch.zeros(nlines, dtype=torch.float32)
        xj_tensor = torch.zeros(nlines, dtype=torch.float32)
        xjp_tensor = torch.zeros(nlines, dtype=torch.float32)
        code_tensor = torch.zeros(nlines, dtype=torch.float32)
        elo_tensor = torch.zeros(nlines, dtype=torch.float32)
        gf_tensor = torch.zeros(nlines, dtype=torch.float32)
        gs_tensor = torch.zeros(nlines, dtype=torch.float32)
        gr_tensor = torch.zeros(nlines, dtype=torch.float32)
        gw_tensor = torch.zeros(nlines, dtype=torch.float32)
        dwl_tensor = torch.zeros(nlines, dtype=torch.float32)
        dgflog_tensor = torch.zeros(nlines, dtype=torch.float32)
        dgammar_tensor = torch.zeros(nlines, dtype=torch.float32)
        dgammas_tensor = torch.zeros(nlines, dtype=torch.float32)
        dgammaw_tensor = torch.zeros(nlines, dtype=torch.float32)
        extra1_tensor = torch.zeros(nlines, dtype=torch.float32)
        extra2_tensor = torch.zeros(nlines, dtype=torch.float32)
        extra3_tensor = torch.zeros(nlines, dtype=torch.float32)
        
        # ALINEC array (99 elements) - REAL*4
        alinec_tensor = torch.zeros((nlines, nrhox), dtype=torch.float32)
        
        # Read each line record by reading data items one by one
        for i in range(nlines):
            # Read LINDAT8I (3 REAL*8) - 3 doubles
            wl_tensor[i] = binary_file.read_double()
            e_tensor[i] = binary_file.read_double()
            ep_tensor[i] = binary_file.read_double()
            
            # Read character data (10 chars each) - 40 bytes
            label_tensor[i] = binary_file.read_string(10)
            labelp_tensor[i] = binary_file.read_string(10)
            other1_tensor[i] = binary_file.read_string(10)
            other2_tensor[i] = binary_file.read_string(10)
            
            # Read LINDAT8II (3 REAL*8) - 3 doubles
            wlvac_tensor[i] = binary_file.read_double()
            center_tensor[i] = binary_file.read_double()
            concen_tensor[i] = binary_file.read_double()
            
            # Read LINDAT4I (4 REAL*4) - 4 floats
            nelion_tensor[i] = binary_file.read_float()
            gammar_tensor[i] = binary_file.read_float()
            gammas_tensor[i] = binary_file.read_float()
            gammaw_tensor[i] = binary_file.read_float()
            
            # Read character data (4 chars) - 4 bytes
            ref_tensor[i] = binary_file.read_string(4)
            
            # Read LINDAT4II (23 REAL*4) - 23 floats
            nblo_tensor[i] = binary_file.read_float()
            nbup_tensor[i] = binary_file.read_float()
            iso1_tensor[i] = binary_file.read_float()
            x1_tensor[i] = binary_file.read_float()
            iso2_tensor[i] = binary_file.read_float()
            x2_tensor[i] = binary_file.read_float()
            gflog_tensor[i] = binary_file.read_float()
            xj_tensor[i] = binary_file.read_float()
            xjp_tensor[i] = binary_file.read_float()
            code_tensor[i] = binary_file.read_float()
            elo_tensor[i] = binary_file.read_float()
            gf_tensor[i] = binary_file.read_float()
            gs_tensor[i] = binary_file.read_float()
            gr_tensor[i] = binary_file.read_float()
            gw_tensor[i] = binary_file.read_float()
            dwl_tensor[i] = binary_file.read_float()
            dgflog_tensor[i] = binary_file.read_float()
            dgammar_tensor[i] = binary_file.read_float()
            dgammas_tensor[i] = binary_file.read_float()
            dgammaw_tensor[i] = binary_file.read_float()
            extra1_tensor[i] = binary_file.read_float()
            extra2_tensor[i] = binary_file.read_float()
            extra3_tensor[i] = binary_file.read_float()
            
            # Read ALINEC array (99 REAL*4) - 99 floats
            for j in range(nrhox):
                alinec_tensor[i, j] = binary_file.read_float()
            
        # Create and return the LineList object
        return LineList(
            NLINES=nlines,
            WL=wl_tensor,
            E=e_tensor,
            EP=ep_tensor,
            LABEL=label_tensor,
            LABELP=labelp_tensor,
            OTHER1=other1_tensor,
            OTHER2=other2_tensor,
            WLVAC=wlvac_tensor,
            CENTER=center_tensor,
            CONCEN=concen_tensor,
            NELION=nelion_tensor,
            GAMMAR=gammar_tensor,
            GAMMAS=gammas_tensor,
            GAMMAW=gammaw_tensor,
            REF=ref_tensor,
            NBLO=nblo_tensor,
            NBUP=nbup_tensor,
            ISO1=iso1_tensor,
            X1=x1_tensor,
            ISO2=iso2_tensor,
            X2=x2_tensor,
            GFLOG=gflog_tensor,
            XJ=xj_tensor,
            XJP=xjp_tensor,
            CODE=code_tensor,
            ELO=elo_tensor,
            GF=gf_tensor,
            GS=gs_tensor,
            GR=gr_tensor,
            GW=gw_tensor,
            DWL=dwl_tensor,
            DGFLOG=dgflog_tensor,
            DGAMMAR=dgammar_tensor,
            DGAMMAS=dgammas_tensor,
            DGAMMAW=dgammaw_tensor,
            EXTRA1=extra1_tensor,
            EXTRA2=extra2_tensor,
            EXTRA3=extra3_tensor,
            ALINEC=alinec_tensor
        )