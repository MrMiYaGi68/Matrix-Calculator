# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.elementary import solve_power_query, solve_root_query


class NaturalQueryElementaryTest(unittest.TestCase):
    def test_solve_square_query(self):
        result = solve_power_query("quadrat von 12")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "12^2")
        self.assertEqual(result.answer, "144")

    def test_solve_cube_query(self):
        result = solve_power_query("kubik von 3")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "3^3")
        self.assertEqual(result.answer, "27")

    def test_solve_root_query(self):
        result = solve_root_query("quadratwurzel 2")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "sqrt(2)")
        self.assertEqual(result.answer, "1.41421356237")


if __name__ == "__main__":
    unittest.main()
