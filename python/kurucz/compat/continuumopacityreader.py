from typing import Optional, TextIO, BinaryIO, Union

import torch

from ..continuumopacity import ContinuumOpacity
from ..fortran.binaryfile import BinaryFile
from .fileio import BaseFileIO
from .spectrumparametersreader import SpectrumParametersReader


class ContinuumOpacityReader(BaseFileIO):
    """
    Reader for the continuum opacity table.

    For file 9, the edge table typically starts immediately after the spectrum header:
    READ(9) NEDGE, (FRQEDG(IEDGE), WLEDGE(IEDGE), CMEDGE(IEDGE), IEDGE=1, NEDGE)

    For file 10, the same edge table appears after an initial model/header record, and
    the continuum grid is then followed by a second record:
    READ(10) NCON, (CONFRQ(NU), NU=1, NCON)

    Set include_frequency_grid=True to read that optional frequency-grid record.
    Set include_asynth=True to read the ASYNTH vector that follows in tape-9 mode.
    """

    def __init__(self, file_source: Union[str, TextIO, BinaryIO]):
        super().__init__(file_source)

        self.legacy_contabs_length = 1131
        self.legacy_contscat_length = 1131

    def read_continuum_edge_data_from_file9(
        self,
        read_header: bool = False,
    ) -> ContinuumOpacity:
        """Read the opacity-edge record from file 9, optionally skipping a preceding header."""
        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)

        if read_header:
            SpectrumParametersReader(handle).read_spectrum_parameters()

        binary_file.start_record()
        nedge = binary_file.read_int()
        edge_values = binary_file.read_double(3 * nedge)
        binary_file.skip_record()

        frqedg = torch.tensor(edge_values[0::3], dtype=torch.float64)
        wledge = torch.tensor(edge_values[1::3], dtype=torch.float64)
        cmedge = torch.tensor(edge_values[2::3], dtype=torch.float64)

        return ContinuumOpacity(
            NEDGE=nedge,
            FRQEDG=frqedg,
            WLEDGE=wledge,
            CMEDGE=cmedge,
        )

    def read_continuum_edges(
        self,
        continuum_opacity: ContinuumOpacity = None
    ) -> ContinuumOpacity:
        
        """
        Read the continuum opacity edge table from file 9 immediately after the
        spectrum header.

        The FORTRAN routine reads:
        READ(9) NEDGE, (FRQEDG(IEDGE), WLEDGE(IEDGE), CMEDGE(IEDGE), IEDGE=1, NEDGE)
        """

        opacity = self.read_continuum_edge_data_from_file9(read_header=False)
        if continuum_opacity is not None:
            continuum_opacity.NEDGE = opacity.NEDGE
            continuum_opacity.FRQEDG = opacity.FRQEDG
            continuum_opacity.WLEDGE = opacity.WLEDGE
            continuum_opacity.CMEDGE = opacity.CMEDGE
            return continuum_opacity

        return opacity

    def read_continuum_frequencies(
        self,
        continuum_opacity: ContinuumOpacity = None
    ) -> ContinuumOpacity:
        
        """
        Read the continuum frequency grid from file 10.

        The FORTRAN routine reads:
        READ(10) NCON, (CONFRQ(NU), NU=1, NCON)
        """

        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)

        binary_file.start_record()
        ncon = binary_file.read_int()
        confrq = binary_file.read_double(ncon)
        binary_file.skip_record()

        continuum_opacity = continuum_opacity or ContinuumOpacity()

        continuum_opacity.NCON = ncon
        continuum_opacity.CONFRQ = torch.tensor(confrq, dtype=torch.float64)

        return continuum_opacity

    def read_continuum_abs_scat(
        self,
        nrhox: int,
        continuum_opacity: ContinuumOpacity = None
    ) -> ContinuumOpacity:
        
        """
        Read the continuum absorption and scattering from file 10.

        The FORTRAN routine reads:
        READ(10)
        READ(10) QCONTABS
        READ(10) QCONTSCAT
        READ(10)
        """
        
        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)

        qcontabs = []
        qcontscat = []

        for i in range(nrhox):
            # Skip the first record
            binary_file.start_record()
            binary_file.skip_record()

            # Read QCONTABS
            binary_file.start_record()
            qcontabs.append(
                torch.tensor(binary_file.read_double(self.legacy_contabs_length), dtype=torch.float64)
            )
            binary_file.skip_record()

            # Read QCONTSCAT
            binary_file.start_record()
            qcontscat.append(
                torch.tensor(binary_file.read_double(self.legacy_contscat_length), dtype=torch.float64)
            )
            binary_file.skip_record()

            # Skip the last record
            binary_file.start_record()
            binary_file.skip_record()

        continuum_opacity = continuum_opacity or ContinuumOpacity()

        continuum_opacity.QCONTABS = torch.stack(qcontabs)
        continuum_opacity.QCONTSCAT = torch.stack(qcontscat)

        return continuum_opacity

    def read_continuum_opacity(
        self,
        include_frequency_grid: bool = False,
        include_asynth: bool = False,
        mode: str = "fort10",
        nrhox: Optional[int] = None,
        nwave: Optional[int] = None,
        read_header: bool = False,
    ) -> ContinuumOpacity:

        # TODO: everything above?

        handle = self._open_file("rb")

        legacy_asynth_length = 99

        binary_file = BinaryFile(handle)

        # When read_header is True, we're reading from a file that has spectrum parameters
        # at the beginning, followed by the edge data. The header reading is done by
        # SpectrumParametersReader, so we just skip it here.
        if mode == "fort9" and read_header:
            # Skip the header record (spectrum parameters) that was already read
            # by SpectrumParametersReader
            binary_file.start_record()
            # Skip the header data - we don't need to read it since it's already handled
            # by SpectrumParametersReader
            binary_file.skip_record()

        # spectrv.patched.for:224
        binary_file.start_record()
        nedge = binary_file.read_int()
        edge_values = binary_file.read_double(3 * nedge)
        binary_file.skip_record()

        frqedg = torch.tensor(edge_values[0::3], dtype=torch.float64)
        wledge = torch.tensor(edge_values[1::3], dtype=torch.float64)
        cmedge = torch.tensor(edge_values[2::3], dtype=torch.float64)

        opacity = ContinuumOpacity(
            NEDGE=nedge,
            FRQEDG=frqedg,
            WLEDGE=wledge,
            CMEDGE=cmedge,
        )

        if include_frequency_grid:
            binary_file.start_record()
            ncon = binary_file.read_int()
            confrq = binary_file.read_double(ncon)
            binary_file.skip_record()
            opacity.NCON = ncon
            opacity.CONFRQ = torch.tensor(confrq, dtype=torch.float64)

        if include_asynth:
            if nwave is None:
                raise ValueError(
                    "nwave must be provided when include_asynth=True; "
                    "pass the spectrum LENGTH or call read_header=True before reading the edge table."
                )

            # Each ASYNTH row is its own unformatted record. Reading the full row in
            # one bulk call is the important optimization; the outer loop is still
            # required because the file contains multiple independent records, one per
            # wavelength sample.
            asynth_rows = []
            for _ in range(nwave):
                binary_file.start_record()
                row = binary_file.read_float(legacy_asynth_length)
                binary_file.skip_record()
                if nrhox is not None:
                    row = row[:nrhox]
                asynth_rows.append(row)
            opacity.ASYNTH = torch.stack([
                torch.tensor(row, dtype=torch.float32) for row in asynth_rows
            ])

        return opacity

__all__ = [
    "ContinuumOpacityReader",
]
