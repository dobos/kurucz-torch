import torch
from typing import Optional
from .atmosphere import Atmosphere
from .continuumopacity import ContinuumOpacity
from .compat.atmospherereader import AtmosphereReader
from .compat.continuumopacityreader import ContinuumOpacityReader
from .compat.plotparametersreader import PlotParameterReader
from .compat.plotparameters import PlotParameters
from .compat.spectrumparametersreader import SpectrumParametersReader
from .compat.spectrumparameters import SpectrumParameters

class Spectrv:
    """
    Spectrv class to read and process stellar atmosphere data for spectral synthesis.
    Based on the FORTRAN SPECTRV program from ATLAS.
    """

    # TODO:
    # read spectrum parameters from 25
    # read tape 9
    # read tape 10
    # read tape 20 (atmosphere)
    # read tape 20 (lines)
    
    def __init__(self):
        self.atmosphere: Optional[Atmosphere] = None
        self.plot_parameters: Optional[PlotParameters] = None
        self.spectrum_parameters: Optional[SpectrumParameters] = None
        self.continuum_opacity: Optional[ContinuumOpacity] = None

        # Store continuum data (kept for compatibility with older readers/tests)
        self.NEDGE: Optional[int] = None
        self.FRQEDG: Optional[torch.Tensor] = None
        self.WLEDGE: Optional[torch.Tensor] = None
        self.CMEDGE: Optional[torch.Tensor] = None
        self.NCON: Optional[int] = None
        self.CONFRQ: Optional[torch.Tensor] = None
        self.ASYNTH: Optional[torch.Tensor] = None
        self.ASYNTH_DIM: int = 99
        self.NRHOX: Optional[int] = None
        
        # Store other parameters
        self.NMU: Optional[int] = None
        self.ANGLE: Optional[torch.Tensor] = None
        self.IFSURF: Optional[int] = None
        
    def read_atmosphere(self, filename: str) -> Atmosphere:
        """
        Read atmosphere data from a file using the AtmosphereReader.
        This replaces the original READIN(20) call in the FORTRAN code.
        
        The atmosphere file contains stellar atmospheric parameters including:
        - TEFF, GLOG (stellar parameters)
        - NRHOX (number of depth points)
        - RHOX, T, P, XNE, ABROSS, ACCRAD, VTURB, FLXRAD, VCONV, VELSND (atmospheric profiles)
        - Various abundance and physical parameters
        
        Args:
            filename (str): Path to the atmosphere file (typically fort.20)
            
        Returns:
            Atmosphere: An Atmosphere object populated with the atmospheric data
        """
        # The atmosphere data is read from unit 20 in FORTRAN (which is typically the atmosphere file)
        # In the original code, this is done via CALL READIN(20)
        reader = AtmosphereReader(filename)
        self.atmosphere = reader.read_atmosphere()
        return self.atmosphere
    
    def read_plot_parameters(self, filename: str) -> PlotParameters:
        """
        Read plot parameters from file 25 (fort.25).
        
        These parameters control the spectral synthesis plotting behavior:
        - RHOXJ: Depth above which the line source function is J
        - R1, R101: Residual intensity values for plotting
        - PH1, PC1, PSI1: Continuum parameters for source function calculation
        - PRDDOP, PRDPOW: Partial redistribution parameters
        
        Args:
            filename (str): Path to the plot parameters file (typically fort.25)
            
        Returns:
            PlotParameters: Object containing the plot parameters
        """
        reader = PlotParameterReader(filename)
        self.plot_parameters = reader.read_plot_parameters()
        return self.plot_parameters
        
    def read_continuum_data_from_file10(self, filename: str):
        """
        Read continuum data from file 10 (fort.10) which contains:
        NEDGE, FRQEDG, WLEDGE, CMEDGE, NCON, CONFRQ, QCONTABS, QCONTSCAT

        This file contains unformatted binary data for continuum calculations:
        - NEDGE: Number of continuum edges
        - FRQEDG, WLEDGE, CMEDGE: Arrays of continuum edge parameters
        - NCON: Number of continuum frequencies
        - CONFRQ: Array of continuum frequencies
        - QCONTABS, QCONTSCAT: Continuum absorption and scattering data

        Args:
            filename (str): Path to the continuum data file (typically fort.10)
        """
        reader = ContinuumOpacityReader(filename)
        self.continuum_opacity = reader.read_continuum_opacity(include_frequency_grid=True)
        self.NEDGE = self.continuum_opacity.NEDGE
        self.FRQEDG = self.continuum_opacity.FRQEDG
        self.WLEDGE = self.continuum_opacity.WLEDGE
        self.CMEDGE = self.continuum_opacity.CMEDGE
        self.NCON = self.continuum_opacity.NCON
        self.CONFRQ = self.continuum_opacity.CONFRQ
        return self.continuum_opacity

    def read_continuum_opacity_from_file9(self, filename: str) -> ContinuumOpacity:
        """
        Read the opacity-edge table from a file-9 binary stream.

        This method is kept for compatibility with the older API. It only reads the
        edge table and does not try to parse the ASYNTH vectors unless the caller uses
        the underlying ContinuumOpacityReader directly with an explicit nwave.
        """
        reader = ContinuumOpacityReader(filename)
        self.continuum_opacity = reader.read_continuum_edge_data_from_file9()
        self.NEDGE = self.continuum_opacity.NEDGE
        self.FRQEDG = self.continuum_opacity.FRQEDG
        self.WLEDGE = self.continuum_opacity.WLEDGE
        self.CMEDGE = self.continuum_opacity.CMEDGE
        self.ASYNTH = self.continuum_opacity.ASYNTH
        self.ASYNTH_DIM = self.continuum_opacity.ASYNTH.shape[0] if self.continuum_opacity.ASYNTH is not None else 0
        self.NRHOX = self.ASYNTH_DIM
        return self.continuum_opacity
        
    def read_spectrum_data_from_file9(self, filename: str) -> SpectrumParameters:
        """
        Read spectrum parameters from file 9 (fort.9), first record only:
        WLBEG, RESOLU, WLEND, LENGTH, N, LINOUT, TURBV, IFVAC

        The file is an unformatted Fortran sequential binary stream where each
        record is wrapped by record-length markers.
        
        Args:
            filename (str): Path to the spectrum data file (typically fort.9).

        Returns:
            SpectrumParameters: Parameters from the first file-9 record.
        """
        reader = SpectrumParametersReader(filename)
        self.spectrum_parameters = reader.read_spectrum_parameters()
        return self.spectrum_parameters