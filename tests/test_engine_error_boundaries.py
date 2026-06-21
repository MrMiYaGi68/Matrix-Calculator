# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.formatting import format_number
from core.expression_parser import CalculatorError, ExpressionParser


class EngineErrorBoundaryTest(unittest.TestCase):
    def parse(self, expression: str, degrees: bool = True):
        return ExpressionParser(expression, degrees).parse()

    def assertParserError(self, expression: str, *, degrees: bool = True):
        with self.assertRaises(CalculatorError, msg=expression):
            self.parse(expression, degrees=degrees)

    def test_rejects_arithmetic_domain_errors(self):
        for expression in ("1/0", "10 mod 0", "(-1)!", "2.5!", "2001!"):
            with self.subTest(expression=expression):
                self.assertParserError(expression)

    def test_rejects_invalid_token_boundaries(self):
        for expression in ("1.2.3", "1e+", "unknown(2)", "abc", "@"):
            with self.subTest(expression=expression):
                self.assertParserError(expression)

    def test_rejects_non_finite_numeric_literals_and_results(self):
        for expression in ("1e309", "1e309+1", "nan", "inf"):
            with self.subTest(expression=expression):
                self.assertParserError(expression)

    def test_formatter_rejects_non_finite_values(self):
        for value in (float("inf"), float("-inf"), float("nan"), complex(float("inf"), 0), complex(1, float("nan"))):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    format_number(value)

    def test_rejects_trig_singularities_in_degree_mode(self):
        for expression in ("tan(90)", "tan(270)"):
            with self.subTest(expression=expression):
                self.assertParserError(expression)

    def test_accepts_finite_trig_values_near_singularities(self):
        self.assertAlmostEqual(self.parse("tan(89.999)"), 57295.7795072, places=4)
        self.assertAlmostEqual(self.parse("tan(pi/4)", degrees=False), 1, places=10)


if __name__ == "__main__":
    unittest.main()
