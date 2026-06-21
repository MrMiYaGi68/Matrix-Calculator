# SPDX-License-Identifier: GPL-3.0-or-later
import math
import unittest

from core.expression_parser import CalculatorError, ExpressionParser


class EngineInvariantTest(unittest.TestCase):
    def parse(self, expression: str, degrees: bool = True):
        return ExpressionParser(expression, degrees).parse()

    def assertClose(self, expression: str, expected, *, degrees: bool = True, places: int = 10):
        value = self.parse(expression, degrees=degrees)
        if isinstance(expected, complex) or isinstance(value, complex):
            self.assertAlmostEqual(value.real, expected.real, places=places, msg=expression)
            self.assertAlmostEqual(value.imag, expected.imag, places=places, msg=expression)
        else:
            self.assertAlmostEqual(value, expected, places=places, msg=expression)

    def test_operator_precedence_and_power_associativity(self):
        cases = {
            "-2^2": -4,
            "(-2)^2": 4,
            "2^-2": 0.25,
            "2^3^2": 512,
            "2*3^2": 18,
            "(2+3)*4": 20,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertClose(expression, expected)

    def test_implicit_multiplication(self):
        cases = {
            "2pi": 2 * math.pi,
            "2e": 2 * math.e,
            "2(3+4)": 14,
            "(1+2)(3+4)": 21,
            "3i": 3j,
            "2sin(30)": 1,
            "sqrt(9)2": 6,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertClose(expression, expected)

    def test_complex_and_angle_functions(self):
        self.assertClose("i*i", -1)
        self.assertClose("(2+3i)+(4-i)", 6 + 2j)
        self.assertClose("sqrt(-1)", 1j)
        self.assertClose("real(2+3i)", 2)
        self.assertClose("imag(2+3i)", 3)
        self.assertClose("conj(2+3i)", 2 - 3j)
        self.assertClose("arg(1+i)", 45)
        self.assertClose("sin(pi/2)", 1, degrees=False)

    def test_real_only_operations_reject_complex_inputs(self):
        with self.assertRaises(CalculatorError):
            self.parse("(2+i) mod 2")


if __name__ == "__main__":
    unittest.main()
