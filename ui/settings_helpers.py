# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt

from ui.dialogs import AssistantSettingsDialog


Translator = Callable[[str], str]


def set_api_status_label(browser, state: str, text: str, *, format_rich_text: Callable[[str], str]) -> None:
    colors = {
        "neutral": ("#222934", "#36404d", "#e8edf5"),
        "info": ("#1f2d3a", "#35526b", "#dfefff"),
        "success": ("#203126", "#3e7d4f", "#e8fff0"),
        "warning": ("#332813", "#8d6a1d", "#fff4d8"),
        "error": ("#341f21", "#8c4a4a", "#ffe8e8"),
    }
    background, border, foreground = colors.get(state, colors["neutral"])
    browser.setHtml(format_rich_text(text))
    browser.setStyleSheet(
        "background:"
        + background
        + "; border: 1px solid "
        + border
        + "; color: "
        + foreground
        + "; border-radius: 14px; padding: 10px 12px; font-size: 14px;"
    )


def prepare_settings_dialog(
    dialog: AssistantSettingsDialog,
    *,
    current_mode_label: str,
    current_model_label: str,
    step_by_step: bool,
    use_context: bool,
    has_api_key: bool,
    translate: Translator,
    open_settings: Callable[[AssistantSettingsDialog], None],
    show_api_help: Callable[[], None],
    test_api: Callable[[AssistantSettingsDialog], None],
    populate_about: Callable[[AssistantSettingsDialog], None],
    check_updates: Callable[[AssistantSettingsDialog], None],
    open_readme: Callable[[], None],
    apply_dialog: Callable[[AssistantSettingsDialog], None],
    clear_dialog: Callable[[AssistantSettingsDialog], None],
    set_api_status: Callable[[object, str, str], None],
) -> None:
    dialog.setModal(False)
    dialog.setWindowModality(Qt.NonModal)
    dialog.mode_select.setCurrentText(current_mode_label)
    dialog.model_value_label.setText(current_model_label)
    dialog.step_checkbox.setChecked(step_by_step)
    dialog.context_checkbox.setChecked(use_context)
    dialog.api_button.clicked.connect(lambda: open_settings(dialog))
    dialog.api_help_button.clicked.connect(show_api_help)
    dialog.api_test_button.clicked.connect(lambda: test_api(dialog))
    if has_api_key:
        set_api_status(
            dialog.api_status_browser,
            "info",
            translate("api_status_key_saved_check").format(test_api=translate("test_api")),
        )
    else:
        set_api_status(
            dialog.api_status_browser,
            "neutral",
            translate("api_status_no_key_simple"),
        )
    populate_about(dialog)
    dialog.check_updates_button.clicked.connect(lambda: check_updates(dialog))
    dialog.readme_button.clicked.connect(open_readme)
    dialog.accepted.connect(lambda d=dialog: apply_dialog(d))
    dialog.finished.connect(lambda _result, d=dialog: clear_dialog(d))
