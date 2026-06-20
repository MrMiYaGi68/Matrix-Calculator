# SPDX-License-Identifier: GPL-3.0-or-later
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QSizePolicy, QTabWidget

from calculator import MatrixCalculatorWindow
from ui.dialogs import AssistantSettingsDialog


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

        for widget in (window.layout_button, window.history_button, window.ai_toggle_button):
            self.assertGreaterEqual(widget.width(), widget.sizeHint().width())

    def test_toolbar_buttons_use_compact_non_expanding_horizontal_policies(self):
        window = self._make_window(1400, open_ai=True)

        self.assertNotEqual(window.layout_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertNotEqual(window.history_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)
        self.assertNotEqual(window.ai_toggle_button.sizePolicy().horizontalPolicy(), QSizePolicy.Expanding)

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


if __name__ == "__main__":
    unittest.main()
