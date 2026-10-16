from typing import Optional

import torch

from ..continuumopacity import ContinuumOpacity
from ..fortran.binaryfile import BinaryFile
from .fileio import BaseFileIO


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

    def read_continuum_opacity(
        self,
        include_frequency_grid: bool = False,
        include_asynth: bool = False,
        mode: str = "fort10",
        nrhox: Optional[int] = None,
        nwave: Optional[int] = None,
        read_header: bool = False,
    ) -> ContinuumOpacity:
        handle = self._open_file("rb")

        try:
            legacy_asynth_length = 99

            if mode == "fort9" and read_header:
                header_reader = BinaryFile(handle)
                header_reader.start_record()
                header_reader.read_double()
                header_reader.read_double()
                header_reader.read_double()
                length = header_reader.read_int()
                nrhox = header_reader.read_int()
                header_reader.read_int()
                header_reader.read_float()
                header_reader.read_int()
                header_reader.skip_record()
                if include_asynth and nwave is None:
                    nwave = length

            binary_file = BinaryFile(handle)

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
                    raise ValueError("nwave must be provided when include_asynth=True")

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
        finally:
            self._close_file()


__all__ = [
    "ContinuumOpacityReader",
]
