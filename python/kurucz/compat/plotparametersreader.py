import torch
from dataclasses import dataclass, field
from typing import Optional
from ..fortran.formattedfile import FormattedFile
import io

from .plotparameters import PlotParameters
from .fileio import BaseFileIO


class PlotParameterReader(BaseFileIO):
    """
    Reader for plot parameters from file 25 (fort.25).
    This reads the same format as the original FORTRAN code:
    READ(25,1)RHOXJ,R1,R101,PH1,PC1,PSI1,PRDDOP,PRDPOW
    FORMAT(8F10.5)
    """
    
    def read_plot_parameters(self) -> PlotParameters:
        """
        Read plot parameters from file 25.
        
        Returns:
            PlotParameters: Object containing the plot parameters
        """
        # Create a new instance with the file source to handle it properly
        reader = PlotParameterReader(self._file_source)
        with reader:
            return reader._read_plot_parameters_internal()
    
    def _read_plot_parameters_internal(self) -> PlotParameters:
        """
        Internal method to read plot parameters from file.
        This is called from the context manager.
        """
        # Open file lazily
        handle = self._open_file('r')
        content = handle.read()
            
        # Parse using the same format as FORTRAN: 8F10.5
        formatted_file = FormattedFile(io.StringIO(content))
        values = formatted_file.read("8F10.5")
        
        # FormattedFile.read returns a tuple, extract the first element
        values_list = values[0]
        
        return PlotParameters(
            RHOXJ=float(values_list[0]),
            R1=float(values_list[1]),
            R101=float(values_list[2]),
            PH1=float(values_list[3]),
            PC1=float(values_list[4]),
            PSI1=float(values_list[5]),
            PRDDOP=float(values_list[6]),
            PRDPOW=float(values_list[7])
        )