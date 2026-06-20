# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.relationships import solve_relationship_query


class RelationshipQueryTest(unittest.TestCase):
    def test_factor_relationship_with_named_target(self):
        result = solve_relationship_query("anna ist doppelt so alt wie ben zusammen sind sie 36 wie alt ist anna")

        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "24")
        self.assertIn("anna", result.explanation)
        self.assertIn("ben", result.explanation)

    def test_delta_relationship_with_named_target(self):
        result = solve_relationship_query("lisa hat 5 mehr als max zusammen haben sie 25 wie viel hat max")

        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "10")

    def test_returns_both_values_when_target_is_not_explicit(self):
        result = solve_relationship_query("tom ist dreimal so viel wie eva zusammen 40")

        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "tom = 30, eva = 10")

    def test_english_relationship_query(self):
        result = solve_relationship_query("anna is twice as old as ben together 36 how old is ben")

        self.assertIsNotNone(result)
        self.assertEqual(result.answer, "12")


if __name__ == "__main__":
    unittest.main()
