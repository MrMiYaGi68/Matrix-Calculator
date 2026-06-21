# SPDX-License-Identifier: GPL-3.0-or-later
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QSizePolicy, QTabWidget

from calculator import MatrixCalculatorWindow
from ui.dialogs import AssistantSettingsDialog, HistoryDialog, SkillsDialog
from ui.theme import theme_palette


class UiLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _make_window(self, width: int | None = None, *, open_ai: bool = False) -> MatrixCalculatorWindow:
        window = MatrixCalculatorWindow()
        if width is not None:
            window.resize(width, 920)
        window.show()
        self.app.processEvents()
        if open_ai:
            window._toggle_ai_panel()
            self.app.processEvents()
            if width is not None:
                window.resize(width, 920)
                self.app.processEvents()
        self.addCleanup(window.close)
        return window

    @staticmethod
    def _contrast_ratio(foreground: str, background: str) -> float:
        def luminance(color: str) -> float:
            channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [
                channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)

    def test_expanded_layout_uses_available_width_on_wide_windows(self):
        window = self._make_window(1900, open_ai=True)

        self.assertGreater(window.content_splitter.width(), window._collapsed_content_width())
        self.assertGreater(window.left_panel.width(), window.LEFT_PANEL_WIDTH)
        self.assertGreater(window.right_panel.width(), window.DEFAULT_AI_PANEL_WIDTH)
        self.assertGreater(window.maximumWidth(), window.EXPANDED_WINDOW_WIDTH)
        self.assertFalse(window.windowFlags() & Qt.MSWindowsFixedSizeDialogHint)

    def test_window_starts_collapsed(self):
        window = self._make_window()

        self.assertFalse(window.ai_panel_visible)
        self.assertFalse(window.right_panel.isVisible())
        self.assertFalse(window.windowFlags() & Qt.WindowMaximizeButtonHint)
        self.assertTrue(window.windowFlags() & Qt.MSWindowsFixedSizeDialogHint)
        self.assertEqual(window.minimumWidth(), window.COLLAPSED_WINDOW_WIDTH)
        self.assertEqual(window.maximumWidth(), window.COLLAPSED_WINDOW_WIDTH)
        self.assertEqual(window.minimumHeight(), window._collapsed_window_height())
        self.assertEqual(window.maximumHeight(), window._collapsed_window_height())
        self.assertEqual(window.width(), window.COLLAPSED_WINDOW_WIDTH)

    def test_collapsed_layout_stays_compact_on_wide_windows(self):
        window = self._make_window()

        self.assertFalse(window.right_panel.isVisible())
        self.assertEqual(window.content_splitter.width(), window._collapsed_content_width())
        self.assertEqual(window.content_splitter.sizes(), [window._collapsed_content_width(), 0])
        self.assertLessEqual(max(button.width() for button in window.all_calc_buttons if button.isVisible()), 720)

    def test_collapsed_normal_window_recovers_from_wide_geometry(self):
        window = self._make_window()
        window.resize(1400, 920)
        self.app.processEvents()

        window._enforce_collapsed_window_state()
        self.app.processEvents()

        self.assertEqual(window.width(), window.COLLAPSED_WINDOW_WIDTH)
        self.assertEqual(window.content_splitter.width(), window._collapsed_content_width())

    def test_collapsed_window_cannot_stay_maximized(self):
        window = self._make_window()

        self.assertFalse(window.windowFlags() & Qt.WindowMaximizeButtonHint)
        window.showMaximized()
        self.app.processEvents()
        window._enforce_collapsed_window_state()
        self.app.processEvents()

        self.assertFalse(window.isMaximized())
        self.assertFalse(window.isFullScreen())
        self.assertFalse(window.ai_panel_visible)
        self.assertEqual(window.width(), window.COLLAPSED_WINDOW_WIDTH)

    def test_collapsing_from_maximized_returns_to_normal_window(self):
        window = self._make_window(open_ai=True)
        self.assertTrue(window.windowFlags() & Qt.WindowMaximizeButtonHint)
        window.showMaximized()
        self.app.processEvents()
        self.assertTrue(window.isMaximized())

        window._toggle_ai_panel()
        self.app.processEvents()
        window._enforce_collapsed_window_state()
        self.app.processEvents()

        self.assertFalse(window.isMaximized())
        self.assertFalse(window.isFullScreen())
        self.assertFalse(window.ai_panel_visible)
        self.assertFalse(window.windowFlags() & Qt.WindowMaximizeButtonHint)
        self.assertTrue(window.windowFlags() & Qt.MSWindowsFixedSizeDialogHint)
        self.assertLessEqual(window.height(), window.COLLAPSED_WINDOW_HEIGHT)
        self.assertEqual(window.content_splitter.width(), window._collapsed_content_width())

    def test_toolbar_controls_have_enough_width_for_german_labels_at_default_width(self):
        window = self._make_window(1400, open_ai=True)

        for widget in (window.basic_mode_button, window.scientific_mode_button, window.history_button, window.ai_toggle_button):
            self.assertGreaterEqual(widget.width(), widget.sizeHint().width())

    def test_toolbar_buttons_use_compact_non_expanding_horizontal_policies(self):
        window = self._make_window(1400, open_ai=True)

        self.assertNotEqual(window.basic_mode_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertNotEqual(window.scientific_mode_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertNotEqual(window.history_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertNotEqual(window.ai_toggle_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)

    def test_layout_mode_uses_clear_segmented_controls(self):
        window = self._make_window()

        self.assertEqual(window.basic_mode_button.text(), window._tr("basic_layout"))
        self.assertEqual(window.scientific_mode_button.text(), window._tr("scientific_layout"))
        self.assertTrue(window.basic_mode_button.isChecked())
        self.assertFalse(window.scientific_mode_button.isChecked())

        window.scientific_mode_button.click()
        self.app.processEvents()

        self.assertFalse(window.basic_mode_button.isChecked())
        self.assertTrue(window.scientific_mode_button.isChecked())
        self.assertTrue(window.scientific_mode)

    def test_basic_keypad_moves_primary_operator_column_to_the_right(self):
        window = self._make_window()

        positions = {}
        for index in range(window.controls_grid.count()):
            item = window.controls_grid.itemAt(index)
            button = item.widget()
            if button is None or not button.isVisible():
                continue
            row, column, row_span, column_span = window.controls_grid.getItemPosition(index)
            positions[button.property("baseLabel")] = (row, column, row_span, column_span)

        self.assertEqual(positions["7"][:2], (5, 3))
        self.assertEqual(positions["8"][:2], (5, 4))
        self.assertEqual(positions["9"][:2], (5, 5))
        self.assertEqual(positions["4"][:2], (6, 3))
        self.assertEqual(positions["1"][:2], (7, 3))
        self.assertEqual(positions["3"][:2], (7, 5))
        self.assertEqual(positions["0"], (8, 0, 1, 5))
        self.assertEqual(positions["."], (8, 5, 1, 1))
        self.assertEqual(positions["AC"], (1, 6, 1, 1))
        self.assertEqual(positions["×"], (5, 6, 1, 1))
        self.assertEqual(positions["-"], (6, 6, 1, 1))
        self.assertEqual(positions["+"], (7, 6, 1, 1))
        self.assertEqual(positions["+/-"], (1, 0, 1, 1))
        self.assertEqual(positions["e"], (7, 0, 1, 1))
        self.assertEqual(positions["π"], (1, 2, 1, 1))
        self.assertEqual(positions["="], (8, 6, 1, 1))
        self.assertEqual(positions["⌫"], (1, 3, 1, 1))
        self.assertEqual(positions["x²"], (5, 0, 1, 1))
        self.assertEqual(positions["x³"], (5, 1, 1, 1))
        self.assertEqual(positions["mod"], (6, 2, 1, 1))
        self.assertEqual(positions["sqrt"], (7, 1, 1, 1))
        self.assertEqual(positions["cbrt"], (7, 2, 1, 1))
        backspace_button = next(button for button in window.all_calc_buttons if button.property("baseLabel") == "⌫")
        self.assertEqual(backspace_button.text(), "")
        self.assertFalse(backspace_button.icon().isNull())
        self.assertTrue(window.basic_group_separator.isVisible())

        visible_labels = {
            button.property("baseLabel"): button.text()
            for button in window.all_calc_buttons
            if button.isVisible()
        }
        self.assertEqual(visible_labels["mod"], "mod")
        self.assertNotIn("CE", visible_labels)
        self.assertNotIn("Ans", visible_labels)
        self.assertEqual(visible_labels["π"], "π")
        self.assertEqual(visible_labels["x²"], "x²")
        self.assertEqual(visible_labels["x³"], "x³")
        self.assertEqual(visible_labels["sqrt"], "√")
        self.assertEqual(visible_labels["cbrt"], "∛")

        window.scientific_mode_button.click()
        self.app.processEvents()

        self.assertTrue(window.left_panel.property("scientific"))
        ac_button = next(button for button in window.all_calc_buttons if button.property("baseLabel") == "AC")
        ac_index = window.controls_grid.indexOf(ac_button)
        self.assertEqual(window.controls_grid.getItemPosition(ac_index), (1, 3, 1, 1))
        self.assertFalse(window.basic_group_separator.isVisible())
        scientific_visibility = {
            button.property("baseLabel"): button.isVisible()
            for button in window.all_calc_buttons
        }
        self.assertTrue(scientific_visibility["CE"])
        self.assertTrue(scientific_visibility["Ans"])
        groups = {
            button.property("baseLabel"): button.property("scientificGroup")
            for button in window.all_calc_buttons
        }
        self.assertEqual(groups["mc"], "memory")
        self.assertEqual(groups["sin"], "trig")
        self.assertEqual(groups["Re"], "complex")
        self.assertEqual(groups["7"], "keypad")
        self.assertFalse(window.subtitle_label.isVisible())
        self.assertEqual(window.controls_grid.verticalSpacing(), 8)
        self.assertEqual(window.controls_layout.contentsMargins().bottom(), 6)

    def test_assistant_panel_groups_query_controls_and_uses_plain_calculate_action(self):
        window = self._make_window(1400, open_ai=True)

        self.assertEqual(window.assistant_query_panel.objectName(), "assistantQueryPanel")
        self.assertEqual(window.ai_live_preview.parentWidget(), window.assistant_query_panel)
        self.assertEqual(window.solve_button.text(), window._tr("calculate"))
        self.assertTrue(window.solve_button.icon().isNull())
        self.assertLessEqual(window.ai_input.maximumHeight(), 150)
        self.assertEqual(window.assistant_context.objectName(), "assistantContext")
        self.assertIn(window._tr("current_calculation"), window.assistant_context.text())
        self.assertEqual(window.settings_button.objectName(), "utilityButton")
        self.assertEqual(window.chatgpt_web_button.objectName(), "utilityButton")
        self.assertEqual(window.clear_ai_button.objectName(), "utilityButton")

    def test_assistant_context_tracks_the_current_calculation(self):
        window = self._make_window(1400, open_ai=True)

        window.expression = "2+2"
        window._update_display()
        self.app.processEvents()

        self.assertIn("2+2", window.assistant_context.text())
        self.assertIn("4", window.assistant_context.text())
        self.assertIn("2+2", window.assistant_example_buttons[0].text())

    def test_assistant_empty_state_examples_execute_and_then_hide(self):
        window = self._make_window(1400, open_ai=True)

        self.assertTrue(window.assistant_examples.isVisible())
        self.assertFalse(window.ai_result.isVisible())
        self.assertEqual(len(window.assistant_example_buttons), 3)

        window.assistant_example_buttons[0].click()
        self.app.processEvents()

        self.assertTrue(window.ai_messages)
        self.assertFalse(window.assistant_examples.isVisible())
        self.assertTrue(window.ai_result.isVisible())
        self.assertEqual(window.result_label.text(), "90")

        window._clear_ai_chat()
        self.app.processEvents()

        self.assertTrue(window.assistant_examples.isVisible())
        self.assertFalse(window.ai_result.isVisible())

    def test_local_icon_set_recolors_with_the_theme(self):
        window = self._make_window(1400, open_ai=True)
        graphite_key = window.header_settings_button.icon().cacheKey()

        window.theme_name = "light"
        window._apply_styles()
        light_key = window.header_settings_button.icon().cacheKey()

        self.assertFalse(window.header_settings_button.icon().isNull())
        self.assertFalse(window.history_button.icon().isNull())
        self.assertFalse(window.chatgpt_web_button.icon().isNull())
        self.assertFalse(window.clear_ai_button.icon().isNull())
        self.assertNotEqual(graphite_key, light_key)

    def test_theme_defines_focus_and_primary_operator_states(self):
        stylesheet = self._make_window().styleSheet()

        self.assertIn("QPushButton:focus", stylesheet)
        self.assertIn("border: 2px solid", stylesheet)
        self.assertIn('QPushButton[role="operator"][primaryOperator="true"]', stylesheet)

    def test_scientific_button_groups_do_not_override_semantic_roles(self):
        stylesheet = self._make_window().styleSheet()

        self.assertNotIn('QPushButton[scientificGroup="entry"] {\n            background:', stylesheet)
        self.assertIn('QPushButton[scientificGroup="memory"][role="memory"]', stylesheet)
        self.assertIn('QPushButton[scientificGroup="power"][role="function"]', stylesheet)
        self.assertIn('QPushButton[scientificGroup="trig"][role="function"]', stylesheet)
        self.assertIn('QPushButton[scientificGroup="complex"][role="function"]', stylesheet)
        self.assertIn('QFrame#mainPanel[scientific="true"] QPushButton[role="clear"]', stylesheet)
        self.assertIn('QFrame#mainPanel[scientific="true"] QPushButton[role="operator"][primaryOperator="true"]', stylesheet)
        self.assertIn('QFrame#mainPanel[scientific="true"] QPushButton[role="equal"]', stylesheet)

    def test_assistant_toggle_uses_theme_button_states_instead_of_blue_override(self):
        stylesheet = self._make_window().styleSheet()

        self.assertNotIn('QPushButton#assistantToggleButton[assistantVisible="false"]', stylesheet)
        self.assertIn('QPushButton#assistantToggleButton[assistantVisible="true"]', stylesheet)
        self.assertIn('QPushButton#assistantToggleButton[assistantVisible="true"]:hover', stylesheet)
        self.assertIn("QPushButton#assistantToggleButton:pressed", stylesheet)
        self.assertIn('QPushButton[role="mode"][modeActive="true"]', stylesheet)

    def test_button_families_define_hover_and_pressed_feedback(self):
        stylesheet = self._make_window().styleSheet()
        selectors = (
            "QPushButton#iconButton",
            "QPushButton#assistantToggleButton",
            "QPushButton#exampleButton",
            'QPushButton[role="number"]',
            'QPushButton[role="operator"]',
            'QPushButton[role="function"]',
            'QPushButton[role="memory"]',
            'QPushButton[role="danger"]',
            'QPushButton[role="clear"]',
            'QPushButton[role="mode"]',
            'QPushButton[role="equal"]',
        )

        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertIn(f"{selector}:hover", stylesheet)
                self.assertIn(f"{selector}:pressed", stylesheet)

    def test_all_themes_keep_text_and_primary_actions_at_wcag_aa_contrast(self):
        for theme_name in ("graphite", "matrix", "high contrast", "light"):
            palette = theme_palette(theme_name)
            with self.subTest(theme=theme_name):
                self.assertGreaterEqual(self._contrast_ratio(palette["text"], palette["window"]), 4.5)
                self.assertGreaterEqual(self._contrast_ratio(palette["muted"], palette["panel"]), 4.5)
                self.assertGreaterEqual(self._contrast_ratio(palette["accent_text"], palette["accent"]), 4.5)

    def test_keyboard_focus_can_reach_visible_calculator_controls(self):
        window = self._make_window()
        ac_button = next(button for button in window.all_calc_buttons if button.property("baseLabel") == "AC")

        ac_button.setFocus(Qt.TabFocusReason)
        self.app.processEvents()

        self.assertTrue(ac_button.hasFocus())
        self.assertTrue(ac_button.focusPolicy() & Qt.TabFocus)

    def test_compact_density_hides_only_the_redundant_subtitle(self):
        window = self._make_window(open_ai=True)

        window.left_panel.resize(620, window.left_panel.height())
        window._refresh_density_state()
        self.assertTrue(window.left_panel.property("compact"))
        self.assertFalse(window.subtitle_label.isVisible())

        window.left_panel.resize(700, window.left_panel.height())
        window._refresh_density_state()
        self.assertFalse(window.left_panel.property("compact"))
        self.assertTrue(window.subtitle_label.isVisible())

    def test_scientific_density_is_distinct_from_ai_compact_density(self):
        window = self._make_window()

        self.assertFalse(window.left_panel.property("compact"))
        window.scientific_mode_button.click()
        self.app.processEvents()

        self.assertFalse(window.left_panel.property("compact"))
        self.assertTrue(window.left_panel.property("scientificDense"))
        self.assertFalse(window.subtitle_label.isVisible())

        window.basic_mode_button.click()
        self.app.processEvents()

        self.assertFalse(window.left_panel.property("scientificDense"))
        self.assertTrue(window.subtitle_label.isVisible())

    def test_top_bar_distinguishes_secondary_history_from_ai_toggle(self):
        window = self._make_window(1400, open_ai=True)

        self.assertEqual(window.history_button.objectName(), "utilityButton")
        self.assertEqual(window.ai_toggle_button.objectName(), "assistantToggleButton")
        self.assertIn(window._tr("hide_ai_panel"), window.ai_toggle_button.text())

    def test_preview_state_marks_errors_and_recovers_after_clear(self):
        window = self._make_window()

        window.expression = "1/0"
        window._evaluate()
        self.app.processEvents()

        self.assertEqual(window.result_label.text(), "ERROR")
        self.assertEqual(window.preview_label.property("state"), "error")

        window._clear_all()
        self.app.processEvents()

        self.assertEqual(window.result_label.text(), "0")
        self.assertEqual(window.preview_label.property("state"), "neutral")

    def test_header_settings_button_exists_for_collapsed_access(self):
        window = self._make_window()

        self.assertEqual(window.header_settings_button.objectName(), "iconButton")
        self.assertEqual(window.header_settings_button.toolTip(), window._tr("settings"))
        self.assertEqual(window.header_settings_button.text(), "")
        self.assertFalse(window.header_settings_button.icon().isNull())
        self.assertTrue(window.header_settings_button.isVisible())

        window._toggle_ai_panel()
        self.app.processEvents()

        self.assertFalse(window.header_settings_button.isVisible())

    def test_history_dialog_buttons_use_styled_object_names(self):
        window = self._make_window()

        self.assertEqual(window.history_dialog.export_button.objectName(), "ghostButton")
        self.assertEqual(window.history_dialog.clear_button.objectName(), "ghostButton")

    def test_settings_dialog_opens_non_modal(self):
        window = self._make_window()

        window._open_settings_dialog()
        self.app.processEvents()

        self.assertIsNotNone(window.settings_dialog)
        self.assertFalse(window.settings_dialog.isModal())
        self.assertTrue(window.settings_dialog.isVisible())

    def test_settings_dialog_controls_use_main_ui_style_hooks(self):
        dialog = AssistantSettingsDialog(language="de")
        self.addCleanup(dialog.close)

        self.assertEqual(dialog.language_select.objectName(), "modeSelect")
        self.assertEqual(dialog.theme_select.objectName(), "themeSelect")
        self.assertEqual(dialog.theme_select.itemData(0), "graphite")
        self.assertEqual(dialog.theme_select.itemData(2), "high contrast")
        self.assertEqual(dialog.mode_select.objectName(), "modeSelect")
        self.assertEqual(dialog.step_checkbox.objectName(), "stepCheck")
        self.assertEqual(dialog.context_checkbox.objectName(), "stepCheck")
        self.assertEqual(dialog.api_button.objectName(), "ghostButton")
        self.assertEqual(dialog.api_help_button.objectName(), "ghostButton")
        self.assertEqual(dialog.api_test_button.objectName(), "ghostButton")
        self.assertEqual(dialog.api_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertEqual(dialog.api_hint_label.objectName(), "helperLabel")
        self.assertEqual(dialog.api_button_grid.itemAtPosition(1, 0).widget(), dialog.api_test_button)
        self.assertEqual(dialog.tabs.objectName(), "settingsTabs")
        self.assertEqual(dialog.tabs.count(), 4)
        self.assertEqual(dialog.about_browser.objectName(), "aboutBrowser")
        self.assertEqual(dialog.check_updates_button.objectName(), "ghostButton")
        self.assertEqual(dialog.readme_button.objectName(), "ghostButton")
        self.assertEqual(dialog.findChildren(QTabWidget)[0], dialog.tabs)

    def test_settings_dialog_action_buttons_have_consistent_minimum_size(self):
        dialog = AssistantSettingsDialog(language="de")
        self.addCleanup(dialog.close)

        ok_button = dialog.dialog_buttons.button(QDialogButtonBox.Ok)
        cancel_button = dialog.dialog_buttons.button(QDialogButtonBox.Cancel)

        self.assertIsNotNone(ok_button)
        self.assertIsNotNone(cancel_button)
        self.assertGreaterEqual(ok_button.minimumWidth(), 136)
        self.assertGreaterEqual(cancel_button.minimumWidth(), 136)
        self.assertEqual(ok_button.objectName(), "primaryButton")
        self.assertEqual(cancel_button.objectName(), "ghostButton")
        self.assertEqual(ok_button.text(), dialog._tr("save_changes") if hasattr(dialog, "_tr") else "Änderungen speichern")
        self.assertEqual(cancel_button.text(), "Abbrechen")

    def test_auxiliary_dialogs_use_compact_screen_aware_minimum_sizes(self):
        settings = AssistantSettingsDialog(language="de")
        history = HistoryDialog(language="de")
        skills = SkillsDialog(language="de")
        self.addCleanup(settings.close)
        self.addCleanup(history.close)
        self.addCleanup(skills.close)

        self.assertLessEqual(settings.minimumWidth(), 520)
        self.assertLessEqual(settings.minimumHeight(), 480)
        self.assertLessEqual(history.minimumWidth(), 420)
        self.assertLessEqual(history.minimumHeight(), 420)
        self.assertLessEqual(skills.minimumWidth(), 520)
        self.assertLessEqual(skills.minimumHeight(), 460)


if __name__ == "__main__":
    unittest.main()
