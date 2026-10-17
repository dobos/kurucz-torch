import io
from unittest import TestCase

from torch import gt

from kurucz.fortran.formattedfile import FormattedFile


class TestFormattedFile(TestCase):
    def setUp(self):
        self.ff = FormattedFile(io.StringIO())

    def test_parse_repeated_field_groups(self):
        tokens, _ = self.ff._parse_sequence("(2(I3,F5.2))", 0)
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0]["kind"], "I")
        self.assertEqual(tokens[1]["kind"], "F")
        self.assertEqual(tokens[2]["kind"], "I")
        self.assertEqual(tokens[3]["kind"], "F")

    def test_parse_hollerith_literals(self):
        tokens, _ = self.ff._parse_sequence("(5HTEFF ,F7.0,9H  GRAVITY,F8.5)", 0)
        self.assertEqual(tokens[0]["type"], "literal")
        self.assertEqual(tokens[0]["value"], "TEFF ")
        self.assertEqual(tokens[2]["value"], "  GRAVITY")

    def test_read_records_with_repeats_and_hollerith(self):
        stream = io.StringIO("  1  2  3  4\n")
        ff = FormattedFile(stream)
        self.assertEqual(ff.read("(2(I3,I3))"), ([[1, 2], [3, 4]],))

        stream = io.StringIO("TEFF  5770\n")
        ff = FormattedFile(stream)
        self.assertEqual(ff.read("(5HTEFF ,F7.0)"), (5770.0,))

    def test_write_records_with_repeats_and_hollerith(self):
        stream = io.StringIO()
        ff = FormattedFile(stream)
        written = ff.write("(2(I3,I3))", [[1, 2], [3, 4]])
        self.assertEqual(written, "  1  2  3  4")
        self.assertEqual(stream.getvalue(), "  1  2  3  4")

        stream = io.StringIO()
        ff = FormattedFile(stream)
        written = ff.write("(5HTEFF ,F7.0)", (5770.0,))
        self.assertTrue(written.startswith("TEFF"))
        self.assertTrue(written.rstrip().endswith("5770."))

    def test_write_stops_when_repeated_group_exhausts_values(self):
        stream = io.StringIO()
        ff = FormattedFile(stream)
        written = ff.write("(2(I1,1H-))", [1])
        self.assertEqual(written, "1-")
        self.assertEqual(stream.getvalue(), "1-")

    def test_write_reverts_to_last_parenthesized_group(self):
        stream = io.StringIO()
        ff = FormattedFile(stream)
        written = ff.write(
            "2(I1,I1)/(1HQ,2(I1,I1))",
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
            [[9, 0]],
        )
        self.assertEqual(written, "1234\nQ5678\nQ90")
        self.assertEqual(stream.getvalue(), "1234\nQ5678\nQ90")

    def test_read_repeated_format_with_newline(self):
        # Test format with repeated group containing newline tokens
        # This tests 2(I5,/) which should read two integers from two separate lines
        # The result should be grouped as [[12345], [67890]] due to the repeated format
        stream = io.StringIO("12345\n67890\n")
        ff = FormattedFile(stream)
        result = ff.read("2(I5,/)") 
        self.assertEqual(result, ([[12345], [67890]],))

    def _assert_materialized(self, format_string, record_literal, expected_values):
        stream = io.StringIO(record_literal)
        ff = FormattedFile(stream)
        actual = ff.read(format_string)
        
        # Flatten nested list/tuple structure
        def flatten(obj):
            result = []
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    if isinstance(item, (list, tuple)):
                        result.extend(flatten(item))
                    else:
                        result.append(item)
            else:
                result.append(obj)
            return result
        
        actual = flatten(actual)
        self.assertEqual(len(actual), len(expected_values))
        for expected, observed in zip(expected_values, actual):
            if isinstance(expected, float):
                self.assertAlmostEqual(float(observed), float(expected), places=6)
            else:
                self.assertEqual(observed, expected)

    def test_read_materialized_data_for_8f10_5(self):
        self._assert_materialized(
            "(8F10.5)",
            "   1.00000   2.50000   3.75000   4.00000   5.25000   6.50000   7.75000   8.12500",
            [1.0, 2.5, 3.75, 4.0, 5.25, 6.5, 7.75, 8.125],
        )

    def test_read_materialized_data_for_2i10_1p3e12_4(self):
        self._assert_materialized(
            "(2I10, 1P3E12.4)",
            "         7       -12  1.2500E-03 -2.5000E+04  3.5000E+02",
            [7, -12, 1.25e-3, -2.5e4, 3.5e2],
        )

    def test_read_materialized_data_for_wlbeg_record(self):
        self._assert_materialized(
            "(7H WLBEG=,F10.4,10H   RESOLU=,F10.1,9H   WLEND=,F10.4,10H   LENGTH=,I7,9H   NRHOX=,I2)",
            " WLBEG=   12.5000   RESOLU=       4.0   WLEND=   99.0000   LENGTH=    123   NRHOX= 8",
            [12.5, 4.0, 99.0, 123, 8],
        )

    def test_read_materialized_data_for_i10_3f13_4(self):
        self._assert_materialized(
            "(I10,3F13.4)",
            "        42       1.2340       2.3450       3.4560",
            [42, 1.234, 2.345, 3.456],
        )

    def test_read_materialized_data_for_surface_flux(self):
        self._assert_materialized("(13H SURFACE FLUX)", " SURFACE FLUX", [])

    def test_read_materialized_data_for_surface_intensity(self):
        self._assert_materialized(
            "(18H SURFACE INTENSITY,I3/20F6.3)",
            " SURFACE INTENSITY  5\n 0.100 0.200 0.300 0.400 0.500 0.600 0.700 0.800 0.900 1.000 1.100 1.200 1.300 1.400 1.500 1.600 1.700 1.800 1.900 2.000",
            [5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
        )

    def test_read_materialized_data_for_1h1(self):
        self._assert_materialized("(1H1)", "1", [])

    def test_read_materialized_data_for_1h_space_i5_f11_4_i7_101a1(self):
        self._assert_materialized(
            "(1H ,I5,F11.4,I7,101A1)",
            "    42     1.2345     67XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            [42, 1.2345, 67] + ['X'] * 101,
        )

    def test_read_materialized_data_for_3i10(self):
        self._assert_materialized("(3I10)", "         1         2         3", [1, 2, 3])

    def test_read_materialized_data_for_1h0_complex(self):
        self._assert_materialized(
            "(1H0,F10.4,F7.3,F5.1,F12.3,F5.1,F12.3,F9.2,1X,A10,A10,F12.4,F9.3,1P2E11.3/1X,0PF10.4,I4,F6.2,F6.2,F6.2,A4,I2,I2,I3,F7.3,I3,F7.3,A10,A10,F7.4,F7.3,3F6.2)",
            "0    1.2345  2.345  3.5       4.567  5.7       6.789     7.89  LABEL1234 OTHER1234      8.9012    9.876  1.000E+00  2.000E+00\n     3.4560   4  5.60  6.70  7.80ABCD 8 9 10 11.200 12 13.400 AFIELD123 BFIELD12314.5000 15.700 16.10 17.20 18.30",
            [1.2345, 2.345, 3.5, 4.567, 5.7, 6.789, 7.89, 'LABEL1234', 'OTHER1234', 8.9012, 9.876, 1.0, 2.0, 3.456, 4, 5.6, 6.7, 7.8, 'ABCD', 8, 9, 10, 11.2, 12, 13.4, 'AFIELD123', 'BFIELD123', 14.5, 15.7, 16.1, 17.2, 18.3],
        )

    def test_read_materialized_data_for_final_record(self):
        self._assert_materialized(
            "(F10.4,F7.3,F5.1,F12.3,F5.1,F12.3,F9.2,A10,A10/0PF10.4,I4,F6.2,F6.2,F6.2,A4,I2,I2,I3,F7.3,I3,F7.3,A10,A10,F7.4,F7.3,3F6.2,F10.4)",
            "    1.2345  2.345  3.5       4.567  5.7       6.789     7.89 LABEL1234 OTHER1234\n    8.9012   4  5.60  6.70  7.80ABCD 8 9 10 11.200 12 13.400 AFIELD123 BFIELD12314.5000 15.700 16.10 17.20 18.30   19.4000",
            [1.2345, 2.345, 3.5, 4.567, 5.7, 6.789, 7.89, 'LABEL1234', 'OTHER1234', 8.9012, 4, 5.6, 6.7, 7.8, 'ABCD', 8, 9, 10, 11.2, 12, 13.4, 'AFIELD123', 'BFIELD123', 14.5, 15.7, 16.1, 17.2, 18.3, 19.4],
        )

    def _assert_formatted_read(self, format, text, data):
        with FormattedFile(io.StringIO(text)) as ff:
            res = ff.read(format)
            self.assertEqual(res, data)

    def _assert_formatted_write(self, format, text, data):
        with FormattedFile(io.StringIO()) as ff:
            res = ff.write(format, *data)
            self.assertEqual(res, text)

    def test_format_1(self):
        text = 'TEFF   5770.  GRAVITY 4.44000     \n'
        text += 'TITLE   B a s i c A T L A S                                                     '
        data = (5770.0, 4.44, '', list('  B a s i c A T L A S'.ljust(74)))
        format = '5HTEFF ,F7.0,9H  GRAVITY,F8.5,1X,A4/6HTITLE ,74A1'

        self._assert_formatted_read(format, text, data)
        self._assert_formatted_write(format, text, data)
        
    def test_format_2(self):

        text = """TEFF   5770.  GRAVITY 4.44000     
TITLE   B a s i c A T L A S                                                     
 OPACITY IFOP 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 0 0 0 0 0
 CONVECTION ON   1.25 TURBULENCE OFF  0.00  0.00  0.00  0.00
ABUNDANCE SCALE   1.00000 ABUNDANCE CHANGE 1 0.91183 2 0.08708
 ABUNDANCE CHANGE  3  -8.78  4 -10.66  5  -9.25  6  -3.54  7  -4.18  8  -3.28"""

        data = (
            5770.0, 4.44000, '',
            list('  B a s i c A T L A S'.ljust(74)),
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
            'ON', 1.25, 'OFF', [0.00, 0.00, 0.00, 0.00],
            1.0,
            [[1, 0.91183], [2, 0.08708]],
            [[3, -8.78], [4, -10.66], [5, -9.25], [6, -3.54], [7, -4.18], [8, -3.28]]
        )

        format = """5HTEFF F7.0,9H GRAVITY F5.3,1XA4/6HTITLE 74A1
/13H OPACITY IFOP20I2/12H CONVECTION A3,F6.2,12H TURBULENCE A3,
4F6.2/16HABUNDANCE SCALE F7.3,17H ABUNDANCE CHANGE2(I2,F6.3)/
(17H ABUNDANCE CHANGE6(I3,F7.2))"""

        self._assert_formatted_read(format, text, data)
        self._assert_formatted_write(format, text, data)

    def test_format_reversion(self):
        text = """TEFF   5770.  GRAVITY 4.44000     
TITLE   B a s i c A T L A S                                                     
 OPACITY IFOP 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 0 0 0 0 0
 CONVECTION ON   1.25 TURBULENCE OFF  0.00  0.00  0.00  0.00
ABUNDANCE SCALE   1.00000 ABUNDANCE CHANGE 1 0.91183 2 0.08708
 ABUNDANCE CHANGE  3  -8.78  4 -10.66  5  -9.25  6  -3.54  7  -4.18  8  -3.28
 ABUNDANCE CHANGE  9  -7.48 10  -4.02 11  -5.80 12  -4.44 13  -5.59 14  -4.53
 ABUNDANCE CHANGE 15  -6.58 16  -4.88 17  -6.54 18  -5.64 19  -6.93 20  -5.70
 ABUNDANCE CHANGE 21  -8.89 22  -7.09 23  -8.11 24  -6.40 25  -6.61 26  -4.52
 ABUNDANCE CHANGE 27  -7.05 28  -5.82 29  -7.85 30  -7.48 31  -9.00 32  -8.39
 ABUNDANCE CHANGE 33  -9.74 34  -8.70 35  -9.50 36  -8.79 37  -9.68 38  -9.17
 ABUNDANCE CHANGE 39  -9.83 40  -9.42 41 -10.58 42 -10.16 43 -20.00 44 -10.29
 ABUNDANCE CHANGE 45 -10.98 46 -10.39 47 -10.84 48 -10.33 49 -11.28 50 -10.00
 ABUNDANCE CHANGE 51 -11.03 52  -9.86 53 -10.49 54  -9.80 55 -10.96 56  -9.86
 ABUNDANCE CHANGE 57 -10.94 58 -10.46 59 -11.32 60 -10.62 61 -20.00 62 -11.08
 ABUNDANCE CHANGE 63 -11.52 64 -10.97 65 -11.74 66 -10.94 67 -11.56 68 -11.12
 ABUNDANCE CHANGE 69 -11.94 70 -11.12 71 -11.94 72 -11.17 73 -12.16 74 -11.39
 ABUNDANCE CHANGE 75 -11.78 76 -10.68 77 -10.66 78 -10.42 79 -11.24 80 -10.87
 ABUNDANCE CHANGE 81 -11.27 82 -10.00 83 -11.39 84 -20.00 85 -20.00 86 -20.00
 ABUNDANCE CHANGE 87 -20.00 88 -20.00 89 -20.00 90 -11.96 91 -20.00 92 -12.58
 ABUNDANCE CHANGE 93 -20.00 94 -20.00 95 -20.00 96 -20.00 97 -20.00 98 -20.00
 ABUNDANCE CHANGE 99 -20.00"""

        data = (
            5770.0, 4.44000, '',
            list('  B a s i c A T L A S'.ljust(74)),
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
            'ON', 1.25, 'OFF', [0.00, 0.00, 0.00, 0.00],
            1.0,
            [[1, 0.91183], [2, 0.08708]],
            [[3, -8.78], [4, -10.66], [5, -9.25], [6, -3.54], [7, -4.18], [8, -3.28]],
            [[ 9,  -7.48], [10,  -4.02], [11,  -5.80], [12,  -4.44], [13,  -5.59], [14,  -4.53]],
            [[15,  -6.58], [16,  -4.88], [17,  -6.54], [18,  -5.64], [19,  -6.93], [20,  -5.70]],
            [[21,  -8.89], [22,  -7.09], [23,  -8.11], [24,  -6.40], [25,  -6.61], [26,  -4.52]],
            [[27,  -7.05], [28,  -5.82], [29,  -7.85], [30,  -7.48], [31,  -9.00], [32,  -8.39]],
            [[33,  -9.74], [34,  -8.70], [35,  -9.50], [36,  -8.79], [37,  -9.68], [38,  -9.17]],
            [[39,  -9.83], [40,  -9.42], [41, -10.58], [42, -10.16], [43, -20.00], [44, -10.29]],
            [[45, -10.98], [46, -10.39], [47, -10.84], [48, -10.33], [49, -11.28], [50, -10.00]],
            [[51, -11.03], [52,  -9.86], [53, -10.49], [54,  -9.80], [55, -10.96], [56,  -9.86]],
            [[57, -10.94], [58, -10.46], [59, -11.32], [60, -10.62], [61, -20.00], [62, -11.08]],
            [[63, -11.52], [64, -10.97], [65, -11.74], [66, -10.94], [67, -11.56], [68, -11.12]],
            [[69, -11.94], [70, -11.12], [71, -11.94], [72, -11.17], [73, -12.16], [74, -11.39]],
            [[75, -11.78], [76, -10.68], [77, -10.66], [78, -10.42], [79, -11.24], [80, -10.87]],
            [[81, -11.27], [82, -10.00], [83, -11.39], [84, -20.00], [85, -20.00], [86, -20.00]],
            [[87, -20.00], [88, -20.00], [89, -20.00], [90, -11.96], [91, -20.00], [92, -12.58]],
            [[93, -20.00], [94, -20.00], [95, -20.00], [96, -20.00], [97, -20.00], [98, -20.00]],
            [[99, -20.00]]
        )

        format = """5HTEFF F7.0,9H GRAVITY F5.3,1XA4/6HTITLE 74A1
/13H OPACITY IFOP20I2/12H CONVECTION A3,F6.2,12H TURBULENCE A3,
4F6.2/16HABUNDANCE SCALE F7.3,17H ABUNDANCE CHANGE2(I2,F6.3)/
(17H ABUNDANCE CHANGE6(I3,F7.2))"""

        self._assert_formatted_write(format, text, data)

    def test_write_format_reversion_partial(self):

        text = """TEFF   5770.  GRAVITY 4.44000     
ABUNDANCE SCALE   1.00000 ABUNDANCE CHANGE 1 0.91183 2 0.08708
 ABUNDANCE CHANGE  3  -8.78  4 -10.66  5  -9.25  6  -3.54  7  -4.18  8  -3.28
 ABUNDANCE CHANGE  9  -7.48 10  -4.02 11  -5.80 12  -4.44 13  -5.59 14  -4.53
 ABUNDANCE CHANGE 99 -20.00"""

        format = """5HTEFF F7.0,9H GRAVITY F5.3,1XA4/
16HABUNDANCE SCALE F7.3,17H ABUNDANCE CHANGE2(I2,F6.3)/
(17H ABUNDANCE CHANGE6(I3,F7.2))"""

        data = (
            5770.0, 4.44000, '',
            1.0,
            [[1, 0.91183], [2, 0.08708]],
            [[3, -8.78], [4, -10.66], [5, -9.25], [6, -3.54], [7, -4.18], [8, -3.28]],
            [[ 9,  -7.48], [10,  -4.02], [11,  -5.80], [12,  -4.44], [13,  -5.59], [14,  -4.53]],
            [[99, -20.00]]
        )

        self._assert_formatted_write(format, text, data)

    def test_read_format_reversion_partial(self):

        text = """TEFF   5770.  GRAVITY 4.44000     
ABUNDANCE SCALE   1.00000 ABUNDANCE CHANGE 1 0.91183 2 0.08708
 ABUNDANCE CHANGE  3  -8.78  4 -10.66  5  -9.25  6  -3.54  7  -4.18  8  -3.28
 ABUNDANCE CHANGE  9  -7.48 10  -4.02 11  -5.80 12  -4.44 13  -5.59 14  -4.53
 ABUNDANCE CHANGE 99 -20.00
"""

        format = """5HTEFF F7.0,9H GRAVITY F5.3,1XA4/
16HABUNDANCE SCALE F7.3,17H ABUNDANCE CHANGE2(I2,F6.3)/
(17H ABUNDANCE CHANGE6(I3,F7.2))"""

        data = (
            5770.0, 4.44000, '',
            1.0, [[1, 0.91183], [2, 0.08708]],
            [[3, -8.78], [4, -10.66], [5, -9.25], [6, -3.54], [7, -4.18], [8, -3.28]],
            [[ 9,  -7.48], [10,  -4.02], [11,  -5.80], [12,  -4.44], [13,  -5.59], [14,  -4.53]],
            [[99, -20.00]]
        )

        self._assert_formatted_read(format, text, data)