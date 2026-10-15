import io

import torch

from kurucz.atmosphere import Atmosphere
from kurucz.fortran.formattedfile import FormattedFile


class AtmosphereReader:
    def read_atmosphere(self, filename):
        with open(filename, "r") as handle:
            lines = [line.rstrip("\n") for line in handle]

        def read_line(format_string, text):
            return FormattedFile(io.StringIO(text)).read(format_string)

        def read_formatted_line(format_string, text):
            return FormattedFile(io.StringIO(text)).read_formatted(format_string)

        line_index = 0
        read_line("12HSURFACE FLUX", lines[line_index])
        line_index += 1
        numits, ifprnt, ifpnch = read_line(
            "11HITERATIONS ,I1,7H PRINT ,I1,7H PUNCH ,I1"
            ,
            lines[line_index],
        )
        line_index += 1
        (ifcorr,) = read_line("11HCORRECTION ,A3", lines[line_index])
        line_index += 1
        (ifpres,) = read_line("9HPRESSURE ,A3", lines[line_index])
        line_index += 1
        read_line("14HREAD MOLECULES", lines[line_index])
        line_index += 1
        (ifmol,) = read_line("10HMOLECULES ,A2", lines[line_index])
        line_index += 1

        teff, glog, wlte = read_line("5HTEFF ,F7.0,9H  GRAVITY,F8.5,1X,A4", lines[line_index])
        line_index += 1
        (title_chars,) = read_line("6HTITLE ,74A1", lines[line_index])
        title = "".join(title_chars)
        line_index += 1
        (ifop,) = read_line("13H OPACITY IFOP20I2", lines[line_index])
        line_index += 1
        ifconv_text, mixlth, ifturb_text, turb_values = read_line(
            "12H CONVECTION A3,F6.2,12H TURBULENCE A3,4F6.2",
            lines[line_index],
        )
        trbfdg, trbpow, trbsnd, trbcon = turb_values
        line_index += 1

        xscale, abundance_pairs_12 = read_line(
            "16HABUNDANCE SCALE ,F9.5,17H ABUNDANCE CHANGE,2(I2,F8.5)",
            lines[line_index],
        )
        line_index += 1
        abundance_pairs = {int(index): float(value) for index, value in abundance_pairs_12}
        while len(abundance_pairs) < 99:
            values = read_formatted_line("17H ABUNDANCE CHANGE,6(I3,F7.2)", lines[line_index])
            for pair_index in range(0, len(values), 2):
                abundance_index = int(values[pair_index])
                abundance_value = float(values[pair_index + 1])
                abundance_pairs[abundance_index] = abundance_value
            line_index += 1

        abundances = [abundance_pairs[index] for index in range(1, 100)]

        (nrhox,) = read_line("10HREAD DECK6,I3", lines[line_index])
        line_index += 1

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
            row = read_line("1PE15.8,0PF9.1,1P8E10.3", lines[line_index])
            line_index += 1
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

        (pradk0,) = read_line("5HPRADK,1PE11.4", lines[line_index])
        line_index += 1
        (iteration,) = read_line("5HBEGIN,20X10HITERATION ,I3,10H COMPLETED", lines[line_index])

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