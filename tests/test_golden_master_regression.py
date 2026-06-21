# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import sys
import unittest
from pathlib import Path

from core.expression_parser import CalculatorError, ExpressionParser
from core.formatting import format_number
from core.natural_query import CLARIFICATION_EXPRESSION
from core.natural_query.assistant_helpers import solve_local_natural_query


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALCULATOR_PATH = PROJECT_ROOT / "calculator.py"


class GoldenMasterExpressionRegressionTest(unittest.TestCase):
    def parse(self, expression: str, *, degrees: bool = True):
        return ExpressionParser(expression, degrees).parse()

    def assertAlmostValue(self, actual, expected, *, places: int = 10, label: str = ""):
        if isinstance(actual, complex) or isinstance(expected, complex):
            actual = complex(actual)
            expected = complex(expected)
            self.assertAlmostEqual(actual.real, expected.real, places=places, msg=label)
            self.assertAlmostEqual(actual.imag, expected.imag, places=places, msg=label)
            return
        self.assertAlmostEqual(actual, expected, places=places, msg=label)

    def test_arithmetic_precedence_and_parser_percent_golden_master(self):
        cases = [
            ("2+2", 4),
            ("2+3*4", 14),
            ("(2+3)*4", 20),
            ("-2^2", -4),
            ("(-2)^2", 4),
            ("2^-2", 0.25),
            ("2^3^2", 512),
            ("17 mod 5", 2),
            ("10%", 0.1),
            ("200*10%", 20),
            ("50%*200", 100),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostValue(self.parse(expression), expected, label=expression)

    def test_implicit_multiplication_golden_master(self):
        cases = [
            ("2pi", 2 * 3.141592653589793),
            ("2e", 2 * 2.718281828459045),
            ("2(3+4)", 14),
            ("(1+2)(3+4)", 21),
            ("3i", 3j),
            ("2sin(30)", 1),
            ("sqrt(9)2", 6),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostValue(self.parse(expression), expected, label=expression)

    def test_function_golden_master(self):
        cases = [
            ("sqrt(144)", 12),
            ("cbrt(27)", 3),
            ("square(12)", 144),
            ("cube(3)", 27),
            ("abs(-42)", 42),
            ("ln(e)", 1),
            ("log(1000)", 3),
            ("pow10(3)", 1000),
            ("5!", 120),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostValue(self.parse(expression), expected, label=expression)

    def test_angle_mode_golden_master(self):
        cases = [
            ("sin(30)", True, 0.5),
            ("cos(60)", True, 0.5),
            ("tan(45)", True, 1),
            ("sin(pi/2)", False, 1),
            ("asin(0.5)", True, 30),
            ("acos(0.5)", True, 60),
            ("atan(1)", True, 45),
        ]
        for expression, degrees, expected in cases:
            with self.subTest(expression=expression, degrees=degrees):
                self.assertAlmostValue(self.parse(expression, degrees=degrees), expected, label=expression)

    def test_complex_golden_master(self):
        cases = [
            ("i*i", -1),
            ("(2+3i)+(4-i)", 6 + 2j),
            ("sqrt(-1)", 1j),
            ("real(2+3i)", 2),
            ("imag(2+3i)", 3),
            ("conj(2+3i)", 2 - 3j),
            ("arg(1+i)", 45),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostValue(self.parse(expression), expected, label=expression)

    def test_formatting_golden_master(self):
        cases = [
            (4.0, "4"),
            (47.5, "47.5"),
            (1 / 3, "0.333333333333"),
            (6 + 2j, "6 + 2i"),
            (2 - 3j, "2 - 3i"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(format_number(value), expected)

    def test_error_boundary_golden_master(self):
        cases = ["1/0", "5 mod 0", "(-1)!", "2.5!", "unknown(2)", "1.2.3", "1e+", "((2+3)"]
        for expression in cases:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    self.parse(expression)


class GoldenMasterNaturalQueryRegressionTest(unittest.TestCase):
    def solve(self, query: str):
        return solve_local_natural_query(query, degrees=True, format_number=format_number)

    def test_local_natural_query_golden_master(self):
        cases = [
            ("Was sind 19 Prozent von 250?", ("250*0.19", "47.5")),
            ("Wurzel aus 144", ("sqrt(144)", "12")),
            ("Wie viel ist 2 hoch 8?", ("2^8", "256")),
            ("convert 5 km to meters", ("5 km -> meters", "5000")),
            ("Wie viele Meter sind 5 Kilometer?", ("5 kilometer -> meter", "5000")),
        ]
        for query, expected_prefix in cases:
            with self.subTest(query=query):
                result = self.solve(query)
                self.assertIsNotNone(result)
                self.assertEqual(result[:2], expected_prefix)

    def test_ambiguous_natural_query_returns_clarification(self):
        queries = [
            "1000 euro bei 5% zinsen für 3 jahre",
            "wie lange brauche ich bei 600 und 50",
            "Wie hoch ist die Dichte bei 10 und 2?",
        ]
        for query in queries:
            with self.subTest(query=query):
                result = self.solve(query)
                self.assertIsNotNone(result)
                self.assertEqual(result[0], CLARIFICATION_EXPRESSION)


class GoldenMasterCalculatorButtonRegressionTest(unittest.TestCase):
    class DummyLabel:
        def __init__(self, value: str = ""):
            self.value = value

        def setText(self, text: str):
            self.value = text

        def text(self):
            return self.value

    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec("PySide6") is None:
            raise unittest.SkipTest("PySide6 lokal nicht installiert; UI-nahe Tests nicht aussagekräftig.")
        spec = importlib.util.spec_from_file_location("matrix_calculator_golden_master", CALCULATOR_PATH)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.module = module

    def make_window(self, expression: str):
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.expression = expression
        window.just_evaluated = False
        window.degrees = True
        window.history_items = []
        window.history_dialog = None
        window.expression_label = self.DummyLabel(expression)
        window.preview_label = self.DummyLabel("")
        window.result_label = self.DummyLabel("")
        translations = {
            "percent_adjusted": "Prozentwert angepasst",
            "result_confirmed": "Ergebnis bestätigt",
            "ready_input": "Bereit für Eingabe",
            "waiting_for_closing_parentheses": "Wartet auf {count} schließende Klammer(n)",
            "building_expression": "Ausdruck wird aufgebaut",
            "finite_number_required": "Kein endlicher Wert",
        }
        window._tr = lambda key: translations[key]
        window._push_history = lambda expression, result: window.history_items.append((expression, result))
        for name in [
            "_apply_percent_input",
            "_last_top_level_operator",
            "_update_display",
            "_evaluate",
            "_balanced_expression",
            "_try_prime_factorization",
            "_is_finite_number",
            "_pretty_expression",
            "_format_number",
        ]:
            setattr(
                window,
                name,
                getattr(self.module.MatrixCalculatorWindow, name).__get__(
                    window, self.module.MatrixCalculatorWindow
                ),
            )
        return window

    def test_percent_button_golden_master(self):
        cases = [
            ("200+10", "200+20", "220"),
            ("200-10", "200-20", "180"),
            ("200*10", "200*0.1", "20"),
            ("200/10", "200/0.1", "2000"),
        ]
        for expression, adjusted_expression, expected_result in cases:
            with self.subTest(expression=expression):
                window = self.make_window(expression)
                window._apply_percent_input()
                self.assertEqual(window.expression, adjusted_expression)
                window._evaluate()
                self.assertEqual(window.result_label.text(), expected_result)


if __name__ == "__main__":
    unittest.main()
