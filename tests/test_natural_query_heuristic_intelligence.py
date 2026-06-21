# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.formatting import format_number
from core.natural_query.assistant_helpers import solve_local_natural_query
from core.natural_query.heuristic_intelligence import improve_query_heuristically, score_query_domains
from core.natural_query.types import CLARIFICATION_EXPRESSION


class NaturalQueryHeuristicIntelligenceTest(unittest.TestCase):
    def solve(self, query: str):
        result = solve_local_natural_query(query, degrees=True, format_number=format_number)
        self.assertIsNotNone(result, query)
        return result

    def assertAnswer(self, query: str, expected: str):
        _, answer, _ = self.solve(query)
        self.assertEqual(answer, expected, query)

    def test_normalization_repairs_common_typos_without_api(self):
        normalized = improve_query_heuristically("wievil sind 15 przent fon 200")
        self.assertIn("wie viel", normalized)
        self.assertRegex(normalized, r"15\s*%")
        self.assertIn("von 200", normalized)
        self.assertAnswer("wievil sind 15 przent fon 200", "30")

    def test_domain_scoring_prefers_percent_for_vat_query(self):
        scored = score_query_domains("19% mehrwertsteuer auf 100 netto")
        self.assertGreaterEqual(scored[0].confidence, 0.4)
        self.assertEqual(scored[0].domain, "percent")

    def test_vat_heuristic_handles_rate_before_net_amount(self):
        self.assertAnswer("19% MwSt auf 100 netto", "119")
        self.assertAnswer("100 brutto inklusive 19% mwst netto berechnen", "84.0336134454")

    def test_heuristics_do_not_steal_specialist_solver_queries(self):
        self.assertIn("meters", improve_query_heuristically("convert 5 km to meters"))
        self.assertAnswer("How much is VAT on 100 with 19%?", "19")
        self.assertAnswer("What is the final price with 15% discount on 200?", "170")
        self.assertAnswer("Wie viel Zinsen bei 11% Jahreszins auf 1000 Euro für 2 Jahre?", "220")

    def test_percent_adjustments_are_understood(self):
        self.assertAnswer("erhöhe 250 um 12%", "280")
        self.assertAnswer("reduziere 250 um 12%", "220")

    def test_everyday_split_amount(self):
        self.assertAnswer("84 Euro auf 4 Personen aufteilen", "21")

    def test_ambiguous_interest_is_not_guessed(self):
        expression, answer, explanation = self.solve("1000 Euro bei 5% Zinsen für 3 Jahre")
        self.assertEqual(expression, CLARIFICATION_EXPRESSION)
        self.assertIn("Zinsbetrag", answer)
        self.assertIn("Endbetrag", f"{answer}\n{explanation}")


if __name__ == "__main__":
    unittest.main()
