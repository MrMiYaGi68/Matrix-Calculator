# SPDX-License-Identifier: GPL-3.0-or-later
import random
import unittest

from core.expression_parser import ExpressionParser


class EngineDeterministicFuzzSampleTest(unittest.TestCase):
    def test_safe_arithmetic_subset_matches_python(self):
        rng = random.Random(20260621)
        operators = ["+", "-", "*", "/"]
        samples = [
            "1+2*3",
            "(1+2)*3",
            "10/(2+3)",
            "2^3^2",
            "1e3+2",
            "1e-2+3",
        ]
        for _ in range(60):
            a = rng.randint(-50, 50)
            b = rng.randint(1, 50)
            c = rng.randint(1, 20)
            op1 = rng.choice(operators)
            op2 = rng.choice(operators)
            samples.append(f"({a}{op1}{b}){op2}{c}")

        for expression in samples:
            with self.subTest(expression=expression):
                parser_value = ExpressionParser(expression, degrees=True).parse()
                python_expression = expression.replace("^", "**")
                python_value = eval(python_expression, {"__builtins__": {}}, {})
                self.assertAlmostEqual(parser_value, python_value, places=10)


if __name__ == "__main__":
    unittest.main()
