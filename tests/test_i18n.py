# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.i18n import LANGUAGES, TRANSLATIONS, normalize_language, tr
from core.natural_query.response import build_local_answer


class I18nTest(unittest.TestCase):
    def test_language_options_include_default_and_five_additional_languages(self):
        self.assertEqual(set(LANGUAGES), {"de", "en", "es", "fr", "it", "tr"})

    def test_english_settings_translation(self):
        self.assertEqual(tr("en", "settings"), "Settings")
        self.assertEqual(tr("en", "calculate"), "Calculate")

    def test_unknown_language_falls_back_to_german(self):
        self.assertEqual(normalize_language("unknown"), "de")
        self.assertEqual(tr("unknown", "settings"), "Einstellungen")

    def test_all_languages_have_core_ui_labels(self):
        for code in LANGUAGES:
            self.assertNotEqual(tr(code, "settings"), "settings")
            self.assertNotEqual(tr(code, "language"), "language")
            self.assertNotEqual(tr(code, "calculate"), "calculate")
            self.assertNotEqual(tr(code, "tooltip_prime_factor"), "tooltip_prime_factor")
            self.assertIn("pf(360)", tr(code, "skills_content_html"))

    def test_all_languages_have_same_translation_keys(self):
        expected = set(TRANSLATIONS["de"])
        for code in LANGUAGES:
            self.assertEqual(set(TRANSLATIONS[code]), expected)

    def test_assistant_intro_mentions_local_ai_language_limit(self):
        self.assertIn("Deutsch und Englisch", tr("de", "assistant_intro"))
        self.assertIn("German and English", tr("en", "assistant_intro"))

    def test_app_language_can_force_english_answer_labels(self):
        body = build_local_answer("Was sind 20% von 450?", "450*0.2", "90", "Direkt ausgewertet.", True, "en")
        self.assertIn("Result:", body)
        self.assertIn("Calculation:", body)


if __name__ == "__main__":
    unittest.main()
