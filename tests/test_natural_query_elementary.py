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

    def test_solve_power_with_base_and_exponent(self):
        result = solve_power_query("potenz 2 hoch 8")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "2^8")
        self.assertEqual(result.answer, "256")

    def test_solve_root_query(self):
        result = solve_root_query("quadratwurzel 2")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "sqrt(2)")
        self.assertEqual(result.answer, "1.41421356237")

    def test_solve_nth_root_query(self):
        result = solve_root_query("dritte wurzel aus 27")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "27^(1/3)")
        self.assertEqual(result.answer, "3")

        result = solve_root_query("4te wurzel aus 16")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "16^(1/4)")
        self.assertEqual(result.answer, "2")


if __name__ == "__main__":
    unittest.main()
