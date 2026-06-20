# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.expression_parser import CalculatorError, ExpressionParser


class ExpressionParserTest(unittest.TestCase):
    def parse(self, expression: str, degrees: bool = True):
        return ExpressionParser(expression, degrees).parse()

    def test_existing_scientific_operations(self):
        self.assertAlmostEqual(self.parse("log(1000)"), 3)
        self.assertEqual(self.parse("5!"), 120)
        self.assertAlmostEqual(self.parse("sin(30)"), 0.5)
        self.assertEqual(self.parse("17 mod 5"), 2)

    def test_hyperbolic_functions(self):
        self.assertEqual(self.parse("sinh(0)"), 0)
        self.assertEqual(self.parse("tanh(0)"), 0)
        self.assertAlmostEqual(self.parse("cosh(0)"), 1)

    def test_complex_numbers(self):
        self.assertEqual(self.parse("i*i"), -1)
        self.assertEqual(self.parse("(2+3i)+(4-i)"), 6 + 2j)
        self.assertEqual(self.parse("real(2+3i)"), 2)
        self.assertEqual(self.parse("imag(2+3i)"), 3)
        self.assertEqual(self.parse("sqrt(-1)"), 1j)

    def test_power_binds_before_unary_minus(self):
        self.assertEqual(self.parse("-2^2"), -4)
        self.assertEqual(self.parse("(-2)^2"), 4)
        self.assertEqual(self.parse("2^-2"), 0.25)

    def test_real_only_operations_reject_complex_values(self):
        with self.assertRaises(CalculatorError):
            self.parse("(2+i) mod 2")


if __name__ == "__main__":
    unittest.main()
