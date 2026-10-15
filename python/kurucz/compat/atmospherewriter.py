from kurucz.fortran.formattedfile import FormattedFile
from kurucz.atmosphere import Atmosphere


class AtmosphereWriter:
    def write_atmosphere(self, atmosphere: Atmosphere, filename: str) -> None:
        with open(filename, "w") as handle:
            ff = FormattedFile(handle)

            numits = 1 if atmosphere.NUMITS is None else atmosphere.NUMITS
            ifprnt = 2 if atmosphere.IFPRNT is None else atmosphere.IFPRNT
            ifpnch = 2 if atmosphere.IFPNCH is None else atmosphere.IFPNCH
            ifcorr = "OFF" if atmosphere.IFCORR is None else atmosphere.IFCORR
            ifpres = "OFF" if atmosphere.IFPRES is None else atmosphere.IFPRES
            ifmol = "ON" if atmosphere.IFMOL is None else atmosphere.IFMOL

            handle.write("SURFACE FLUX\n")
            handle.write(f"ITERATIONS {numits} PRINT {ifprnt} PUNCH {ifpnch}\n")
            handle.write(f"CORRECTION {ifcorr}\n")
            handle.write(f"PRESSURE {ifpres}\n")
            handle.write("READ MOLECULES\n")
            handle.write(f"MOLECULES {ifmol}\n")

            ifconv = "ON" if atmosphere.IFCONV == 1 else "OFF"
            iftur = "ON" if atmosphere.IFTURB == 1 else "OFF"
            title_chars = list(atmosphere.TITLE.ljust(74)[:74])
            abundances = atmosphere.ABUND.tolist()
            abundance_count = min(99, len(abundances))

            ff.write(
                "5HTEFF ,F7.0,9H  GRAVITY,F8.5,1X,A4/6HTITLE ,74A1"
                "/13H OPACITY IFOP20I2/12H CONVECTION A3,F6.2,12H TURBULENCE A3,"
                "4F6.2/16HABUNDANCE SCALE ,F9.5,17H ABUNDANCE CHANGE,2(I2,F8.5)",
                atmosphere.TEFF.item(),
                atmosphere.GLOG.item(),
                atmosphere.WLTE,
                title_chars,
                atmosphere.IFOP,
                ifconv,
                atmosphere.MIXLTH.item(),
                iftur,
                [
                    atmosphere.TRBFDG.item(),
                    atmosphere.TRBPOW.item(),
                    atmosphere.TRBSND.item(),
                    atmosphere.TRBCON.item(),
                ],
                atmosphere.XSCALE.item(),
                [[1, abundances[0] if abundance_count >= 1 else 0.0], [2, abundances[1] if abundance_count >= 2 else 0.0]],
            )
            handle.write("\n")
            for abundance_index in range(2, abundance_count, 6):
                values = []
                for pair_index in range(min(6, abundance_count - abundance_index)):
                    values.extend([abundance_index + pair_index + 1, abundances[abundance_index + pair_index]])
                ff.write_formatted("17H ABUNDANCE CHANGE,6(I3,F7.2)", values)
                handle.write("\n")

            handle.write(
                f"READ DECK6{atmosphere.NRHOX:3d} RHOX,T,P,XNE,ABROSS,ACCRAD,VTURB,         FLXRAD,VCONV,VELSND\n"
            )
            flxrad = atmosphere.FLXRAD if atmosphere.FLXRAD is not None else [0.0] * atmosphere.NRHOX
            vconv = atmosphere.VCONV if atmosphere.VCONV is not None else [0.0] * atmosphere.NRHOX
            velsnd = atmosphere.VELSND if atmosphere.VELSND is not None else [0.0] * atmosphere.NRHOX
            for row_index in range(atmosphere.NRHOX):
                ff.write_formatted(
                    "1PE15.8,0PF9.1,1P8E10.3",
                    [
                        atmosphere.RHOX[row_index].item(),
                        atmosphere.T[row_index].item(),
                        atmosphere.P[row_index].item(),
                        atmosphere.XNE[row_index].item(),
                        atmosphere.ABROSS[row_index].item(),
                        atmosphere.ACCRAD[row_index].item(),
                        atmosphere.VTURB[row_index].item(),
                        flxrad[row_index].item() if hasattr(flxrad[row_index], "item") else flxrad[row_index],
                        vconv[row_index].item() if hasattr(vconv[row_index], "item") else vconv[row_index],
                        velsnd[row_index].item() if hasattr(velsnd[row_index], "item") else velsnd[row_index],
                    ],
                )
                handle.write("\n")

            ff.write_formatted("5HPRADK1PE11.4", [atmosphere.PRADK0.item()])
            handle.write("\n")
            ff.write_formatted("5HBEGIN,20X10HITERATION I3,10H COMPLETED", [atmosphere.ITER])