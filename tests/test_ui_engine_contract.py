# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.calculator_logic import handle_button, update_display
from core.expression_parser import ExpressionParser
from core.formatting import format_number, pretty_expression
from ui.button_config import (
    BUTTON_INSERTIONS,
    BUTTON_ROWS,
    BUTTON_SHORTCUT_HINTS,
    SECOND_MODE_LABELS,
    button_shortcut_hint,
)


class UiEngineContractTest(unittest.TestCase):
    SPECIAL_BUTTONS = {
        "2nd",
        "Deg",
        "Rad",
        "AC",
        "CE",
        "⌫",
        "=",
        "+/-",
        "%",
        "mc",
        "mr",
        "m+",
        "m-",
        "ms",
        "Ans",
        "Rand",
    }
    DIRECT_PARSER_LABELS = set("0123456789") | {".", "+", "-", "(", ")", "e"}
    REQUIRED_SECOND_MODE_LABELS = {
        "x²": "sqrt",
        "x³": "cbrt",
        "sin": "asin",
        "cos": "acos",
        "tan": "atan",
        "ln": "e^x",
        "log": "10^x",
    }

    def assertAlmostValue(self, actual, expected, *, places: int = 10, label: str = ""):
        if isinstance(actual, complex) or isinstance(expected, complex):
            actual = complex(actual)
            expected = complex(expected)
            self.assertAlmostEqual(actual.real, expected.real, places=places, msg=label)
            self.assertAlmostEqual(actual.imag, expected.imag, places=places, msg=label)
            return
        self.assertAlmostEqual(actual, expected, places=places, msg=label)

    def test_every_visible_button_has_engine_contract(self):
        labels = [label for row in BUTTON_ROWS for label in row]
        duplicates = {label for label in labels if labels.count(label) > 1}
        self.assertEqual(duplicates, {"(", ")"})
        for label in labels:
            with self.subTest(label=label):
                self.assertTrue(
                    label in self.SPECIAL_BUTTONS
                    or label in self.DIRECT_PARSER_LABELS
                    or label in BUTTON_INSERTIONS,
                    f"Button ohne Engine-Vertrag: {label!r}",
                )

    def test_required_symbol_mappings_are_stable(self):
        expected = {
            "×": "*",
            "÷": "/",
            "π": "pi",
            "xʸ": "^",
            "n!": "!",
            "1/x": "inv(",
            "|x|": "abs(",
            "x²": "square(",
            "x³": "cube(",
            "sqrt": "sqrt(",
            "cbrt": "cbrt(",
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",
            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",
            "ln": "ln(",
            "log": "log(",
            "e^x": "exp(",
            "10^x": "pow10(",
            "mod": " mod ",
            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",
            "i": "i",
            "Re": "real(",
            "Im": "imag(",
            "pf": "pf(",
        }
        for label, insertion in expected.items():
            with self.subTest(label=label):
                self.assertEqual(BUTTON_INSERTIONS.get(label), insertion)

    def test_second_mode_targets_are_visible_and_insertable(self):
        visible = {label for row in BUTTON_ROWS for label in row}
        self.assertEqual(SECOND_MODE_LABELS, self.REQUIRED_SECOND_MODE_LABELS)
        for base, alternate in SECOND_MODE_LABELS.items():
            with self.subTest(base=base, alternate=alternate):
                self.assertIn(base, visible)
                self.assertIn(alternate, BUTTON_INSERTIONS)

    def test_parser_accepts_button_function_insertions(self):
        cases = {
            "inv(2)": 0.5,
            "abs(-3)": 3,
            "square(3)": 9,
            "cube(2)": 8,
            "sqrt(9)": 3,
            "cbrt(27)": 3,
            "sin(30)": 0.5,
            "cos(60)": 0.5,
            "tan(45)": 1,
            "asin(0.5)": 30,
            "acos(0.5)": 60,
            "atan(1)": 45,
            "ln(e)": 1,
            "log(100)": 2,
            "exp(0)": 1,
            "pow10(2)": 100,
            "sinh(0)": 0,
            "cosh(0)": 1,
            "tanh(0)": 0,
            "real(2+3i)": 2,
            "imag(2+3i)": 3,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertAlmostValue(ExpressionParser(expression, True).parse(), expected, label=expression)

    def test_shortcut_hints_match_button_insertions(self):
        expected_shortcuts = {
            "+": "+",
            "-": "-",
            "×": "*",
            "÷": "/",
            "=": "Enter",
            "⌫": "Backspace",
            "CE": "Entfernen",
            "AC": "Escape",
            "(": "(",
            ")": ")",
            "%": "%",
            ".": ".",
            "xʸ": "^",
        }
        self.assertEqual(BUTTON_SHORTCUT_HINTS, expected_shortcuts)
        self.assertEqual(BUTTON_INSERTIONS["×"], "*")
        self.assertEqual(BUTTON_INSERTIONS["÷"], "/")
        self.assertEqual(BUTTON_INSERTIONS["xʸ"], "^")
        for digit in "0123456789":
            with self.subTest(digit=digit):
                self.assertEqual(button_shortcut_hint(digit), digit)


class CalculatorLogicWindow:
    class DummyLabel:
        def __init__(self, value: str = ""):
            self.value = value

        def setText(self, text: str):
            self.value = text

        def text(self):
            return self.value

    TRANSLATIONS = {
        "percent_adjusted": "Prozentwert angepasst",
        "result_confirmed": "Ergebnis bestätigt",
        "ready_input": "Bereit für Eingabe",
        "waiting_for_closing_parentheses": "Wartet auf {count} schließende Klammer(n)",
        "building_expression": "Ausdruck wird aufgebaut",
        "finite_number_required": "Kein endlicher Wert",
        "prime_factor_real_required": "Primfaktorzerlegung braucht eine reelle Zahl",
        "prime_factor_integer_required": "Primfaktorzerlegung braucht eine ganze Zahl",
        "last_calculation": "Letzte Rechnung",
    }

    def __init__(self):
        self.expression = ""
        self.degrees = True
        self.just_evaluated = False
        self.memory = 0.0
        self.history_items = []
        self.history_dialog = None
        self.expression_label = self.DummyLabel()
        self.result_label = self.DummyLabel("0")
        self.preview_label = self.DummyLabel()
        self.preview_state = "neutral"
        self.refresh_mode_count = 0
        update_display(self)

    def _format_number(self, value):
        return format_number(value)

    def _pretty_expression(self, text: str) -> str:
        return pretty_expression(text)

    def _tr(self, key: str) -> str:
        return self.TRANSLATIONS[key]

    def _set_preview_state(self, text: str, state: str = "neutral") -> None:
        self.preview_label.setText(text)
        self.preview_state = state

    def _update_display(self) -> None:
        update_display(self)

    def _refresh_mode_labels(self) -> None:
        self.refresh_mode_count += 1


class UiEngineButtonSequenceContractTest(unittest.TestCase):
    def press(self, *labels: str) -> CalculatorLogicWindow:
        window = CalculatorLogicWindow()
        for label in labels:
            handle_button(window, label)
        return window

    def test_basic_button_sequences_reach_engine_correctly(self):
        cases = [
            (("2", "×", "3", "="), "6"),
            (("2", "+", "3", "×", "4", "="), "14"),
            (("(", "2", "+", "3", ")", "×", "4", "="), "20"),
            (("sqrt", "9", ")", "="), "3"),
            (("2", "xʸ", "3", "="), "8"),
            (("5", "n!", "="), "120"),
        ]
        for sequence, expected_result in cases:
            with self.subTest(sequence=sequence):
                window = self.press(*sequence)
                self.assertEqual(window.result_label.text(), expected_result)
                self.assertEqual(window.expression, expected_result)
                self.assertEqual(window.preview_state, "success")
                self.assertEqual(window.history_items[-1][1], expected_result)

    def test_pi_button_uses_implicit_multiplication_contract(self):
        window = self.press("2", "π")
        self.assertEqual(window.expression, "2*pi")
        self.assertAlmostEqual(float(window.result_label.text()), 2 * 3.141592653589793, places=10)

    def test_prime_factor_button_is_calculator_logic_contract_not_parser_function(self):
        window = self.press("pf", "1", "2", ")", "=")
        self.assertEqual(window.result_label.text(), "2 × 2 × 3")
        self.assertEqual(window.history_items[-1], ("pf(12)", "2 × 2 × 3"))
        self.assertEqual(window.preview_state, "success")

    def test_percent_button_sequences_are_stable(self):
        cases = [
            (("2", "0", "0", "+", "1", "0", "%", "="), "200+20", "220"),
            (("2", "0", "0", "-", "1", "0", "%", "="), "200-20", "180"),
            (("2", "0", "0", "×", "1", "0", "%", "="), "200*0.1", "20"),
            (("2", "0", "0", "÷", "1", "0", "%", "="), "200/0.1", "2000"),
        ]
        for sequence, adjusted_expression, expected_result in cases:
            with self.subTest(sequence=sequence):
                window = CalculatorLogicWindow()
                for label in sequence[:-1]:
                    handle_button(window, label)
                self.assertEqual(window.expression, adjusted_expression)
                handle_button(window, sequence[-1])
                self.assertEqual(window.result_label.text(), expected_result)
                self.assertEqual(window.history_items[-1][1], expected_result)

    def test_evaluation_error_is_controlled_and_does_not_push_history(self):
        window = self.press("1", "÷", "0", "=")
        self.assertEqual(window.result_label.text(), "ERROR")
        self.assertEqual(window.preview_state, "error")
        self.assertEqual(window.history_items, [])


if __name__ == "__main__":
    unittest.main()
