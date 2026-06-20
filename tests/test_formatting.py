# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.formatting import format_number, pretty_expression


class FormattingTest(unittest.TestCase):
    def test_format_number_trims_integer_float(self):
        self.assertEqual(format_number(12.0), "12")

    def test_format_number_uses_compact_precision(self):
        self.assertEqual(format_number(1 / 3), "0.333333333333")

    def test_format_number_displays_complex_values(self):
        self.assertEqual(format_number(3 + 2j), "3 + 2i")
        self.assertEqual(format_number(0 - 1j), "-i")

    def test_pretty_expression_uses_display_operators(self):
        self.assertEqual(pretty_expression("1+2*3/4^2"), "1+2 × 3 ÷ 4 ^ 2")


if __name__ == "__main__":
    unittest.main()
