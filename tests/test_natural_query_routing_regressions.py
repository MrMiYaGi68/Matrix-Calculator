# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.formatting import format_number
from core.natural_query.assistant_helpers import solve_local_natural_query
from core.natural_query.types import CLARIFICATION_EXPRESSION


class NaturalQueryRoutingRegressionTest(unittest.TestCase):
    def solve(self, query: str):
        result = solve_local_natural_query(query, degrees=True, format_number=format_number)
        self.assertIsNotNone(result, query)
        return result

    def assertAnswer(self, query: str, expected: str):
        _, answer, _ = self.solve(query)
        self.assertEqual(answer, expected, query)

    def assertClarification(self, query: str, expected_text: str):
        expression, answer, explanation = self.solve(query)
        self.assertEqual(expression, CLARIFICATION_EXPRESSION, query)
        self.assertIn(expected_text, f"{answer}\n{explanation}", query)

    def test_percent_queries_win_over_generic_arithmetic(self):
        self.assertAnswer("Was sind 20% von 450?", "90")
        self.assertAnswer("100 plus 19%", "119")
        self.assertAnswer("100 minus 19%", "81")

    def test_ambiguous_domain_queries_ask_for_clarification(self):
        self.assertClarification("1000 euro bei 5% zinsen für 3 jahre", "Zinsbetrag")
        self.assertClarification("wie lange brauche ich bei 600 und 50", "Einheiten")
        self.assertClarification("Wie hoch ist die Dichte bei 10 und 2?", "Physikaufgabe")
        self.assertClarification("mehrwertsteuer 2026 deutschland", "Finanzaufgabe")

    def test_unit_physics_and_motion_routes_do_not_steal_each_other(self):
        self.assertAnswer("100 kw in ps", "135.96216173")
        self.assertAnswer("Wie hoch ist die Dichte bei 10 kg und 2 m3?", "5")
        self.assertAnswer("wie lange brauche ich für 600 km mit 50 kmh", "12")

    def test_german_umlaut_words_survive_english_replacements(self):
        self.assertAnswer("Wie hoch ist die Dichte bei 2 m3 und 10 kg?", "5")
        self.assertAnswer("How long for 600 km with 50 km/h?", "12")

    def test_local_ai_handles_more_elementary_and_statistics_queries(self):
        self.assertAnswer("dritte wurzel aus 27", "3")
        self.assertAnswer("potenz 2 hoch 8", "256")
        self.assertAnswer("summe von 2 4 6", "12")
        self.assertAnswer("maximum von 2 9 4", "9")
        self.assertAnswer("spannweite von 2 9 4", "7")
        self.assertAnswer("ein drittel von 90", "30")
        self.assertAnswer("die hälfte von 42", "21")


if __name__ == "__main__":
    unittest.main()
