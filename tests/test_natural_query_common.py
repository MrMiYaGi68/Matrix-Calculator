# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.common import (
    extract_numbers,
    format_local_result,
    local_smalltalk_response,
    normalize_natural_query,
    unit_factor,
)


class NaturalQueryCommonTest(unittest.TestCase):
    def test_extract_numbers_handles_decimal_values(self):
        self.assertEqual(extract_numbers("12 und 3.5"), [12.0, 3.5])

    def test_normalize_natural_query_replaces_german_number_words(self):
        self.assertEqual(normalize_natural_query("Was ist zwei plus drei?"), "was ist 2 plus 3?")
        self.assertEqual(normalize_natural_query("fünfundzwanzig prozent von vierhundert"), "25 % von 400")

    def test_normalize_natural_query_replaces_number_abbreviations(self):
        self.assertEqual(normalize_natural_query("1k plus 2k"), "1000 plus 2000")
        self.assertEqual(normalize_natural_query("1,5k plus 2 Mio"), "1500 plus 2000000")
        self.assertEqual(normalize_natural_query("3 mrd minus 500 tsd"), "3000000000 minus 500000")

    def test_normalize_natural_query_replaces_english_chat_abbreviations(self):
        self.assertEqual(normalize_natural_query("can u calculate 20% w/ vat pls"), "can you calculate 20% with vat please")
        self.assertEqual(normalize_natural_query("how much r 20% of 450"), "how much are 20% of 450")
        self.assertEqual(normalize_natural_query("thx btw"), "thanks by the way")

    def test_normalize_natural_query_keeps_radius_abbreviation_before_number(self):
        self.assertEqual(normalize_natural_query("circle area r 5"), "circle area r 5")

    def test_normalize_natural_query_keeps_pls_as_plus_between_numbers(self):
        self.assertEqual(normalize_natural_query("7 pls 5"), "7 plus 5")

    def test_normalize_natural_query_keeps_units_with_k_prefix(self):
        self.assertEqual(normalize_natural_query("100 kw in ps"), "100 kw in ps")
        self.assertEqual(normalize_natural_query("5 km mit 1 h"), "5 km mit 1 h")

    def test_normalize_natural_query_does_not_turn_articles_into_numbers(self):
        self.assertEqual(
            normalize_natural_query("Ein Artikel kostet zweihundert Euro"),
            "ein artikel kostet 200 euro",
        )

    def test_normalize_natural_query_replaces_hyphenated_english_number_words(self):
        self.assertEqual(normalize_natural_query("twenty-one plus five"), "21 plus 5")

    def test_format_local_result_formats_number(self):
        self.assertEqual(format_local_result("1/2", 0.5, "halb"), ("1/2", "0.5", "halb"))

    def test_unit_factor_knows_time_units(self):
        self.assertEqual(unit_factor("woche"), 604800.0)

    def test_unit_factor_knows_power_abbreviations(self):
        self.assertEqual(unit_factor("kw"), 1000.0)
        self.assertEqual(unit_factor("ps"), 735.49875)

    def test_smalltalk_hallo_returns_local_hint(self):
        result = local_smalltalk_response("Hallo")
        self.assertIsNotNone(result)
        self.assertIn("Hallo!", result[1])

    def test_smalltalk_hello_returns_english_hint(self):
        result = local_smalltalk_response("Hello!")
        self.assertIsNotNone(result)
        self.assertIn("Hello!", result[1])
        self.assertIn("20% of 450", result[2])

    def test_smalltalk_thanks_returns_english_response(self):
        result = local_smalltalk_response("thank you")
        self.assertIsNotNone(result)
        self.assertIn("welcome", result[1])

    def test_smalltalk_help_returns_english_capability_hint(self):
        result = local_smalltalk_response("what can you do?")
        self.assertIsNotNone(result)
        self.assertIn("German and English", result[1])

    def test_smalltalk_handles_english_chat_abbreviations(self):
        result = local_smalltalk_response("how r u?")
        self.assertIsNotNone(result)
        self.assertIn("Hello!", result[1])


if __name__ == "__main__":
    unittest.main()
