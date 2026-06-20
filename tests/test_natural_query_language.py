# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.natural_query.language import is_english_query, translate_local_text


class NaturalQueryLanguageTest(unittest.TestCase):
    def test_is_english_query_detects_common_markers(self):
        self.assertTrue(is_english_query("What is the square root of 100?"))
        self.assertFalse(is_english_query("Was ist die Wurzel von 100?"))

    def test_translate_local_text_keeps_german_when_disabled(self):
        self.assertEqual(translate_local_text("Ergebnis", english=False), "Ergebnis")

    def test_translate_local_text_replaces_known_labels(self):
        self.assertEqual(translate_local_text("Ergebnis: 90", english=True), "Result: 90")


if __name__ == "__main__":
    unittest.main()
