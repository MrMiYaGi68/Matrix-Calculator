# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.algebra import solve_equation_query, solve_fraction_query


class NaturalQueryAlgebraTest(unittest.TestCase):
    def test_solve_quadratic_equation(self):
        result = solve_equation_query("1x^2 - 5x + 6 = 0")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "x1=3, x2=2")
        self.assertEqual(result.answer, "x1 = 3, x2 = 2")

    def test_solve_linear_system(self):
        result = solve_equation_query("2x + 3y = 13 und 1x + 1y = 5")
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "x = 2, y = 3")

    def test_solve_linear_equation(self):
        result = solve_equation_query("2x + 4 = 10")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "(10-4)/2")
        self.assertEqual(result.answer, "3")

    def test_solve_fraction_query(self):
        result = solve_fraction_query("1/2 + 3/4")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "(1/2)+(3/4)")
        self.assertEqual(result.answer, "1.25")

    def test_solve_written_fraction_of_query(self):
        cases = [
            ("ein drittel von 90", "(1/3)*90", "30"),
            ("2 drittel von 90", "(2/3)*90", "60"),
            ("ein viertel von 80", "(1/4)*80", "20"),
            ("die hälfte von 42", "(1/2)*42", "21"),
        ]
        for query, expression, answer in cases:
            with self.subTest(query=query):
                result = solve_fraction_query(query)
                self.assertIsNotNone(result)
                self.assertEqual(result.expression, expression)
                self.assertEqual(result.answer, answer)


if __name__ == "__main__":
    unittest.main()
