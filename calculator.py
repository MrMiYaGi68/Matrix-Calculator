#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
try:
    from PySide6.QtCore import QEvent, QSize, QThread, QTimer, Qt, QUrl, Signal
    from PySide6.QtGui import QAction, QDesktopServices, QIcon, QKeyEvent, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSplitter,
        QStyle,
        QTabWidget,
        QTextBrowser,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    QApplication = None

from core.expression_parser import CalculatorError
from core.assistant_flow import assistant_mode_label, normalize_assistant_mode, solve_natural_query
from core.calculator_logic import (
    append_text,
    apply_percent_input,
    balanced_expression,
    clear_all,
    current_numeric_value,
    evaluate_expression,
    handle_button,
    is_finite_number,
    last_top_level_operator,
    needs_implicit_multiply,
    prime_factorization_text,
    push_history,
    set_expression_and_evaluate,
    toggle_sign,
    try_prime_factorization,
    update_display,
)
from core.formatting import format_number, pretty_expression
from core.i18n import normalize_language, tr
from core.natural_query import (
    CLARIFICATION_EXPRESSION,
    build_live_query_preview,
    build_query_help,
    build_local_answer,
    extract_numbers,
    format_local_result,
    is_english_query,
    local_smalltalk_response,
    parse_interest_query,
    prepare_simple_expression,
    solve_interest_choice,
    solve_local_natural_query,
    translate_local_text,
    unit_factor,
)
from core.openai_support import (
    AUTO_OPENAI_MODEL_FALLBACK as DEFAULT_OPENAI_MODEL,
    choose_auto_openai_model,
    describe_openai_api_error,
    extract_openai_output_text,
    normalize_openai_model,
)
from core.openai_client import OpenAIClient
from core.openai_session import build_openai_input, perform_openai_request, resolve_openai_model
from core.settings import AppSettings, SettingsStore
from ui.settings_helpers import prepare_settings_dialog, set_api_status_label
from ui.history_actions import (
    clear_history,
    on_history_clicked,
    open_chatgpt_in_app,
    open_chatgpt_web_for_current_query,
    open_history_dialog,
    open_skills_dialog,
)
from ui.window_state import (
    available_content_window_width,
    collapsed_content_width,
    collapsed_window_height,
    current_screen_available_geometry,
    enforce_collapsed_window_state,
    enforce_collapsed_window_width,
    expanded_splitter_sizes,
    fit_window_to_available_screen,
    handle_change_event,
    last_expanded_splitter_sizes,
    refresh_ai_toggle_button,
    resize_and_center,
    set_ai_panel_visible,
    set_maximize_available,
    toggle_ai_panel,
)
from ui.window_builders import build_assistant_panel_content, build_auxiliary_dialogs, build_left_panel_content
from ui.button_config import (
    ADVANCED_ROWS,
    DEFAULT_THEME,
    SECOND_MODE_LABELS,
    button_shortcut_hint,
    button_tooltip_key,
)
from ui.dialogs import AssistantSettingsDialog, ChatGPTWebDialog, HistoryDialog, SkillsDialog
from ui.assistant_rendering import format_ai_message_html, format_rich_text_block, render_ai_chat_html
from ui.theme import build_stylesheet, theme_palette


class CalcButton(QPushButton):
    def __init__(self, text: str, role: str):
        super().__init__(text)
        self.role = role
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(54)
        self.setProperty("role", role)


class OpenAIWorker(QThread):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, query: str, model: str, parent: MatrixCalculatorWindow):
        super().__init__(parent)
        self.query = query
        self.model = model
        self.parent_window = parent

    def run(self):
        try:
            result = self.parent_window._perform_openai_request(self.query, self.model)
            self.finished.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class MatrixCalculatorWindow(QMainWindow):
    QEVENT_WINDOW_STATE_CHANGE = QEvent.WindowStateChange
    PROJECT_ROOT = Path(__file__).resolve().parent
    CONFIG_PATH = Path.home() / ".config" / "matrix-calculator" / "settings.json"
    README_PATH = PROJECT_ROOT / "README.md"
    CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"
    PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
    AUTO_OPENAI_MODEL_FALLBACK = DEFAULT_OPENAI_MODEL
    COLLAPSED_WINDOW_WIDTH = 780
    COLLAPSED_MINIMUM_WIDTH = 760
    COLLAPSED_WINDOW_HEIGHT = 900
    EXPANDED_WINDOW_WIDTH = 1400
    EXPANDED_MINIMUM_WIDTH = 1180
    WINDOW_MINIMUM_HEIGHT = 800
    LEFT_PANEL_WIDTH = 700
    RIGHT_PANEL_MINIMUM_WIDTH = 560
    DEFAULT_AI_PANEL_WIDTH = 700
    OUTER_HORIZONTAL_MARGIN = 32
    SPLITTER_HANDLE_WIDTH = 10
    SCREEN_EDGE_MARGIN = 24
    WINDOW_FRAME_SAFETY_MARGIN = 120

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Matrix KI Taschenrechner")
        self.resize(self.EXPANDED_WINDOW_WIDTH, 920)
        self.setMinimumSize(self.EXPANDED_MINIMUM_WIDTH, self.WINDOW_MINIMUM_HEIGHT)

        self.expression = ""
        self.memory = 0.0
        self.degrees = True
        self.second_mode = False
        self.scientific_mode = False
        self.just_evaluated = False
        self.history_items: list[tuple[str, str]] = []
        self.ai_api_key = ""
        self.ai_model = "gpt-5-mini"
        self.assistant_mode = "browser_fallback"
        self.app_language = "de"
        self.ai_step_by_step = True
        self.ai_messages: list[tuple[str, str]] = []
        self.ai_use_context = False
        self.online_ai_transfer_confirmed = False
        self.theme_name = DEFAULT_THEME
        self.ai_panel_visible = True
        self._last_ai_panel_width = self.DEFAULT_AI_PANEL_WIDTH
        self.history_dialog: HistoryDialog | None = None
        self.skills_dialog: SkillsDialog | None = None
        self.chatgpt_web_dialog: ChatGPTWebDialog | None = None
        self.settings_dialog: AssistantSettingsDialog | None = None
        self.last_ai_query = ""
        self.pending_clarification: dict[str, object] | None = None
        self.ai_worker: OpenAIWorker | None = None

        self.second_pairs = dict(SECOND_MODE_LABELS)
        self.toggle_buttons: dict[str, CalcButton] = {}
        self.row_groups: dict[int, list[QWidget]] = {}
        self.all_calc_buttons: list[CalcButton] = []
        self.advanced_rows = set(ADVANCED_ROWS)

        self._build_ui()
        self._build_shortcuts()
        self._apply_styles()
        self._load_settings()
        self._apply_language()
        self._refresh_mode_labels()
        self._refresh_layout_mode()
        self._update_display()
        self._set_ai_panel_visible(False, resize_window=True)
        self._set_maximize_available(False)

    def _button_shortcut_hint(self, label: str) -> str | None:
        return button_shortcut_hint(label)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        self.outer_layout = QVBoxLayout(root)
        self.outer_layout.setContentsMargins(16, 16, 16, 16)
        self.outer_layout.setSpacing(12)

        self.left_panel = QFrame()
        self.left_panel.setObjectName("mainPanel")
        self.left_panel.setMinimumWidth(560)
        self.left_panel.setMaximumWidth(16777215)
        self.left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(12)

        self.right_panel = QFrame()
        self.right_panel.setObjectName("sidePanel")
        self.right_panel.setMinimumWidth(self.RIGHT_PANEL_MINIMUM_WIDTH)
        self.right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)

        self.content_splitter = QSplitter(Qt.Horizontal)
        self.content_splitter.setChildrenCollapsible(False)
        self.content_splitter.setHandleWidth(self.SPLITTER_HANDLE_WIDTH)
        self.content_splitter.addWidget(self.left_panel)
        self.content_splitter.addWidget(self.right_panel)
        self.content_splitter.setStretchFactor(0, 1)
        self.content_splitter.setStretchFactor(1, 1)
        self.content_splitter.setSizes(self._expanded_splitter_sizes())
        self._last_ai_splitter_sizes = self._expanded_splitter_sizes()
        self.outer_layout.addWidget(self.content_splitter, 1)

        build_left_panel_content(self, left_layout, button_class=CalcButton)
        build_assistant_panel_content(self, right_layout)
        build_auxiliary_dialogs(self)

    def _build_shortcuts(self) -> None:
        clear_action = QAction(self)
        clear_action.setShortcut("Escape")
        clear_action.triggered.connect(self._clear_all)
        self.addAction(clear_action)

    def _apply_styles(self) -> None:
        self.setStyleSheet(build_stylesheet(self.theme_name))
        self._refresh_chip_styles()

    def _theme_palette(self) -> dict[str, str]:
        return theme_palette(getattr(self, "theme_name", DEFAULT_THEME))

    def _change_theme(self, label: str) -> None:
        self.theme_name = label.strip().lower() or DEFAULT_THEME
        self._apply_styles()
        self._render_ai_chat()
        if self.settings_dialog is not None:
            self._populate_about_tab(self.settings_dialog)
        self._save_settings()

    def _theme_display_name(self) -> str:
        labels = {
            "graphite": "Graphite",
            "matrix": "Matrix",
            "high contrast": "High Contrast",
            "light": "Light",
        }
        return labels.get(self.theme_name, "Graphite")

    def _set_visual_state(self, widget, state: str) -> None:
        if not hasattr(widget, "setProperty"):
            return
        widget.setProperty("state", state)
        if not hasattr(widget, "style"):
            return
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _set_preview_state(self, text: str, state: str = "neutral") -> None:
        self.preview_label.setText(text)
        self._set_visual_state(self.preview_label, state)

    def _set_ai_status(self, text: str, state: str = "neutral") -> None:
        self.ai_status.setText(text)
        self._set_visual_state(self.ai_status, state)

    def _set_ai_preview(self, text: str, state: str = "neutral") -> None:
        self.ai_live_preview.setText(text)
        self._set_visual_state(self.ai_live_preview, state)

    def _button_role(self, label: str) -> str:
        if label == "AC":
            return "clear"
        if label == "=":
            return "equal"
        if label in {"+", "-", "×", "÷", "%", "xʸ", "mod"}:
            return "operator"
        if label in {"CE", "⌫"}:
            return "danger"
        if label in {"mc", "mr", "m+", "m-", "ms", "Ans"}:
            return "memory"
        if label in {"2nd", "Deg", "Rad"}:
            return "mode"
        if label in {"sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "ln", "log", "e^x", "10^x", "sqrt", "cbrt", "x²", "x³", "1/x", "|x|", "n!", "Rand", "π", "e", "i", "Re", "Im", "pf"}:
            return "function"
        return "number"

    def _make_chip(self, text: str, variant: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("chip", True)
        label.setProperty("variant", variant)
        return label

    def _refresh_chip_styles(self) -> None:
        colors = self._theme_palette()
        chip_colors = {
            "accent": (colors["chip_accent"], colors["text"]),
            "good": (colors["chip_good"], colors["text"]),
            "warm": (colors["chip_warm"], colors["accent_text"]),
        }
        for label in (self.smart_chip, self.mode_chip, self.memory_chip):
            variant = label.property("variant") or "accent"
            bg, fg = chip_colors.get(variant, chip_colors["accent"])
            label.setStyleSheet(f"background:{bg}; color:{fg};")

    def _refresh_mode_labels(self) -> None:
        for base, button in self.toggle_buttons.items():
            label = self.second_pairs[base] if self.second_mode else base
            button.setText(label)
        self.mode_toggle_button.setText("Deg" if self.degrees else "Rad")
        self.mode_chip.setText("DEG" if self.degrees else "RAD")
        self.memory_chip.setText(f"M {self._format_number(self.memory)}")
        self.memory_chip.setVisible(abs(self.memory) > 1e-12)
        self._refresh_basic_symbol_buttons()

    def _refresh_layout_mode(self) -> None:
        for row_index, widgets in self.row_groups.items():
            visible = self.scientific_mode or row_index not in self.advanced_rows
            if hasattr(self, "controls_grid"):
                self.controls_grid.setRowStretch(row_index, 1 if visible else 0)
            for widget in widgets:
                widget.setVisible(visible)
                if isinstance(widget, CalcButton):
                    if self.scientific_mode:
                        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        widget.setMinimumHeight(46)
                        widget.setMaximumHeight(16777215)
                    else:
                        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        widget.setMinimumHeight(54)
                        widget.setMaximumHeight(16777215)
        if hasattr(self, "controls_grid") and hasattr(self, "controls_layout"):
            grid_spacing = 10
            outer_margin = 6 if self.scientific_mode else 0
            self.controls_grid.setHorizontalSpacing(grid_spacing)
            self.controls_grid.setVerticalSpacing(grid_spacing)
            self.controls_grid.setContentsMargins(outer_margin, outer_margin, outer_margin, outer_margin)
            self.controls_layout.setAlignment(Qt.Alignment() if self.scientific_mode else Qt.AlignCenter)
        if hasattr(self, "basic_mode_button"):
            self.basic_mode_button.setText(self._tr("basic_layout"))
            self.basic_mode_button.setChecked(not self.scientific_mode)
        if hasattr(self, "scientific_mode_button"):
            self.scientific_mode_button.setText(self._tr("scientific_layout"))
            self.scientific_mode_button.setChecked(self.scientific_mode)
        self._refresh_basic_symbol_buttons()

    def _refresh_basic_symbol_buttons(self) -> None:
        symbol_labels = {"(", ")", "%", "+/-", "÷", "×", "-", "+", "=", ".", "AC", "CE", "⌫"}
        for button in getattr(self, "all_calc_buttons", []):
            base_label = button.property("baseLabel") or button.text()
            is_basic_symbol = (not self.scientific_mode) and (base_label in symbol_labels)
            if button.property("basicSymbol") == is_basic_symbol:
                continue
            button.setProperty("basicSymbol", is_basic_symbol)
            button.style().unpolish(button)
            button.style().polish(button)

    def _set_layout_mode(self, scientific: bool) -> None:
        self.scientific_mode = scientific
        self._set_preview_state(self._tr("scientific_layout_active") if scientific else self._tr("basic_layout_active"), "info")
        self._refresh_layout_mode()

    def _tr(self, key: str) -> str:
        return tr(getattr(self, "app_language", "de"), key)

    def _apply_language(self) -> None:
        self.app_language = normalize_language(getattr(self, "app_language", "de"))
        self.setWindowTitle(self._tr("app_title"))
        self.title_label.setText(self._tr("title_html"))
        self.subtitle_label.setText(self._tr("subtitle"))
        if hasattr(self, "header_settings_button"):
            self.header_settings_button.setToolTip(self._tr("settings"))
        self.history_button.setText(self._tr("history"))
        if hasattr(self, "smart_chip"):
            self.smart_chip.setText(self._tr("local_chip"))
        if hasattr(self, "basic_mode_button"):
            self.basic_mode_button.setText(self._tr("basic_layout"))
        if hasattr(self, "scientific_mode_button"):
            self.scientific_mode_button.setText(self._tr("scientific_layout"))
        self.ai_title.setText(self._tr("assistant_title_html"))
        self.ai_input.setPlaceholderText(self._tr("query_placeholder"))
        self.ai_result.setPlaceholderText(self._tr("assistant_output_placeholder"))
        self.solve_button.setText(self._tr("calculate"))
        self.settings_button.setText(self._tr("settings"))
        if hasattr(self, "chatgpt_web_button"):
            self.chatgpt_web_button.setText(self._tr("chatgpt_web"))
        self.clear_ai_button.setText(self._tr("clear_ai_history"))
        self._refresh_ai_toggle_button()
        if not self.ai_messages:
            self._set_ai_status(self._tr("ready_local"), "neutral")
            self._set_ai_preview(self._tr("live_preview_empty"), "neutral")
        self.mode_preference.clear()
        self.mode_preference.addItems([self._tr("mode_browser"), self._tr("mode_api")])
        self.mode_preference.setCurrentText(self._assistant_mode_label())
        self.step_checkbox.setText(self._tr("step_by_step"))
        self.context_checkbox.setText(self._tr("chat_context"))
        if not self.expression:
            self._set_preview_state(self._tr("ready_input"), "neutral")
        self._refresh_button_tooltips()
        self._recreate_localized_dialogs()
        self._refresh_layout_mode()
        self._render_ai_chat()

    def _refresh_button_tooltips(self) -> None:
        for button in getattr(self, "all_calc_buttons", []):
            base_label = button.property("baseLabel") or button.text()
            shortcut_hint = self._button_shortcut_hint(base_label)
            tooltip_key = button_tooltip_key(base_label)
            if tooltip_key:
                button.setToolTip(self._tr(tooltip_key))
            elif shortcut_hint:
                button.setToolTip(shortcut_hint)
            else:
                button.setToolTip("")

    def _recreate_localized_dialogs(self) -> None:
        for dialog_attr in ["history_dialog", "skills_dialog", "chatgpt_web_dialog"]:
            old_dialog = getattr(self, dialog_attr, None)
            if old_dialog:
                old_dialog.deleteLater()

        self.history_dialog = HistoryDialog(self, self.app_language)
        self.history_dialog.history_list.itemClicked.connect(self._on_history_clicked)
        self.history_dialog.export_button.clicked.connect(self._export_history)
        self.history_dialog.clear_button.clicked.connect(self._clear_history)
        for expr, value in self.history_items:
            item = QListWidgetItem(f"{self._pretty_expression(expr)} = {value}")
            item.setData(Qt.UserRole, (expr, value))
            self.history_dialog.history_list.addItem(item)
        if not self.history_items:
            self.history_dialog.info_label.setText(self._tr("no_history"))
        self.skills_dialog = SkillsDialog(self, self.app_language)
        self.chatgpt_web_dialog = None

    def _toggle_layout_mode(self) -> None:
        self._set_layout_mode(not self.scientific_mode)

    def _toggle_ai_panel(self) -> None:
        toggle_ai_panel(self)

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        handle_change_event(self, event.type())

    def closeEvent(self, event: QEvent) -> None:
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait()
        super().closeEvent(event)

    def _set_ai_panel_visible(self, visible: bool, resize_window: bool = True) -> None:
        set_ai_panel_visible(self, visible, resize_window)

    def _set_maximize_available(self, available: bool) -> None:
        set_maximize_available(self, available)

    def _enforce_collapsed_window_state(self) -> None:
        enforce_collapsed_window_state(self)

    def _enforce_collapsed_window_width(self) -> None:
        enforce_collapsed_window_width(self)

    def _collapsed_content_width(self) -> int:
        return collapsed_content_width(self)

    def _collapsed_window_height(self) -> int:
        return collapsed_window_height(self)

    def _expanded_splitter_sizes(self) -> list[int]:
        return expanded_splitter_sizes(self)

    def _last_expanded_splitter_sizes(self) -> list[int]:
        return last_expanded_splitter_sizes(self)

    def _refresh_ai_toggle_button(self) -> None:
        refresh_ai_toggle_button(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_ai_toggle_button()

    def _current_screen_available_geometry(self):
        return current_screen_available_geometry(self)

    def _resize_and_center(self, width: int, height: int) -> None:
        resize_and_center(self, width, height)

    def _fit_window_to_available_screen(self) -> None:
        fit_window_to_available_screen(self)

    def _available_content_window_width(self, available) -> int:
        return available_content_window_width(self, available)

    def _handle_button(self, label: str) -> None:
        handle_button(self, label)

    def _append(self, text: str, source_label: str | None = None) -> None:
        append_text(self, text, source_label)

    def _clear_all(self) -> None:
        clear_all(self)

    def _set_expression_and_evaluate(self, expression: str) -> None:
        set_expression_and_evaluate(self, expression)

    def _toggle_sign(self) -> None:
        toggle_sign(self)

    def _evaluate(self) -> None:
        evaluate_expression(self)

    def _update_display(self) -> None:
        update_display(self)

    def _balanced_expression(self, text: str) -> str:
        return balanced_expression(text)

    def _try_prime_factorization(self, expression: str) -> str | None:
        return try_prime_factorization(self, expression)

    def _prime_factorization_text(self, value: float | complex) -> str:
        return prime_factorization_text(self, value)

    def _is_finite_number(self, value: float | complex) -> bool:
        return is_finite_number(value)

    def _needs_implicit_multiply(self, text: str, source_label: str | None = None) -> bool:
        return needs_implicit_multiply(self, text, source_label)

    def _apply_percent_input(self) -> None:
        apply_percent_input(self)

    def _last_top_level_operator(self, text: str) -> tuple[int | None, str | None]:
        return last_top_level_operator(text)

    def _current_numeric_value(self) -> float:
        return current_numeric_value(self)

    def _push_history(self, expression: str, result: str) -> None:
        push_history(self, expression, result)

    def _on_history_clicked(self, item: QListWidgetItem) -> None:
        on_history_clicked(self, item)

    def _clear_history(self) -> None:
        clear_history(self)

    def _open_history_dialog(self) -> None:
        open_history_dialog(self)

    def _open_skills_dialog(self) -> None:
        open_skills_dialog(self)

    def _normalize_assistant_mode(self, text: str) -> str:
        return normalize_assistant_mode(text)

    def _assistant_mode_label(self, mode: str | None = None) -> str:
        return assistant_mode_label(mode, active_mode=self.assistant_mode, translate=self._tr)

    def _open_chatgpt_in_app(self, query: str) -> bool:
        return open_chatgpt_in_app(self, query)

    def _open_chatgpt_web_for_current_query(self) -> None:
        open_chatgpt_web_for_current_query(self)

    def _solve_natural_query(self) -> None:
        solve_natural_query(self)

    def _extract_numbers(self, text: str) -> list[float]:
        return extract_numbers(text)

    def _update_ai_live_preview(self, text: str) -> None:
        self._set_ai_preview(self._build_live_query_preview(text), "info" if text.strip() else "neutral")

    def _build_live_query_preview(self, query: str) -> str:
        return build_live_query_preview(
            query,
            local_solver=self._solve_local_natural_query,
            pretty_expression=self._pretty_expression,
            format_number=self._format_number,
        )

    def _is_english_query(self, query: str) -> bool:
        return is_english_query(query)

    def _translate_local_text(self, text: str, english: bool) -> str:
        return translate_local_text(text, english)

    def _build_query_help(self, query: str) -> str:
        return build_query_help(query, format_number=self._format_number)

    def _build_local_answer(self, query: str, expression: str, answer: str, explanation: str) -> str:
        language = "en" if getattr(self, "app_language", "de") == "en" else None
        return build_local_answer(query, expression, answer, explanation, self.ai_step_by_step, language)

    def _remember_pending_clarification(self, query: str, expression: str, answer: str, explanation: str) -> None:
        if expression != CLARIFICATION_EXPRESSION or "Zins" not in answer:
            self.pending_clarification = None
            return
        parsed = parse_interest_query(query.lower().strip().replace(",", "."))
        if parsed is None:
            self.pending_clarification = None
            return
        capital, rate, years = parsed
        self.pending_clarification = {
            "type": "interest",
            "capital": capital,
            "rate": rate,
            "years": years,
        }

    def _resolve_pending_clarification(self, query: str) -> tuple[str, str, str] | None:
        pending = getattr(self, "pending_clarification", None)
        if not pending:
            return None
        if pending.get("type") != "interest":
            self.pending_clarification = None
            return None
        result = solve_interest_choice(
            float(pending["capital"]),
            float(pending["rate"]),
            float(pending["years"]),
            query,
        )
        if result is None:
            return (
                CLARIFICATION_EXPRESSION,
                "Ich brauche noch eine eindeutige Auswahl.",
                "Bitte antworte mit 'Zinsbetrag', 'Endbetrag' oder 'Zinseszins'.",
            )
        self.pending_clarification = None
        return result.as_tuple()

    def _format_local_result(self, expression: str, value: float, explanation: str) -> tuple[str, str, str]:
        return format_local_result(expression, value, explanation)

    def _unit_factor(self, unit: str) -> float | None:
        return unit_factor(unit)

    def _local_smalltalk_response(self, query: str) -> tuple[str, str, str] | None:
        return local_smalltalk_response(query)

    def _prepare_simple_expression(self, text: str) -> str:
        return prepare_simple_expression(text)

    def _solve_local_natural_query(self, query: str) -> tuple[str, str, str] | None:
        return solve_local_natural_query(
            query,
            degrees=getattr(self, "degrees", True),
            format_number=self._format_number,
        )

    def _normalize_openai_model(self, model: str) -> str:
        return normalize_openai_model(model)

    def _choose_auto_openai_model(self, available_models: list[str]) -> str:
        return choose_auto_openai_model(available_models)

    def _openai_api_help_text(self) -> str:
        return self._tr("openai_api_help_text")

    def _show_openai_api_help(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr("api_help"))
        dialog.resize(620, 520)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel(self._tr("api_help_title"))
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        browser = QTextBrowser()
        browser.setObjectName("apiStatusBrowser")
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._format_rich_text_block(self._openai_api_help_text()))
        layout.addWidget(browser, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_button = buttons.button(QDialogButtonBox.Close)
        if close_button is not None:
            close_button.setObjectName("ghostButton")
            close_button.setAutoDefault(False)
            close_button.setDefault(False)
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()

    def _format_rich_text_block(self, text: str) -> str:
        return format_rich_text_block(text)

    def _set_api_status_label(self, browser: QTextBrowser, state: str, text: str) -> None:
        set_api_status_label(
            browser,
            state,
            text,
            format_rich_text=self._format_rich_text_block,
        )

    def _openai_request_headers(self, api_key: str) -> dict[str, str]:
        return OpenAIClient(api_key).headers()

    def _extract_openai_output_text(self, data: dict) -> str:
        return extract_openai_output_text(data)

    def _fetch_available_openai_models(self, api_key: str) -> list[str]:
        return OpenAIClient(api_key).fetch_available_models()

    def _describe_openai_api_error(self, status_code: int | None, payload: dict | None = None) -> str:
        return describe_openai_api_error(status_code, payload)

    def _resolve_openai_model(self) -> str:
        api_key = (self.ai_api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        resolved = resolve_openai_model(api_key, self.AUTO_OPENAI_MODEL_FALLBACK)
        self.ai_model = resolved
        return resolved

    def _perform_openai_request(self, query: str, model: str | None = None, max_output_tokens: int = 220) -> str:
        api_key = (self.ai_api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        chosen_model = model or self._resolve_openai_model()
        return perform_openai_request(
            api_key,
            query_input=self._build_openai_input(query),
            model=chosen_model,
            response_language=self._tr("openai_response_language"),
            step_by_step=self.ai_step_by_step,
            max_output_tokens=max_output_tokens,
            missing_key_error=self._tr("openai_missing_key_error"),
            requests_missing_error=self._tr("requests_missing"),
            empty_response_error=self._tr("openai_empty_response"),
        )

    def _test_openai_api(self, dialog: AssistantSettingsDialog) -> None:
        if not (self.ai_api_key or os.getenv("OPENAI_API_KEY", "")).strip():
            self._set_api_status_label(
                dialog.api_status_browser,
                "warning",
                self._tr("api_status_missing"),
            )
            return

        chosen_model = self._resolve_openai_model()
        dialog.model_value_label.setText(self._tr("auto_detected_model").format(model=chosen_model))
        self._set_api_status_label(
            dialog.api_status_browser,
            "info",
            self._tr("api_status_testing").format(model=chosen_model),
        )
        QApplication.processEvents()

        try:
            answer = self._perform_openai_request("Antworte nur mit dem Wort OK.", chosen_model, max_output_tokens=20)
            self._set_api_status_label(
                dialog.api_status_browser,
                "success",
                self._tr("api_status_success").format(answer=answer),
            )
            self._set_ai_status(self._tr("openai_test_success").format(model=chosen_model), "success")
        except CalculatorError as exc:
            message = str(exc)
            state = "warning" if "Billing" in message or "Guthaben" in message or "Limit" in message else "error"
            self._set_api_status_label(dialog.api_status_browser, state, self._tr("api_status_error").format(message=message))
            self._set_ai_status(self._tr("openai_test_failed"), state)

    def _configure_openai(self, dialog: AssistantSettingsDialog | None = None) -> None:
        value, ok = QInputDialog.getText(
            self,
            self._tr("api_key_dialog_title"),
            self._tr("api_key_dialog_text"),
            QLineEdit.Password,
            self.ai_api_key or os.getenv("OPENAI_API_KEY", ""),
        )
        if ok:
            self.ai_api_key = value.strip()
            if self.ai_api_key:
                self._append_ai_message(
                    "system",
                    self._tr("api_key_saved_message").format(model=self.ai_model, test_api=self._tr("test_api"))
                )
                self._set_ai_status(self._tr("api_key_saved_status"), "success")
                if dialog is not None:
                    self._set_api_status_label(
                        dialog.api_status_browser,
                        "info",
                        self._tr("api_status_key_saved").format(test_api=self._tr("test_api")),
                    )
            else:
                self._append_ai_message(
                    "system",
                    self._tr("api_key_missing_message")
                )
                self._set_ai_status(self._tr("local_assistant_only"), "neutral")
                if dialog is not None:
                    self._set_api_status_label(
                        dialog.api_status_browser,
                        "neutral",
                        self._tr("api_status_no_key_web"),
                    )

    def _open_settings_dialog(self) -> None:
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return

        dialog = AssistantSettingsDialog(self, self.app_language)
        self.settings_dialog = dialog
        prepare_settings_dialog(
            dialog,
            current_mode_label=self._assistant_mode_label(),
            current_model_label=f"{self._tr('automatic')}: {self._normalize_openai_model(self.ai_model)}",
            step_by_step=self.ai_step_by_step,
            use_context=self.ai_use_context,
            has_api_key=bool(self.ai_api_key or os.getenv("OPENAI_API_KEY", "")),
            translate=self._tr,
            open_settings=self._configure_openai,
            show_api_help=self._show_openai_api_help,
            test_api=self._test_openai_api,
            populate_about=self._populate_about_tab,
            check_updates=self._check_for_updates,
            open_readme=self._open_readme,
            apply_dialog=self._apply_settings_dialog,
            clear_dialog=self._clear_settings_dialog,
            set_api_status=self._set_api_status_label,
            current_theme_label=self._theme_display_name(),
        )
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _apply_settings_dialog(self, dialog: AssistantSettingsDialog) -> None:
        selected_language = dialog.language_select.currentData()
        self.app_language = normalize_language(selected_language)
        self.theme_name = dialog.theme_select.currentText().strip().lower() or DEFAULT_THEME
        self._apply_styles()
        self._render_ai_chat()
        self.assistant_mode = self._normalize_assistant_mode(dialog.mode_select.currentText())
        self.mode_preference.setCurrentText(self._assistant_mode_label())
        self.step_checkbox.setChecked(dialog.step_checkbox.isChecked())
        self.context_checkbox.setChecked(dialog.context_checkbox.isChecked())
        self._save_settings()
        self._apply_language()
        self._set_ai_status(self._tr("settings_updated"), "success")

    def _clear_settings_dialog(self, dialog: AssistantSettingsDialog) -> None:
        if self.settings_dialog is dialog:
            self.settings_dialog = None

    def _ask_openai(self, query: str | None = None) -> None:
        if self.ai_worker and self.ai_worker.isRunning():
            return

        query = (query or self.ai_input.text()).strip()
        if not query:
            self._append_ai_message("system", self._tr("enter_query"))
            return
        if not self._confirm_online_ai_transfer():
            self._append_ai_message("system", self._tr("online_ai_transfer_cancelled"))
            self._set_ai_status(self._tr("online_ai_transfer_cancelled_status"), "warning")
            return
        api_key = self.ai_api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            self._append_ai_message(
                "system",
                self._tr("online_api_missing_key_message")
            )
            self._append_ai_message("system", self._build_query_help(query))
            self._set_ai_status(self._tr("online_api_missing_key_status"), "warning")
            return

        chosen_model = self._resolve_openai_model()
        self._save_settings()

        self._set_ai_status(self._tr("openai_responding").format(model=chosen_model), "info")
        self.solve_button.setEnabled(False)
        self.ai_input.setEnabled(False)

        self.ai_worker = OpenAIWorker(query, chosen_model, self)
        self.ai_worker.finished.connect(lambda text: self._on_openai_finished(text, chosen_model))
        self.ai_worker.failed.connect(self._on_openai_failed)
        self.ai_worker.start()

    def _on_openai_finished(self, output_text: str, model: str) -> None:
        self.solve_button.setEnabled(True)
        self.ai_input.setEnabled(True)
        self._append_ai_message("assistant", output_text or self._tr("openai_empty_response"))
        self._set_ai_status(self._tr("openai_answer_received").format(model=model), "success")
        self.ai_worker = None

    def _on_openai_failed(self, error: str) -> None:
        self.solve_button.setEnabled(True)
        self.ai_input.setEnabled(True)
        self._append_ai_message("system", self._tr("openai_request_failed_message").format(error=error))
        self._set_ai_status(self._tr("openai_request_failed_status"), "error")
        self.ai_worker = None

    def _confirm_online_ai_transfer(self) -> bool:
        if self.online_ai_transfer_confirmed:
            return True
        message = QMessageBox(self)
        message.setIcon(QMessageBox.Warning)
        message.setWindowTitle(self._tr("online_ai_transfer_title"))
        message.setText(self._tr("online_ai_transfer_text"))
        message.setInformativeText(self._tr("online_ai_transfer_details"))
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.setDefaultButton(QMessageBox.No)
        if message.exec() != QMessageBox.Yes:
            return False
        self.online_ai_transfer_confirmed = True
        return True

    def _load_settings(self) -> None:
        store = SettingsStore(self.CONFIG_PATH)
        self.ai_api_key = store.session_api_key()
        data = store.read()
        if not data:
            self.mode_preference.setCurrentText(self._assistant_mode_label())
            self.step_checkbox.setChecked(self.ai_step_by_step)
            self.context_checkbox.setChecked(self.ai_use_context)
            return
        self.ai_model = self._normalize_openai_model(data.get("openai_model", self.ai_model))
        self.app_language = normalize_language(data.get("app_language", self.app_language))
        self.assistant_mode = self._normalize_assistant_mode(data.get("assistant_mode", self._assistant_mode_label()))
        self.ai_step_by_step = data.get("ai_step_by_step", self.ai_step_by_step)
        self.ai_use_context = data.get("ai_use_context", self.ai_use_context)
        theme_name = data.get("theme_name", self.theme_name)
        self.theme_name = theme_name.strip().lower() if isinstance(theme_name, str) else DEFAULT_THEME
        self.mode_preference.setCurrentText(self._assistant_mode_label())
        self.step_checkbox.setChecked(self.ai_step_by_step)
        self.context_checkbox.setChecked(self.ai_use_context)
        self._apply_styles()

    def _save_settings(self) -> None:
        SettingsStore(self.CONFIG_PATH).write(
            AppSettings(
                openai_model=self._normalize_openai_model(self.ai_model),
                assistant_mode=self._assistant_mode_label(self.assistant_mode),
                app_language=normalize_language(self.app_language),
                ai_step_by_step=self.ai_step_by_step,
                ai_use_context=self.ai_use_context,
                theme_name=self.theme_name,
            )
        )

    def _toggle_step_mode(self, enabled: bool) -> None:
        self.ai_step_by_step = enabled
        self._save_settings()
        self._set_ai_status(self._tr("step_mode_on") if enabled else self._tr("step_mode_off"), "info")

    def _toggle_context_mode(self, enabled: bool) -> None:
        self.ai_use_context = enabled
        self._save_settings()
        self._set_ai_status(self._tr("context_mode_on") if enabled else self._tr("context_mode_off"), "info")

    def _append_ai_message(self, role: str, text: str) -> None:
        self.ai_messages.append((role, text))
        self.ai_messages = self.ai_messages[-24:]
        self._render_ai_chat()

    def _format_ai_message_html(self, role: str, text: str) -> str:
        colors = self._assistant_rich_text_colors()
        return format_ai_message_html(role, text, colors)

    def _clear_ai_chat(self) -> None:
        self.ai_messages.clear()
        self.ai_result.clear()
        self._set_ai_status(self._tr("ai_history_cleared"), "neutral")

    def _render_ai_chat(self) -> None:
        if not hasattr(self, "ai_result") or not hasattr(self.ai_result, "setHtml"):
            return
        colors = self._theme_palette()
        labels = {
            "user": (self._tr("chat_role_user"), colors["blue"], "#ffffff", "right"),
            "assistant": (self._tr("chat_role_assistant"), colors["raised"], colors["text"], "left"),
            "system": (self._tr("chat_role_system"), colors["chip_accent"], colors["soft_text"], "left"),
            "fallback": (self._tr("chat_role_info"), colors["button"], colors["text"], "left"),
        }
        self.ai_result.setHtml(
            render_ai_chat_html(
                self.ai_messages,
                labels,
                body_background=colors["output"],
                rich_text_colors=self._assistant_rich_text_colors(),
            )
        )
        cursor = self.ai_result.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ai_result.setTextCursor(cursor)

    def _assistant_rich_text_colors(self) -> dict[str, str]:
        colors = self._theme_palette()
        return {
            "link": colors["blue"],
            "note_bg": colors["chip_accent"],
            "note_fg": colors["blue_text"],
            "section_bg": colors["button"],
            "section_border": colors["button_border"],
            "section_label": colors["muted"],
            "section_fg": colors["text"],
            "explanation_bg": colors["raised"],
            "explanation_border": colors["strong_border"],
            "explanation_label": colors["soft_text"],
            "explanation_fg": colors["text"],
            "plain_fg": colors["text"],
        }

    def _project_version(self) -> str:
        try:
            data = tomllib.loads(self.PYPROJECT_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, tomllib.TOMLDecodeError):
            return "Unbekannt"
        project = data.get("project", {})
        version = project.get("version", "")
        return version if isinstance(version, str) and version.strip() else "Unbekannt"

    def _latest_packaged_version(self) -> str:
        try:
            for line in self.CHANGELOG_PATH.read_text(encoding="utf-8").splitlines():
                if line.startswith("## "):
                    return line[3:].split(" - ", 1)[0].strip() or self._project_version()
        except (FileNotFoundError, OSError):
            return self._project_version()
        return self._project_version()

    def _release_notes_html(self) -> str:
        colors = self._theme_palette()
        try:
            changelog = self.CHANGELOG_PATH.read_text(encoding="utf-8").strip()
        except (FileNotFoundError, OSError):
            return f"<p style='color:{colors['muted']}; margin:0;'>Keine Versionshinweise gefunden.</p>"

        lines = changelog.splitlines()
        html_lines: list[str] = []
        in_list = False
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                continue
            if stripped.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h3 style='margin:14px 0 8px; color:{colors['text']};'>{stripped[3:]}</h3>")
                continue
            if stripped.startswith("- "):
                if not in_list:
                    html_lines.append("<ul style='margin:6px 0 10px 20px; padding:0;'>")
                    in_list = True
                html_lines.append(f"<li style='margin:0 0 6px; color:{colors['soft_text']};'>{stripped[2:]}</li>")
                continue
        if in_list:
            html_lines.append("</ul>")
        return "".join(html_lines) or f"<p style='color:{colors['muted']}; margin:0;'>Keine Versionshinweise gefunden.</p>"

    def _about_html(self) -> str:
        colors = self._theme_palette()
        version = self._project_version()
        notes_html = self._release_notes_html()
        return (
            "<html><body style=\""
            f"font-family:'DejaVu Sans'; font-size:14px; line-height:1.5; color:{colors['text']};"
            f" background:{colors['output']}; margin:0;\">"
            f"<h2 style='margin:0 0 10px; color:{colors['text']};'>Matrix KI Taschenrechner</h2>"
            f"<p style='margin:0 0 14px; color:{colors['soft_text']};'><b>Kontakt zum Entwickler:</b><br>"
            "Orhan (MrMiYaGi068 - GITHUB)<br>"
            "miyagi068@gmail.com</p>"
            f"<p style='margin:0 0 14px; color:{colors['soft_text']};'><b>Version:</b> {version}<br>"
            "<b>Lizenz:</b> GNU GPL v3 oder neuer (GPL-3.0-or-later)<br>"
            "<b>Copyright:</b> Copyright (C) 2026 Orhan</p>"
            f"<h3 style='margin:0 0 8px; color:{colors['text']};'>Versionshinweise</h3>"
            f"{notes_html}"
            "</body></html>"
        )

    def _populate_about_tab(self, dialog: AssistantSettingsDialog) -> None:
        dialog.about_browser.setHtml(self._about_html())
        if not dialog.about_status_label.text():
            dialog.about_status_label.hide()

    def _check_for_updates(self, dialog: AssistantSettingsDialog) -> None:
        installed = self._project_version()
        packaged = self._latest_packaged_version()
        if installed == packaged:
            message = (
                f"Installierte Version {installed} stimmt mit den enthaltenen Versionshinweisen überein. "
                "Eine Online-Updateprüfung ist in dieser Desktop-Version noch nicht eingerichtet."
            )
        else:
            message = (
                f"Installierte Version {installed}, neueste enthaltene Versionshinweise {packaged}. "
                "Bitte README und Changelog dieses Pakets prüfen."
            )
        dialog.about_status_label.setText(message)
        dialog.about_status_label.show()

    def _open_readme(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.README_PATH)))

    def _build_openai_input(self, query: str) -> str:
        return build_openai_input(
            query,
            use_context=self.ai_use_context,
            messages=self.ai_messages,
            user_label=self._tr("openai_transcript_user"),
            assistant_label=self._tr("openai_transcript_assistant"),
            system_label=self._tr("openai_transcript_system"),
        )

    def _export_history(self) -> None:
        if not self.history_items:
            if self.history_dialog is not None:
                self.history_dialog.info_label.setText(self._tr("history_export_empty"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            self._tr("export_history"),
            str(Path.home() / "matrix-calculator-history.txt"),
            self._tr("history_export_filter"),
        )
        if not path:
            return
        lines = [f"{self._pretty_expression(expr)} = {value}" for expr, value in self.history_items]
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        if self.history_dialog is not None:
            self.history_dialog.info_label.setText(self._tr("history_exported").format(path=path))

    def _pretty_expression(self, text: str) -> str:
        return pretty_expression(text)

    def _format_number(self, value: float | complex | str) -> str:
        return format_number(value)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        text = event.text()
        if key in {Qt.Key_Return, Qt.Key_Enter}:
            self._evaluate()
            return
        if key == Qt.Key_Backspace:
            self._handle_button("⌫")
            return
        if key == Qt.Key_Delete:
            self._handle_button("CE")
            return
        if text in "0123456789.+-*/()%^i":
            mapping = {"*": "×", "/": "÷", "^": "xʸ"}
            self._handle_button(mapping.get(text, text))
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched: object, event: object) -> bool:
        if (
            watched is self.ai_input
            and isinstance(event, QKeyEvent)
            and event.type() == QEvent.KeyPress
            and event.key() == Qt.Key_Up
            and not self.ai_input.text().strip()
            and self.last_ai_query
        ):
            self.ai_input.setText(self.last_ai_query)
            self.ai_input.setCursorPosition(len(self.last_ai_query))
            return True
        return super().eventFilter(watched, event)


def main() -> int:
    if QApplication is None:
        print("PySide6 ist nicht installiert. Auf openSUSE Tumbleweed: sudo zypper install python313-pyside6")
        return 1
    app = QApplication(sys.argv)
    app.setApplicationName("MatrixCalculator")
    app.setApplicationDisplayName("Matrix Calculator")
    app.setDesktopFileName("io.github.MrMiYaGi68.MatrixCalculator")
    icon_path = Path(__file__).resolve().parent / "assets" / "matrix-calculator-icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setStyle("Fusion")
    window = MatrixCalculatorWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"GUI konnte nicht gestartet werden: {exc}")
        sys.exit(1)
