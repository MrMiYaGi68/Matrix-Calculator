# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem


def _set_preview(window, text: str, state: str = "neutral") -> None:
    if hasattr(window, "_set_preview_state"):
        window._set_preview_state(text, state)
    else:
        window.preview_label.setText(text)


def _set_ai_status(window, text: str, state: str = "neutral") -> None:
    if hasattr(window, "_set_ai_status"):
        window._set_ai_status(text, state)
    else:
        window.ai_status.setText(text)


def on_history_clicked(window, item: QListWidgetItem) -> None:
    expr, result = item.data(Qt.UserRole)
    window.expression = expr
    window.result_label.setText(result)
    _set_preview(window, window._tr("history_loaded"), "success")
    window.just_evaluated = False
    window._update_display()


def clear_history(window) -> None:
    window.history_items.clear()
    if window.history_dialog is not None:
        window.history_dialog.history_list.clear()
        window.history_dialog.info_label.setText(window._tr("no_history"))
    _set_preview(window, window._tr("history_cleared"), "neutral")


def open_history_dialog(window) -> None:
    if window.history_dialog is None:
        return
    if not window.history_items:
        window.history_dialog.info_label.setText(window._tr("no_history"))
    window.history_dialog.show()
    window.history_dialog.raise_()
    window.history_dialog.activateWindow()


def open_skills_dialog(window) -> None:
    if window.skills_dialog is None:
        return
    window.skills_dialog.show()
    window.skills_dialog.raise_()
    window.skills_dialog.activateWindow()


def open_chatgpt_in_app(window, query: str) -> bool:
    from ui.dialogs import ChatGPTWebDialog

    if window.chatgpt_web_dialog is None:
        window.chatgpt_web_dialog = ChatGPTWebDialog(window, window.app_language)
    loaded = window.chatgpt_web_dialog.load_query(query)
    if not loaded:
        return False
    window.chatgpt_web_dialog.show()
    window.chatgpt_web_dialog.raise_()
    window.chatgpt_web_dialog.activateWindow()
    return True


def open_chatgpt_web_for_current_query(window) -> None:
    query = window.ai_input.text().strip() or window.last_ai_query.strip()
    if not query:
        window._append_ai_message("system", window._tr("chatgpt_need_query"))
        return
    if window._open_chatgpt_in_app(query):
        _set_ai_status(window, window._tr("chatgpt_opened"), "success")
    else:
        window._append_ai_message("system", window._tr("chatgpt_unavailable_message"))
        _set_ai_status(window, window._tr("chatgpt_unavailable_status"), "warning")
