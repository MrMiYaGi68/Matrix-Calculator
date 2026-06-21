# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.statistics import solve_average_query, solve_distribution_query, solve_summary_query


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

    def test_solve_sum_query(self):
        result = solve_summary_query("summe von 2 4 6")
        self.assertIsNotNone(result)
        self.assertEqual(result.expression, "sum(2,4,6)")
        self.assertEqual(result.answer, "12")

    def test_solve_minimum_maximum_and_range_queries(self):
        cases = [
            ("minimum von 2 9 4", "min(2,9,4)", "2"),
            ("maximum von 2 9 4", "max(2,9,4)", "9"),
            ("spannweite von 2 9 4", "range(2,9,4)", "7"),
        ]
        for query, expression, answer in cases:
            with self.subTest(query=query):
                result = solve_summary_query(query)
                self.assertIsNotNone(result)
                self.assertEqual(result.expression, expression)
                self.assertEqual(result.answer, answer)


if __name__ == "__main__":
    unittest.main()
