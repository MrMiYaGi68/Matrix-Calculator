# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.response import build_local_answer


class NaturalQueryResponseTest(unittest.TestCase):
    def test_build_local_answer_uses_english_labels_for_english_query(self):
        body = build_local_answer(
            "What is 20% of 450?",
            "450*0.2",
            "90",
            "20% von 450 bedeutet 450 × 0.2.",
            step_by_step=True,
        )
        self.assertIn("Result: 90", body)
        self.assertIn("Calculation: 450 × 0.2", body)
        self.assertIn("Explanation:", body)

    def test_build_local_answer_can_hide_explanation(self):
        body = build_local_answer("Was ist 5 plus 5?", "5+5", "10", "Direkt.", step_by_step=False)
        self.assertEqual(body, "Ergebnis: 10\nRechnung: 5+5")


if __name__ == "__main__":
    unittest.main()
