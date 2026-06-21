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

    def test_scientific_buttons_have_semantic_groups(self):
        self.assertEqual(button_config.scientific_button_group("mc"), "memory")
        self.assertEqual(button_config.scientific_button_group("AC"), "entry")
        self.assertEqual(button_config.scientific_button_group("x²"), "power")
        self.assertEqual(button_config.scientific_button_group("sin"), "trig")
        self.assertEqual(button_config.scientific_button_group("Re"), "complex")
        self.assertEqual(button_config.scientific_button_group("7"), "keypad")
        self.assertEqual(button_config.scientific_button_group("+"), "keypad")

    def test_advanced_buttons_have_tooltip_keys(self):
        self.assertEqual(button_config.button_tooltip_key("pf"), "tooltip_prime_factor")
        self.assertEqual(button_config.button_tooltip_key("mod"), "tooltip_mod")
        self.assertEqual(button_config.button_tooltip_key("AC"), "tooltip_clear_all")
        self.assertEqual(button_config.button_tooltip_key("CE"), "tooltip_clear_entry")
        self.assertEqual(button_config.button_tooltip_key("+/-"), "tooltip_toggle_sign")

    def test_graphite_is_default_theme(self):
        self.assertEqual(button_config.DEFAULT_THEME, "graphite")

    def test_bottom_row_zero_keeps_full_width_span(self):
        self.assertEqual(button_config.BUTTON_COLUMN_COUNT, 7)
        self.assertEqual(button_config.BUTTON_COLUMN_SPANS["0"], button_config.BUTTON_COLUMN_COUNT)

    def test_basic_layout_moves_primary_operator_column_to_the_right(self):
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(1, 3)], (1, 6, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(5, 3)], (5, 6, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(6, 3)], (6, 6, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(7, 3)], (7, 6, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(5, 4)], (7, 0, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(5, 0)], (5, 3, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(8, 0)], (8, 0, 5))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(5, 5)], (8, 5, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(7, 6)], (8, 6, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(3, 6)], (1, 3, 1))

    def test_basic_layout_groups_entry_and_function_controls(self):
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(1, 4)], (1, 0, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(1, 2)], (1, 1, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(2, 5)], (1, 2, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(2, 0)], (5, 0, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(2, 1)], (5, 1, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(1, 5)], (6, 2, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(7, 4)], (7, 1, 1))
        self.assertEqual(button_config.BASIC_BUTTON_POSITIONS[(7, 5)], (7, 2, 1))


if __name__ == "__main__":
    unittest.main()
