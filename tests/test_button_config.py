# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from ui import button_config


class ButtonConfigTest(unittest.TestCase):
    def test_backspace_button_is_configured_for_ui_and_keyboard_hint(self):
        labels = [label for row in button_config.BUTTON_ROWS for label in row]
        self.assertIn("⌫", labels)
        self.assertEqual(button_config.button_shortcut_hint("⌫"), "Backspace")

    def test_scientific_insertions_match_parser_tokens(self):
        self.assertEqual(button_config.BUTTON_INSERTIONS["×"], "*")
        self.assertEqual(button_config.BUTTON_INSERTIONS["÷"], "/")
        self.assertEqual(button_config.BUTTON_INSERTIONS["mod"], " mod ")
        self.assertEqual(button_config.BUTTON_INSERTIONS["sqrt"], "sqrt(")
        self.assertEqual(button_config.BUTTON_INSERTIONS["sinh"], "sinh(")
        self.assertEqual(button_config.BUTTON_INSERTIONS["i"], "i")
        self.assertEqual(button_config.BUTTON_INSERTIONS["pf"], "pf(")

    def test_second_mode_labels_are_available_in_advanced_rows(self):
        advanced_labels = {
            label
            for row_index in button_config.ADVANCED_ROWS
            for label in button_config.BUTTON_ROWS[row_index]
        }
        self.assertTrue(set(button_config.SECOND_MODE_LABELS).issubset(advanced_labels))

    def test_advanced_buttons_have_tooltip_keys(self):
        self.assertEqual(button_config.button_tooltip_key("pf"), "tooltip_prime_factor")
        self.assertEqual(button_config.button_tooltip_key("mod"), "tooltip_mod")

    def test_graphite_is_default_theme(self):
        self.assertEqual(button_config.DEFAULT_THEME, "graphite")

    def test_bottom_row_zero_keeps_full_width_span(self):
        self.assertEqual(button_config.BUTTON_COLUMN_COUNT, 7)
        self.assertEqual(button_config.BUTTON_COLUMN_SPANS["0"], button_config.BUTTON_COLUMN_COUNT)


if __name__ == "__main__":
    unittest.main()
