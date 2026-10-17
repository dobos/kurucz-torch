from ..fortran.binaryfile import BinaryFile
from .fileio import BaseFileIO
from .spectrumparameters import SpectrumParameters


class SpectrumParametersReader(BaseFileIO):
    """
    Reader for the first record of file 9 (fort.9).

    File 9 is written as an unformatted Fortran sequential binary file in SYNTHE,
    so each record contains a leading and trailing record-length marker.

    This reader intentionally stops after the first record:
    READ(9) WLBEG, RESOLU, WLEND, LENGTH, N, LINOUT, TURBV, IFVAC
    """

    def read_spectrum_parameters(self):
        """
        Read spectrum synthesis parameters from file 9.

        Returns:
            SpectrumParameters: Object containing the first-record parameters.
        """

        handle = self._open_file("rb")
        binary_file = BinaryFile(handle)

        # spectrv.patched.for:223
        binary_file.start_record()
        parameters = SpectrumParameters(
            WLBEG=binary_file.read_double(),
            RESOLU=binary_file.read_double(),
            WLEND=binary_file.read_double(),
            LENGTH=binary_file.read_int(),
            N=binary_file.read_int(),
            LINOUT=binary_file.read_int(),
            TURBV=binary_file.read_float(),
            IFVAC=binary_file.read_int(),
        )
        binary_file.end_record()

        return parameters
