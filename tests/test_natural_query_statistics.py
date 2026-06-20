# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.statistics import solve_average_query, solve_distribution_query


class NaturalQueryStatisticsTest(unittest.TestCase):
    def test_solve_average_query(self):
        result = solve_average_query("durchschnitt von 2 4 6")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "(2+4+6)/3")
        self.assertEqual(result.answer, "4")

    def test_solve_median_query(self):
        result = solve_distribution_query("median von 9 1 5")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "median(1,5,9)")
        self.assertEqual(result.answer, "5")

    def test_solve_variance_query(self):
        result = solve_distribution_query("varianz von 2 4 6")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "var(2,4,6)")
        self.assertEqual(result.answer, "2.66666666667")

    def test_solve_standard_deviation_query(self):
        result = solve_distribution_query("standardabweichung von 2 4 6")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "std(2,4,6)")
        self.assertEqual(result.answer, "1.63299316186")


if __name__ == "__main__":
    unittest.main()
