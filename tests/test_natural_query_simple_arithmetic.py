# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.simple_arithmetic import prepare_simple_expression, solve_simple_arithmetic


class SimpleArithmeticQueryTest(unittest.TestCase):
    def test_prepare_simple_expression_handles_german_words_and_typos(self):
        self.assertEqual(prepare_simple_expression("Was ist 2 pluss 2?"), "2+2")
        self.assertEqual(prepare_simple_expression("wass is 8 geteillt duch 2?"), "8/2")

    def test_solve_simple_arithmetic_returns_structured_result(self):
        result = solve_simple_arithmetic("was ist 5 plus 5", degrees=True)
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "5+5")
        self.assertEqual(result.answer, "10")
        self.assertEqual(result.explanation, "Direkt ausgewertet als 5+5.")

    def test_solve_simple_arithmetic_returns_none_for_unknown_text(self):
        self.assertIsNone(solve_simple_arithmetic("hallo welt", degrees=True))

    def test_solve_simple_arithmetic_handles_sloppy_input(self):
        result = solve_simple_arithmetic("rechne bitte 7 pls 5", degrees=True)
        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "12")

    def test_solve_simple_arithmetic_handles_written_number_words(self):
        result = solve_simple_arithmetic("was ist zwei plus drei plus vier", degrees=True)
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "2+3+4")
        self.assertEqual(result.answer, "9")


if __name__ == "__main__":
    unittest.main()
