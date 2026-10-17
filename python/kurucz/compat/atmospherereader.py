import io

import torch

from kurucz.atmosphere import Atmosphere
from kurucz.fortran.formattedfile import FormattedFile
from .fileio import BaseFileIO


class AtmosphereReader(BaseFileIO):
    
    def read_atmosphere(self):
        """
        Method to read atmosphere from file.
        """
        # Open file lazily
        # TODO: this must be a text file
        handle = self._open_file('r')

        # lines = [line.rstrip("\n") for line in handle]

        with FormattedFile(handle) as f:

            # def read_line(format_string, text):
            #     return FormattedFile(io.StringIO(text)).read(format_string)

            # def read_formatted_line(format_string, text):
            #     return FormattedFile(io.StringIO(text)).read_formatted(format_string)

            # Skip the initial SURFACE FLUX line
            f.read("12HSURFACE FLUX")

            # Read the iterations line
            numits, ifprnt, ifpnch = f.read("11HITERATIONS ,I1,7H PRINT ,I1,7H PUNCH ,I1")
            
            # Read correction line
            ifcorr = f.read("11HCORRECTION ,A3")[0]
            
            # Read pressure line
            ifpres = f.read("9HPRESSURE ,A3")[0]
            
            # Skip the "READ MOLECULES" line
            f.read("14HREAD MOLECULES")
            
            # Read molecules line
            ifmol = f.read("10HMOLECULES ,A2")[0]

            # Read TEFF, GRAVITY, and title line
            teff, glog, wlte = f.read("5HTEFF ,F7.0,9H  GRAVITY,F8.5,1X,A4")
            
            # Read title line
            title_chars = f.read("6HTITLE ,74A1")[0]
            title = "".join(title_chars)
            
            # Read opacity line
            ifop = f.read("13H OPACITY IFOP20I2")[0]
            
            # Read convection line
            ifconv_text, mixlth, ifturb_text, turb_values = f.read(
                "12H CONVECTION A3,F6.2,12H TURBULENCE A3,4F6.2"
            )
            trbfdg, trbpow, trbsnd, trbcon = turb_values
            
            # Read abundance scale and change line
            xscale, abundance_pairs_12 = f.read(
                "16HABUNDANCE SCALE ,F9.5,17H ABUNDANCE CHANGE,2(I2,F8.5)"
            )
            
            # Process abundance pairs
            abundance_pairs = {int(index): float(value) for index, value in abundance_pairs_12}
            while len(abundance_pairs) < 99:
                # Read abundance change values using read_formatted for the complex
                # repeated format that has issues with read() due to parsing bugs.
                # The final partial record may end with a dangling scalar because the
                # reader treats the missing trailing field as zero; ignore the final
                # unmatched item so we only process complete (index, value) pairs.
                abundance_change_values = f.read_formatted("17H ABUNDANCE CHANGE,6(I3,F7.2)")
                if not abundance_change_values:
                    break
                if len(abundance_change_values) % 2 != 0:
                    abundance_change_values = abundance_change_values[:-1]
                # Process pairs from the flat list of values
                for i in range(0, len(abundance_change_values), 2):
                    abundance_index = int(abundance_change_values[i])
                    abundance_value = float(abundance_change_values[i + 1])
                    abundance_pairs[abundance_index] = abundance_value

            abundances = [abundance_pairs[index] for index in range(1, 100)]

            # Read deck line
            nrhox = f.read("10HREAD DECK6,I3")[0]

            # Read atmospheric data
            rhox = []
            temperature = []
            pressure = []
            xne = []
            abross = []
            accrad = []
            vturb = []
            flxrad = []
            vconv = []
            velsnd = []
            for _ in range(nrhox):
                row = f.read("1PE15.8,0PF9.1,1P8E10.3")
                rhox.append(float(row[0]))
                temperature.append(float(row[1]))
                pressure.append(float(row[2][0]))
                xne.append(float(row[2][1]))
                abross.append(float(row[2][2]))
                accrad.append(float(row[2][3]))
                vturb.append(float(row[2][4]))
                flxrad.append(float(row[2][5]))
                vconv.append(float(row[2][6]))
                velsnd.append(float(row[2][7]))

            # Read PRADK line
            pradk0 = f.read("5HPRADK,1PE11.4")[0]
            
            # Read iteration line
            iteration = f.read("5HBEGIN,20X10HITERATION ,I3,10H COMPLETED")[0]

            return Atmosphere(
                TEFF=torch.tensor(float(teff), dtype=torch.float64),
                GLOG=torch.tensor(float(glog), dtype=torch.float64),
                WLTE=wlte,
                TITLE=title,
                IFOP=[int(value) for value in ifop],
                IFCONV=1 if ifconv_text.strip() == "ON" else 0,
                IFTURB=1 if ifturb_text.strip() == "ON" else 0,
                MIXLTH=torch.tensor(float(mixlth), dtype=torch.float64),
                TRBFDG=torch.tensor(float(trbfdg), dtype=torch.float64),
                TRBPOW=torch.tensor(float(trbpow), dtype=torch.float64),
                TRBSND=torch.tensor(float(trbsnd), dtype=torch.float64),
                TRBCON=torch.tensor(float(trbcon), dtype=torch.float64),
                XSCALE=torch.tensor(xscale, dtype=torch.float64),
                ABUND=torch.tensor(abundances, dtype=torch.float64),
                NRHOX=nrhox,
                RHOX=torch.tensor(rhox, dtype=torch.float64),
                T=torch.tensor(temperature, dtype=torch.float64),
                P=torch.tensor(pressure, dtype=torch.float64),
                XNE=torch.tensor(xne, dtype=torch.float64),
                ABROSS=torch.tensor(abross, dtype=torch.float64),
                ACCRAD=torch.tensor(accrad, dtype=torch.float64),
                VTURB=torch.tensor(vturb, dtype=torch.float64),
                FLXRAD=torch.tensor(flxrad, dtype=torch.float64),
                VCONV=torch.tensor(vconv, dtype=torch.float64),
                VELSND=torch.tensor(velsnd, dtype=torch.float64),
                PRADK0=torch.tensor(float(pradk0), dtype=torch.float64),
                ITER=int(iteration),
                NLTEON=0,
                IFWAVE=1,
                NUMITS=int(numits),
                IFPRNT=int(ifprnt),
                IFPNCH=int(ifpnch),
                IFCORR=ifcorr.strip(),
                IFPRES=ifpres.strip(),
                IFMOL=ifmol.strip(),
            )