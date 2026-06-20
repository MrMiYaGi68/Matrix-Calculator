# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.units import solve_unit_conversion_query


class NaturalQueryUnitsTest(unittest.TestCase):
    def test_converts_ps_to_kw_with_abbreviations(self):
        result = solve_unit_conversion_query("100 ps in kw")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "100 ps -> kw")
        self.assertEqual(result.answer, "73.549875")

    def test_converts_ps_to_kw_with_dash_abbreviation(self):
        result = solve_unit_conversion_query("100ps-kw")
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "73.549875")

    def test_converts_abbreviation_pair_before_value(self):
        result = solve_unit_conversion_query("ps-kw 100")
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "73.549875")

    def test_converts_kw_to_ps(self):
        result = solve_unit_conversion_query("100 kw in ps")
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "135.96216173")


if __name__ == "__main__":
    unittest.main()
