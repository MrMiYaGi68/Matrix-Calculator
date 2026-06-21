# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALCULATOR_PATH = PROJECT_ROOT / "calculator.py"


def load_calculator_module():
    spec = importlib.util.spec_from_file_location("matrix_calculator", CALCULATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LocalParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_calculator_module()

    def setUp(self):
        self.window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        self.window.degrees = True
        self.window.ai_step_by_step = True
        for name in [
            "_format_number",
            "_try_prime_factorization",
            "_prime_factorization_text",
            "_is_finite_number",
            "_pretty_expression",
            "_extract_numbers",
            "_format_local_result",
            "_unit_factor",
            "_button_shortcut_hint",
            "_local_smalltalk_response",
            "_prepare_simple_expression",
            "_solve_local_natural_query",
            "_build_live_query_preview",
            "_build_local_answer",
            "_is_english_query",
            "_translate_local_text",
            "_build_query_help",
            "_normalize_assistant_mode",
            "_normalize_openai_model",
            "_choose_auto_openai_model",
            "_openai_api_help_text",
            "_describe_openai_api_error",
        ]:
            setattr(
                self.window,
                name,
                getattr(self.module.MatrixCalculatorWindow, name).__get__(
                    self.window, self.module.MatrixCalculatorWindow
                ),
            )

    def solve(self, query: str):
        result = self.window._solve_local_natural_query(query)
        self.assertIsNotNone(result, f"Parser returned None for: {query}")
        return result

    class DummyLabel:
        def __init__(self, value: str = ""):
            self.value = value

        def setText(self, text: str):
            self.value = text

        def text(self):
            return self.value

    def make_calculator_logic_window(self, expression: str):
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
            "_push_history",
        ]:
            if name == "_push_history":
                window._push_history = lambda expression, result: window.history_items.append((expression, result))
                continue
            setattr(
                window,
                name,
                getattr(self.module.MatrixCalculatorWindow, name).__get__(
                    window, self.module.MatrixCalculatorWindow
                ),
            )
        return window

    def test_settings_help_dialog_dependencies_imported(self):
        self.assertTrue(hasattr(self.module, "QDialog"))
        self.assertTrue(hasattr(self.module, "QDialogButtonBox"))

    def test_prime_factorization_text(self):
        self.assertEqual(self.window._prime_factorization_text(360), "2 × 2 × 2 × 3 × 3 × 5")
        self.assertEqual(self.window._try_prime_factorization("pf(84)"), "2 × 2 × 3 × 7")
        self.assertEqual(self.window._try_prime_factorization("factor(84)"), "2 × 2 × 3 × 7")

    def test_language_switch_updates_idle_calculator_preview(self):
        class DummyText:
            def __init__(self, value: str = ""):
                self.value = value

            def setText(self, text: str):
                self.value = text

            def text(self):
                return self.value

            def setPlaceholderText(self, text: str):
                self.value = text

        class DummyCombo:
            def clear(self):
                pass

            def addItems(self, items):
                self.items = items

            def setCurrentText(self, text: str):
                self.current = text

        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.setWindowTitle = lambda title: None
        window.app_language = "en"
        window.expression = ""
        window.ai_messages = []
        window.assistant_mode = "browser_fallback"
        for attr in [
            "title_label",
            "subtitle_label",
            "history_button",
            "ai_title",
            "ai_hint",
            "ai_intro",
            "ai_input",
            "ai_result",
            "solve_button",
            "settings_button",
            "clear_ai_button",
            "ai_status",
            "ai_live_preview",
            "step_checkbox",
            "context_checkbox",
            "preview_label",
        ]:
            setattr(window, attr, DummyText("Bereit für Eingabe"))
        window.mode_preference = DummyCombo()
        window._recreate_localized_dialogs = lambda: None
        window._refresh_layout_mode = lambda: None
        for name in ["_apply_language", "_tr", "_assistant_mode_label"]:
            setattr(
                window,
                name,
                getattr(self.module.MatrixCalculatorWindow, name).__get__(
                    window, self.module.MatrixCalculatorWindow
                ),
            )

        window._apply_language()

        self.assertEqual(window.preview_label.text(), "Ready for input")

    def test_backspace_last_digit_resets_display_to_zero_and_keeps_input_working(self):
        class DummyLabel:
            def __init__(self, value: str = ""):
                self.value = value

            def setText(self, text: str):
                self.value = text

            def text(self):
                return self.value

        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.expression = "12"
        window.just_evaluated = False
        window.degrees = True
        window.expression_label = DummyLabel("12")
        window.preview_label = DummyLabel("Live: 12")
        window.result_label = DummyLabel("12")
        for name in [
            "_handle_button",
            "_append",
            "_update_display",
            "_balanced_expression",
            "_needs_implicit_multiply",
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

        window._handle_button("⌫")
        self.assertEqual(window.expression, "1")
        self.assertEqual(window.result_label.text(), "1")

        window._handle_button("⌫")
        self.assertEqual(window.expression, "")
        self.assertEqual(window.result_label.text(), "0")

        window._handle_button("7")
        self.assertEqual(window.expression, "7")
        self.assertEqual(window.result_label.text(), "7")

    def test_percent_button_uses_calculator_percent_logic(self):
        window = self.make_calculator_logic_window("200+10")
        window._apply_percent_input()
        self.assertEqual(window.expression, "200+20")

        window._evaluate()
        self.assertEqual(window.result_label.text(), "220")

    def test_percent_button_handles_minus_multiply_and_divide_semantics(self):
        cases = [
            ("200-10", "200-20", "180"),
            ("200*10", "200*0.1", "20"),
            ("200/10", "200/0.1", "2000"),
        ]
        for expression, adjusted_expression, expected_result in cases:
            with self.subTest(expression=expression):
                window = self.make_calculator_logic_window(expression)

                window._apply_percent_input()
                self.assertEqual(window.expression, adjusted_expression)

                window._evaluate()
                self.assertEqual(window.result_label.text(), expected_result)

    def test_failed_evaluation_does_not_push_history(self):
        window = self.make_calculator_logic_window("1/0")

        window._evaluate()

        self.assertEqual(window.result_label.text(), "ERROR")
        self.assertEqual(window.history_items, [])

    def assert_answer(self, query: str, expected: str):
        _, answer, _ = self.solve(query)
        self.assertEqual(answer, expected, query)

    def test_percent_de(self):
        self.assert_answer("Was sind 20% von 450?", "90")

    def test_percent_en(self):
        self.assert_answer("What is 20% of 450?", "90")

    def test_travel_time_de_variant_one(self):
        self.assert_answer("wie lange brauche ich mit 50 kmh bei 600km", "12")

    def test_travel_time_de_variant_two(self):
        self.assert_answer("wie lange brauche ich für 600 km mit 50 kmh", "12")

    def test_travel_time_en(self):
        self.assert_answer("How long do I need for 600 km with 50 km/h?", "12")

    def test_travel_distance(self):
        self.assert_answer("wie weit komme ich mit 50 kmh in 3 stunden", "150")

    def test_travel_speed(self):
        self.assert_answer("wie schnell bin ich bei 600 km in 12 stunden", "50")

    def test_travel_time_with_units_reordered(self):
        self.assert_answer("wie lange brauche ich bei 600 km und 50 kmh", "12")

    def test_ambiguous_travel_query_asks_for_clarification(self):
        expression, answer, explanation = self.solve("wie lange brauche ich bei 600 und 50")
        self.assertEqual(expression, self.module.CLARIFICATION_EXPRESSION)
        self.assertIn("Strecke", answer)
        self.assertIn("600 km", explanation)

    def test_discount_sentence_de(self):
        self.assert_answer(
            "Gegeben: Ein Artikel kostet 200 Euro. Gesucht: Preis nach 15% Rabatt.",
            "170",
        )

    def test_discount_sentence_en(self):
        self.assert_answer("What is the final price with 15% discount on 200?", "170")

    def test_rule_of_three_en(self):
        self.assert_answer("Given: 4 pieces cost 10 euro. Find: what do 7 pieces cost?", "17.5")

    def test_account_spending_de(self):
        self.assert_answer(
            "wenn ich 1500€ auf dem konto habe, wie viel habe ich dann wenn ich jeden Tag 34,5€ ausgebe in 30 Tagen?",
            "465",
        )

    def test_account_spending_de_variant(self):
        self.assert_answer(
            "wenn ich 1500 euro auf dem konto habe und jeden tag 34,5 euro ausgebe, wie viel bleibt in 30 tagen?",
            "465",
        )

    def test_account_spending_en(self):
        self.assert_answer(
            "If I have 1500 euro in my account and spend 34.5 euro every day for 30 days, how much is left?",
            "465",
        )

    def test_english_replacements_do_not_modify_german_umlaut_words(self):
        self.assert_answer("How long for 600 km with 50 km/h?", "12")

    def test_account_income_de(self):
        self.assert_answer(
            "wenn ich 1500 euro auf dem konto habe und jeden tag 20 euro verdiene, wie viel habe ich in 10 tagen?",
            "1700",
        )

    def test_repeated_amount_de(self):
        self.assert_answer(
            "wenn ich 200 eier pro woche habe, wie viele habe ich dann in 54 wochen?",
            "10800",
        )

    def test_repeated_amount_en(self):
        self.assert_answer(
            "If I have 200 eggs per week, how many do I have in 54 weeks?",
            "10800",
        )

    def test_recurring_income_week_to_year_de(self):
        self.assert_answer(
            "ich will 200€ in einer Woche verdienen, was habe ich in 1 Jahr?",
            "10435.7142857",
        )

    def test_recurring_income_week_to_year_en(self):
        self.assert_answer(
            "I earn 200 euro per week, how much is that in 1 year?",
            "10435.7142857",
        )

    def test_daily_consumption_to_week_de(self):
        self.assert_answer(
            "wie viele Eier brauche ich in der woche, wenn ich jeden Tag 2 Eier esse?",
            "14",
        )

    def test_daily_consumption_to_week_en(self):
        self.assert_answer(
            "How many eggs do I need in a week if I eat 2 eggs every day?",
            "14",
        )

    def test_root_en(self):
        self.assert_answer("What is the square root of 100?", "10")

    def test_root_de_without_von(self):
        self.assert_answer("Was ist die Quadratwurzel 2?", "1.41421356237")

    def test_root_de_plain(self):
        self.assert_answer("quadratwurzel 2", "1.41421356237")

    def test_density_en(self):
        self.assert_answer("What is the density with 10 kg and 2 m3?", "5")

    def test_density_with_units_reordered(self):
        self.assert_answer("Wie hoch ist die Dichte bei 2 m3 und 10 kg?", "5")

    def test_ambiguous_physics_query_asks_for_clarification(self):
        expression, answer, explanation = self.solve("Wie hoch ist die Dichte bei 10 und 2?")
        self.assertEqual(expression, self.module.CLARIFICATION_EXPRESSION)
        self.assertIn("Physikaufgabe", answer)
        self.assertIn("Dichte", explanation)

    def test_vat_en(self):
        self.assert_answer("How much is VAT on 100 with 19%?", "19")

    def test_gross_vat_en(self):
        self.assert_answer("What is the gross price including VAT on 100 with 19%?", "119")

    def test_simple_interest_en_more_natural_phrase(self):
        self.assert_answer(
            "How much simple interest do I pay on 1000 euro at 11% annual interest for 24 months?",
            "220",
        )

    def test_percent_change_en(self):
        self.assert_answer("What is the percentage change from 80 to 100?", "25")

    def test_speed_en(self):
        self.assert_answer("How fast am I with 600 km in 12 hours?", "50")

    def test_percent_increase_phrase(self):
        self.assert_answer("100 plus 19%", "119")

    def test_percent_decrease_phrase(self):
        self.assert_answer("100 minus 19%", "81")

    def test_simple_interest_amount_de_when_explicit(self):
        self.assert_answer("Wie viel Zinsbetrag bekomme ich bei 1000 euro mit 5% zinsen für 3 jahre?", "150")

    def test_annual_interest_with_month_duration(self):
        expression, answer, explanation = self.solve(
            "wie viel zinsen muss ich zahlen bei 11% Jahreszins bei 1000€ in 24 Monaten?"
        )
        self.assertEqual(expression, "1000*0.11*2")
        self.assertEqual(answer, "220")
        self.assertIn("1220", explanation)

    def test_annual_interest_with_rate_first_and_year_duration(self):
        self.assert_answer("Wie viel Zinsen bei 11% Jahreszins auf 1000 Euro für 2 Jahre?", "220")

    def test_ambiguous_interest_query_asks_for_clarification(self):
        expression, answer, explanation = self.solve("1000 euro bei 5% zinsen für 3 jahre")
        self.assertEqual(expression, self.module.CLARIFICATION_EXPRESSION)
        self.assertIn("Zinsbetrag", answer)
        self.assertIn("Zinseszins", answer)
        self.assertIn("Endbetrag", explanation)

    def test_compound_interest_when_explicit(self):
        self.assert_answer("1000 euro bei 5% zinseszins für 3 jahre", "1157.625")

    def test_voltage_current_power_de(self):
        self.assert_answer("Wie viel Leistung sind 12 V und 3 A?", "36")

    def test_quadratic_equation(self):
        expression, answer, _ = self.solve("1x^2 - 5x + 6 = 0")
        self.assertEqual(expression, "x1=3, x2=2")
        self.assertEqual(answer, "x1 = 3, x2 = 2")

    def test_linear_system_de(self):
        _, answer, _ = self.solve("2x + 3y = 13 und 1x + 1y = 5")
        self.assertEqual(answer, "x = 2, y = 3")

    def test_linear_system_en(self):
        _, answer, _ = self.solve("2x + 3y = 13 and 1x + 1y = 5")
        self.assertEqual(answer, "x = 2, y = 3")

    def test_fraction(self):
        self.assert_answer("1/2 + 3/4", "1.25")

    def test_simple_natural_arithmetic_de(self):
        self.assert_answer("Was ist 5 plus 5?", "10")

    def test_simple_conversational_arithmetic_de(self):
        self.assert_answer("Kannst du 7 minus 2 rechnen?", "5")

    def test_simple_arithmetic_with_typo(self):
        self.assert_answer("Was ist 2 pluss 2?", "4")

    def test_simple_arithmetic_with_written_number_words(self):
        self.assert_answer("Was ist zwei plus zwei?", "4")

    def test_percent_with_written_number_words(self):
        self.assert_answer("Was sind zwanzig Prozent von vierhundertfünfzig?", "90")

    def test_simple_arithmetic_with_number_abbreviations(self):
        self.assert_answer("Was ist 1k plus 2k?", "3000")

    def test_english_chat_abbreviation_in_calculation(self):
        self.assert_answer("Can u calculate 20% of 450 pls?", "90")

    def test_english_chat_are_abbreviation_in_percent_query(self):
        self.assert_answer("How much r 20% of 450?", "90")

    def test_percent_with_million_abbreviation(self):
        self.assert_answer("Was sind 10% von 1 Mio?", "100000")

    def test_local_ai_tolerates_sloppy_percent_query(self):
        self.assert_answer("wiviel sint 20 prozent fon 450", "90")

    def test_local_ai_tolerates_sloppy_motion_query(self):
        self.assert_answer("wi lange brauhe ich fur 600 km mitt 50 kmh", "12")

    def test_local_ai_tolerates_sloppy_root_query(self):
        self.assert_answer("wass is die quatratwurzel fon 9", "3")

    def test_circle_area_en(self):
        self.assert_answer("What is the circle area with radius 5?", "78.5398163397")

    def test_circle_area_en_radius_abbreviation(self):
        self.assert_answer("circle area r 5", "78.5398163397")

    def test_rectangle_area_en(self):
        self.assert_answer("What is the area of a rectangle with length 5 and width 4?", "20")

    def test_triangle_area_en(self):
        self.assert_answer("What is the triangle area with base 10 and height 6?", "30")

    def test_cuboid_volume_en(self):
        self.assert_answer("What is the volume of a cuboid with length 2 width 3 height 4?", "24")

    def test_circumference_en(self):
        self.assert_answer("What is the circumference with radius 5?", "31.4159265359")

    def test_radius_from_diameter_en(self):
        self.assert_answer("What is radius from diameter 10?", "5")

    def test_cone_volume_en(self):
        self.assert_answer("Volume of cone radius 3 height 10", "94.2477796077")

    def test_cylinder_surface_en(self):
        self.assert_answer("Surface area of cylinder radius 3 height 10", "245.04422698")

    def test_median_en(self):
        self.assert_answer("Median of 3 1 9 5 7", "5")

    def test_variance_en(self):
        self.assert_answer("Variance 2 4 4 4 5 5 7 9", "4")

    def test_standard_deviation_en(self):
        self.assert_answer("Standard deviation 2 4 4 4 5 5 7 9", "2")

    def test_relationship_word_problem_de(self):
        self.assert_answer("Anna ist doppelt so alt wie Ben. Zusammen sind sie 36. Wie alt ist Anna?", "24")

    def test_relationship_delta_word_problem_de(self):
        self.assert_answer("Lisa hat 5 mehr als Max. Zusammen haben sie 25. Wie viel hat Max?", "10")

    def test_english_output_labels(self):
        expression, answer, explanation = self.solve("What is 20% of 450?")
        body = self.window._build_local_answer("What is 20% of 450?", expression, answer, explanation)
        self.assertIn("Result:", body)
        self.assertIn("Calculation:", body)
        self.assertIn("Explanation:", body)

    def test_help_text_language_en(self):
        help_text = self.window._build_query_help("do something with 12 and 5")
        self.assertIn("Did you mean:", help_text)

    def test_help_text_language_de(self):
        help_text = self.window._build_query_help("mach mal was mit 12 und 5")
        self.assertIn("Meintest du:", help_text)

    def test_help_text_for_income_rate_query(self):
        help_text = self.window._build_query_help("ich will 200 euro in einer woche verdienen, was habe ich in 1 jahr")
        self.assertIn("Euro pro Woche", help_text)

    def test_chatgpt_fallback_not_duplicated(self):
        help_text = self.window._build_query_help("mach was kompliziertes mit 12 und 5")
        self.assertNotIn("Frag bitte ChatGPT:", help_text)
        self.assertIn("https://chatgpt.com/?q=", help_text)

    def test_api_mode_with_api_key_calls_openai(self):
        class DummyInput:
            def __init__(self, value: str):
                self.value = value

            def text(self):
                return self.value

            def clear(self):
                self.value = ""

        class DummyMode:
            def currentText(self):
                return "Direkt per API (Erweitert)"

        messages = []
        asked = []
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.ai_input = DummyInput("mach was komplexes")
        window.mode_preference = DummyMode()
        window.ai_api_key = "test-key"
        window.last_ai_query = ""
        window.ai_status = type("Status", (), {"setText": lambda self, text: None})()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._update_ai_live_preview = lambda text: None
        window._solve_local_natural_query = lambda query: None
        window._set_expression_and_evaluate = lambda expression: None
        window._build_query_help = self.window._build_query_help
        window._build_local_answer = self.window._build_local_answer
        window._normalize_assistant_mode = self.window._normalize_assistant_mode
        window._open_chatgpt_in_app = lambda query: self.fail("Embedded ChatGPT should not open in API mode with API key")
        window._ask_openai = lambda query=None: asked.append(query)

        self.module.MatrixCalculatorWindow._solve_natural_query(window)

        self.assertEqual(window.last_ai_query, "mach was komplexes")
        self.assertIn(("system", "Lokal nicht sicher erkannt. Ich versuche die API."), messages)
        self.assertEqual(asked, ["mach was komplexes"])

    def test_interest_clarification_followup_computes_choice_without_api(self):
        class DummyInput:
            def __init__(self, value: str):
                self.value = value

            def text(self):
                return self.value

            def clear(self):
                self.value = ""

        messages = []
        evaluated = []
        status = []
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.ai_input = DummyInput("1000 euro bei 5% zinsen für 3 jahre")
        window.ai_step_by_step = True
        window.pending_clarification = None
        window.last_ai_query = ""
        window.ai_status = type("Status", (), {"setText": lambda self, text: status.append(text)})()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._update_ai_live_preview = lambda text: None
        window._set_expression_and_evaluate = lambda expression: evaluated.append(expression)
        for name in [
            "_solve_local_natural_query",
            "_build_local_answer",
            "_remember_pending_clarification",
            "_resolve_pending_clarification",
            "_format_local_result",
            "_local_smalltalk_response",
            "_extract_numbers",
            "_unit_factor",
            "_prepare_simple_expression",
            "_is_english_query",
            "_translate_local_text",
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

        self.module.MatrixCalculatorWindow._solve_natural_query(window)

        self.assertTrue(window.pending_clarification)
        self.assertEqual(evaluated, [])
        self.assertTrue(any("Zinseszins" in text for _, text in messages))

        window.ai_input = DummyInput("Zinseszins")
        self.module.MatrixCalculatorWindow._solve_natural_query(window)

        self.assertIsNone(window.pending_clarification)
        self.assertEqual(evaluated, ["1000*(1+0.05)^3"])
        self.assertTrue(any("1157.625" in text for _, text in messages))

    def test_browser_fallback_does_not_auto_open_embedded_chatgpt(self):
        class DummyInput:
            def __init__(self, value: str):
                self.value = value

            def text(self):
                return self.value

            def clear(self):
                self.value = ""

        class DummyMode:
            def currentText(self):
                return "Lokal zuerst"

        messages = []
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.ai_input = DummyInput("mach was komplexes")
        window.mode_preference = DummyMode()
        window.ai_api_key = "test-key"
        window.last_ai_query = ""
        window.ai_status = type("Status", (), {"setText": lambda self, text: None})()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._update_ai_live_preview = lambda text: None
        window._solve_local_natural_query = lambda query: None
        window._set_expression_and_evaluate = lambda expression: None
        window._build_query_help = self.window._build_query_help
        window._build_local_answer = self.window._build_local_answer
        window._normalize_assistant_mode = self.window._normalize_assistant_mode
        window._open_chatgpt_in_app = lambda query: self.fail("Embedded ChatGPT should not auto-open in fallback mode")
        window._ask_openai = lambda query=None: self.fail("API should not be called in browser fallback mode")

        self.module.MatrixCalculatorWindow._solve_natural_query(window)

        self.assertTrue(any(role == "system" and "ChatGPT Web" in text for role, text in messages))

    def test_api_mode_without_api_key_does_not_auto_open_embedded_chatgpt(self):
        class DummyInput:
            def __init__(self, value: str):
                self.value = value

            def text(self):
                return self.value

            def clear(self):
                self.value = ""

        class DummyMode:
            def currentText(self):
                return "Direkt per API (Erweitert)"

        messages = []
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.ai_input = DummyInput("mach was komplexes")
        window.mode_preference = DummyMode()
        window.ai_api_key = ""
        window.last_ai_query = ""
        window.ai_status = type("Status", (), {"setText": lambda self, text: None})()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._update_ai_live_preview = lambda text: None
        window._solve_local_natural_query = lambda query: None
        window._set_expression_and_evaluate = lambda expression: None
        window._build_query_help = self.window._build_query_help
        window._build_local_answer = self.window._build_local_answer
        window._normalize_assistant_mode = self.window._normalize_assistant_mode
        window._open_chatgpt_in_app = lambda query: self.fail("Embedded ChatGPT should not auto-open without API key")
        window._ask_openai = lambda query=None: self.fail("API should not be called without API key")

        old_api_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            self.module.MatrixCalculatorWindow._solve_natural_query(window)
        finally:
            if old_api_key is not None:
                os.environ["OPENAI_API_KEY"] = old_api_key

        self.assertTrue(any(role == "system" and "Button 'ChatGPT Web'" in text for role, text in messages))

    def test_live_preview_for_resolved_query(self):
        preview = self.window._build_live_query_preview("Was sind 20% von 450?")
        self.assertIn("Live-Erkennung:", preview)
        self.assertIn("= 90", preview)

    def test_live_preview_for_partial_money_query(self):
        preview = self.window._build_live_query_preview(
            "wenn ich 1500 euro auf dem konto habe und jeden tag 34,5 euro ausgebe"
        )
        self.assertIn("Startbetrag 1500", preview)
        self.assertIn("Ausgabe 34.5", preview)
        self.assertIn("Rhythmus Tag", preview)

    def test_format_ai_message_html_supports_english_labels(self):
        html_body = self.module.MatrixCalculatorWindow._format_ai_message_html(
            self.window,
            "assistant",
            "Task recognized\nResult: 90\nCalculation: 450 * 0.2\nExplanation: First compute the percentage.",
        )
        self.assertIn("Aufgabe erkannt", html_body)
        self.assertIn("First compute the percentage.", html_body)
        self.assertNotIn("text-transform:uppercase", html_body)
        self.assertIn("font-size:24px", html_body)

    def test_format_ai_message_html_emphasizes_localized_result_labels(self):
        for label in ("Ergebnis", "Result", "Resultado", "Résultat", "Risultato", "Sonuç"):
            with self.subTest(label=label):
                html_body = self.module.MatrixCalculatorWindow._format_ai_message_html(
                    self.window,
                    "assistant",
                    f"{label}: 42",
                )
                self.assertIn("font-size:24px", html_body)

    def test_export_history_updates_history_dialog_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = str(Path(tmpdir) / "history.txt")

            class DummyDialog:
                @staticmethod
                def getSaveFileName(*args, **kwargs):
                    return export_path, "Textdateien (*.txt)"

            class DummyLabel:
                def __init__(self):
                    self.text = ""

                def setText(self, text):
                    self.text = text

            dialog = type("HistoryDialogStub", (), {"info_label": DummyLabel()})()
            window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
            window.history_items = [("1+1", "2")]
            window.history_dialog = dialog
            window._pretty_expression = self.window._pretty_expression

            original_dialog = self.module.QFileDialog
            self.module.QFileDialog = DummyDialog
            try:
                self.module.MatrixCalculatorWindow._export_history(window)
            finally:
                self.module.QFileDialog = original_dialog

            self.assertEqual(Path(export_path).read_text(encoding="utf-8"), "1+1 = 2\n")
            self.assertEqual(dialog.info_label.text, f"Exportiert nach: {export_path}")

    def test_normalize_openai_model_maps_old_values(self):
        self.assertEqual(self.window._normalize_openai_model("gpt-5.4-mini"), "gpt-5-mini")
        self.assertEqual(self.window._normalize_openai_model("gpt-5.4"), "gpt-5.1")
        self.assertEqual(self.window._normalize_openai_model("unknown-model"), "gpt-5-mini")

    def test_choose_auto_openai_model_prefers_highest_gpt5(self):
        chosen = self.window._choose_auto_openai_model(["gpt-5", "gpt-5-mini", "gpt-5.1", "gpt-5.2"])
        self.assertEqual(chosen, "gpt-5.2")

    def test_openai_api_help_text_contains_steps_and_links(self):
        help_text = self.window._openai_api_help_text()
        self.assertIn("https://platform.openai.com/api-keys", help_text)
        self.assertIn("https://platform.openai.com/settings/organization/billing/credit-grants", help_text)
        self.assertIn("https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits", help_text)
        self.assertIn("Schritt für Schritt", help_text)
        self.assertIn("ChatGPT-Login", help_text)

    def test_openai_error_for_insufficient_quota_is_german_and_specific(self):
        message = self.window._describe_openai_api_error(
            429,
            {
                "error": {
                    "message": "You exceeded your current quota, please check your plan and billing details.",
                    "code": "insufficient_quota",
                }
            },
        )
        self.assertIn("API-Projekt", message)
        self.assertIn("Billing", message)
        self.assertIn("Guthaben", message)

    def test_openai_error_for_invalid_key_is_german_and_specific(self):
        message = self.window._describe_openai_api_error(
            401,
            {
                "error": {
                    "message": "Incorrect API key provided",
                    "code": "invalid_api_key",
                }
            },
        )
        self.assertIn("API-Key", message)
        self.assertIn("api-keys", message)

    def test_local_smalltalk_hallo(self):
        expression, answer, explanation = self.solve("Hallo")
        self.assertEqual(expression, "")
        self.assertIn("Hallo", answer)
        self.assertIn("5 plus 5", explanation)

    def test_local_smalltalk_hello(self):
        expression, answer, explanation = self.solve("Hello")
        self.assertEqual(expression, "")
        self.assertIn("Hello", answer)
        self.assertIn("20% of 450", explanation)

    def test_local_smalltalk_english_help(self):
        expression, answer, explanation = self.solve("What can you do?")
        self.assertEqual(expression, "")
        self.assertIn("German and English", answer)
        self.assertIn("circle area", explanation)

    def test_local_smalltalk_english_abbreviated_help(self):
        expression, answer, explanation = self.solve("what can u do?")
        self.assertEqual(expression, "")
        self.assertIn("German and English", answer)
        self.assertIn("circle area", explanation)

    def test_button_shortcut_hint_for_divide(self):
        self.assertEqual(self.window._button_shortcut_hint("÷"), "/")

    def test_button_shortcut_hint_for_plus(self):
        self.assertEqual(self.window._button_shortcut_hint("+"), "+")

    def test_open_chatgpt_web_for_current_query_uses_input_first(self):
        opened = []
        messages = []
        window = self.module.MatrixCalculatorWindow.__new__(self.module.MatrixCalculatorWindow)
        window.ai_input = type("DummyInput", (), {"text": lambda self: "test frage"})()
        window.last_ai_query = "alte frage"
        window._open_chatgpt_in_app = lambda query: opened.append(query) or True
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window.ai_status = type("Status", (), {"setText": lambda self, text: None})()

        self.module.MatrixCalculatorWindow._open_chatgpt_web_for_current_query(window)

        self.assertEqual(opened, ["test frage"])
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
