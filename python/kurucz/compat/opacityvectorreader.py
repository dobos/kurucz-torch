from typing import Optional
from typing import Union, TextIO, BinaryIO
import torch

from ..fortran.binaryfile import BinaryFile
from ..opacityvectors import OpacityVectors
from .fileio import BaseFileIO


class OpacityVectorReader(BaseFileIO):
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

        self.legacy_asynth_length = 99

    def read_opacity_vectors(
        self,
        nrhox: int,
        nwave: int,
    ) -> OpacityVectors:

        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)

        

        # Each ASYNTH row is its own unformatted record. Reading the full row in
        # one bulk call is the important optimization; the outer loop is still
        # required because the file contains multiple independent records, one per
        # wavelength sample.
        asynth_rows = []
        for _ in range(nwave):
            binary_file.start_record()
            row = binary_file.read_float(self.legacy_asynth_length)
            binary_file.skip_record()
            asynth_rows.append(row[:nrhox])
        
        asynth = torch.stack([
            torch.tensor(row, dtype=torch.float32) for row in asynth_rows
        ])

        return OpacityVectors(
            NRHOX=nrhox,
            NWAVE=nwave,
            ASYNTH=asynth,
        )