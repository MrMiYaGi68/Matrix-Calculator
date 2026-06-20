# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QTextBrowser,
    QVBoxLayout,
)

from ui.assistant_widgets import QueryInput
from ui.button_config import BUTTON_COLUMN_COUNT, BUTTON_COLUMN_SPANS, BUTTON_ROWS, button_tooltip_key
from ui.dialogs import HistoryDialog, SkillsDialog


def _settings_gear_icon(window) -> QIcon:
    icon = QIcon.fromTheme("settings-configure")
    if icon.isNull():
        icon = QIcon.fromTheme("preferences-system")
    if icon.isNull():
        icon = window.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
    return icon


def build_left_panel_content(window, left_layout, *, button_class) -> None:
    title_row = QHBoxLayout()
    title_row.setSpacing(10)
    title_row.setAlignment(Qt.AlignVCenter)
    left_layout.addLayout(title_row)

    title_text_layout = QVBoxLayout()
    title_text_layout.setContentsMargins(0, 0, 0, 0)
    title_text_layout.setSpacing(2)
    title_row.addLayout(title_text_layout, 1)

    window.title_label = QLabel("Matrix <span style='color:#ff9f0a;'>KI</span> Taschenrechner")
    window.title_label.setObjectName("titleLabel")
    window.subtitle_label = QLabel("Bereit fuer schnelle Rechnungen.")
    window.subtitle_label.setObjectName("subtitleLabel")
    title_text_layout.addWidget(window.title_label)
    title_text_layout.addWidget(window.subtitle_label)

    window.header_settings_button = QPushButton()
    window.header_settings_button.setObjectName("iconButton")
    window.header_settings_button.setCursor(Qt.PointingHandCursor)
    window.header_settings_button.setText("")
    window.header_settings_button.setIcon(_settings_gear_icon(window))
    window.header_settings_button.setIconSize(QSize(18, 18))
    window.header_settings_button.setToolTip("Einstellungen")
    window.header_settings_button.clicked.connect(window._open_settings_dialog)
    title_row.addWidget(window.header_settings_button, 0, Qt.AlignTop)

    chip_row = QHBoxLayout()
    chip_row.setSpacing(10)
    left_layout.addLayout(chip_row)

    window.smart_chip = window._make_chip("Lokal", "accent")
    window.mode_chip = window._make_chip("DEG", "good")
    window.memory_chip = window._make_chip("M 0", "warm")
    chip_row.addWidget(window.smart_chip)
    chip_row.addWidget(window.mode_chip)
    chip_row.addWidget(window.memory_chip)
    chip_row.addStretch()

    top_controls_row = QHBoxLayout()
    top_controls_row.setSpacing(10)
    top_controls_row.setAlignment(Qt.AlignVCenter)
    left_layout.addLayout(top_controls_row)

    window.layout_mode_group = QButtonGroup(window)
    window.layout_mode_group.setExclusive(True)

    window.basic_mode_button = QPushButton("Basis")
    window.basic_mode_button.setObjectName("modeSegmentButton")
    window.basic_mode_button.setCheckable(True)
    window.basic_mode_button.setCursor(Qt.PointingHandCursor)
    window.basic_mode_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    window.basic_mode_button.clicked.connect(lambda: window._set_layout_mode(False))
    window.layout_mode_group.addButton(window.basic_mode_button)
    top_controls_row.addWidget(window.basic_mode_button)

    window.scientific_mode_button = QPushButton("Wissenschaft")
    window.scientific_mode_button.setObjectName("modeSegmentButton")
    window.scientific_mode_button.setCheckable(True)
    window.scientific_mode_button.setCursor(Qt.PointingHandCursor)
    window.scientific_mode_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    window.scientific_mode_button.clicked.connect(lambda: window._set_layout_mode(True))
    window.layout_mode_group.addButton(window.scientific_mode_button)
    top_controls_row.addWidget(window.scientific_mode_button)
    window.layout_button = window.scientific_mode_button

    window.history_button = QPushButton("Verlauf")
    window.history_button.setObjectName("utilityButton")
    window.history_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    window.history_button.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
    window.history_button.setIconSize(QSize(16, 16))
    window.history_button.clicked.connect(window._open_history_dialog)
    top_controls_row.addWidget(window.history_button)

    window.ai_toggle_button = QPushButton()
    window.ai_toggle_button.setObjectName("assistantToggleButton")
    window.ai_toggle_button.setCursor(Qt.PointingHandCursor)
    window.ai_toggle_button.setMinimumWidth(118)
    window.ai_toggle_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    window.ai_toggle_button.clicked.connect(window._toggle_ai_panel)
    top_controls_row.addWidget(window.ai_toggle_button)
    window._refresh_ai_toggle_button()

    window.display_panel = QFrame()
    window.display_panel.setObjectName("displayPanel")
    display_layout = QVBoxLayout(window.display_panel)
    display_layout.setContentsMargins(18, 16, 18, 16)
    display_layout.setSpacing(5)
    left_layout.addWidget(window.display_panel)

    window.preview_label = QLabel("Bereit für Eingabe")
    window.preview_label.setObjectName("previewLabel")
    window.expression_label = QLabel("")
    window.expression_label.setObjectName("expressionLabel")
    window.expression_label.setWordWrap(True)
    window.expression_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    window.result_label = QLabel("0")
    window.result_label.setObjectName("resultLabel")
    window.result_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    display_layout.addWidget(window.preview_label)
    display_layout.addWidget(window.expression_label)
    display_layout.addWidget(window.result_label)

    controls_wrap = QFrame()
    controls_wrap.setObjectName("controlsPanel")
    window.controls_layout = QVBoxLayout(controls_wrap)
    window.controls_layout.setContentsMargins(0, 0, 0, 0)
    window.controls_layout.setSpacing(0)
    left_layout.addWidget(controls_wrap, 1)

    window.controls_grid = QGridLayout()
    window.controls_grid.setContentsMargins(0, 0, 0, 0)
    window.controls_grid.setHorizontalSpacing(10)
    window.controls_grid.setVerticalSpacing(10)
    for column in range(BUTTON_COLUMN_COUNT):
        window.controls_grid.setColumnStretch(column, 1)
    window.controls_layout.addLayout(window.controls_grid)

    for row_index, row in enumerate(BUTTON_ROWS):
        for col_index, label in enumerate(row):
            role = window._button_role(label)
            button = button_class(label, role)
            button.setProperty("baseLabel", label)
            window.all_calc_buttons.append(button)
            button.clicked.connect(lambda checked=False, value=label: window._handle_button(value))
            shortcut_hint = window._button_shortcut_hint(label)
            if shortcut_hint:
                button.setToolTip(shortcut_hint)
            tooltip_key = button_tooltip_key(label)
            if tooltip_key:
                button.setToolTip(window._tr(tooltip_key))
            span = BUTTON_COLUMN_SPANS.get(label, 1)
            window.controls_grid.addWidget(button, row_index, col_index, 1, span)
            window.row_groups.setdefault(row_index, []).append(button)
            if label in window.second_pairs:
                window.toggle_buttons[label] = button
            if label == "Deg":
                window.mode_toggle_button = button


def build_assistant_panel_content(window, right_layout) -> None:
    ai_scroll = QScrollArea()
    ai_scroll.setWidgetResizable(True)
    ai_scroll.setFrameShape(QFrame.NoFrame)
    right_layout.addWidget(ai_scroll, 3)

    window.ai_panel = QFrame()
    window.ai_panel.setObjectName("assistantPanel")
    ai_scroll.setWidget(window.ai_panel)
    ai_layout = QVBoxLayout(window.ai_panel)
    ai_layout.setContentsMargins(12, 12, 12, 12)
    ai_layout.setSpacing(8)

    window.ai_title = QLabel("Matrix <span style='color:#ff9f0a;'>KI</span> Assistent")
    window.ai_title.setObjectName("panelTitle")
    ai_layout.addWidget(window.ai_title)

    window.ai_status = QLabel("Bereit. Lokaler Rechenmodus ist aktiv.")
    window.ai_status.setObjectName("statusBarLabel")
    window.ai_status.setWordWrap(True)
    ai_layout.addWidget(window.ai_status)

    window.assistant_query_panel = QFrame()
    window.assistant_query_panel.setObjectName("assistantQueryPanel")
    query_column = QVBoxLayout(window.assistant_query_panel)
    query_column.setContentsMargins(10, 10, 10, 10)
    query_column.setSpacing(10)
    ai_layout.addWidget(window.assistant_query_panel)

    window.ai_input = QueryInput()
    window.ai_input.setObjectName("queryInput")
    window.ai_input.setPlaceholderText("Frage den Matrix KI Taschenrechner...")
    window.ai_input.setTabChangesFocus(False)
    window.ai_input.returnPressed.connect(window._solve_natural_query)
    window.ai_input.textChangedValue.connect(window._update_ai_live_preview)
    window.ai_input.installEventFilter(window)
    query_column.addWidget(window.ai_input, 1)

    window.solve_button = QPushButton("Berechnen")
    window.solve_button.setObjectName("solveButton")
    window.solve_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    window.solve_button.clicked.connect(window._solve_natural_query)
    query_column.addWidget(window.solve_button)

    window.ai_live_preview = QLabel("Live-Erkennung erscheint hier.")
    window.ai_live_preview.setObjectName("queryPreview")
    window.ai_live_preview.setWordWrap(True)
    query_column.addWidget(window.ai_live_preview)

    action_grid = QGridLayout()
    action_grid.setHorizontalSpacing(8)
    action_grid.setVerticalSpacing(8)
    ai_layout.addLayout(action_grid)

    window.settings_button = QPushButton("Einstellungen")
    window.settings_button.setObjectName("toolButton")
    window.settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    window.settings_button.setIcon(_settings_gear_icon(window))
    window.settings_button.setIconSize(QSize(16, 16))
    window.settings_button.clicked.connect(window._open_settings_dialog)
    action_grid.addWidget(window.settings_button, 0, 0)

    window.chatgpt_web_button = QPushButton("ChatGPT")
    window.chatgpt_web_button.setObjectName("toolButton")
    window.chatgpt_web_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    window.chatgpt_web_button.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
    window.chatgpt_web_button.setIconSize(QSize(16, 16))
    window.chatgpt_web_button.clicked.connect(window._open_chatgpt_web_for_current_query)
    action_grid.addWidget(window.chatgpt_web_button, 0, 1)

    action_grid.setColumnStretch(0, 1)
    action_grid.setColumnStretch(1, 1)

    window.mode_preference = QComboBox()
    window.mode_preference.setObjectName("modeSelect")
    window.mode_preference.addItems(["Lokal, dann Browser", "Direkt per API (Erweitert)"])
    window.mode_preference.hide()

    window.step_checkbox = QCheckBox("Schritte zeigen")
    window.step_checkbox.setObjectName("stepCheck")
    window.step_checkbox.setChecked(True)
    window.step_checkbox.toggled.connect(window._toggle_step_mode)
    window.step_checkbox.hide()

    window.context_checkbox = QCheckBox("Chat-Kontext")
    window.context_checkbox.setObjectName("stepCheck")
    window.context_checkbox.setChecked(True)
    window.context_checkbox.toggled.connect(window._toggle_context_mode)
    window.context_checkbox.hide()

    window.ai_result = QTextBrowser()
    window.ai_result.setObjectName("assistantOutput")
    window.ai_result.setReadOnly(True)
    window.ai_result.setOpenExternalLinks(True)
    window.ai_result.setMinimumHeight(220)
    window.ai_result.setPlaceholderText(window._tr("assistant_output_placeholder"))
    ai_layout.addWidget(window.ai_result, 1)

    window.clear_ai_button = QPushButton("KI-Verlauf löschen")
    window.clear_ai_button.setObjectName("ghostButton")
    window.clear_ai_button.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
    window.clear_ai_button.setIconSize(QSize(16, 16))
    window.clear_ai_button.clicked.connect(window._clear_ai_chat)
    action_grid.addWidget(window.clear_ai_button, 1, 0, 1, 2)


def build_auxiliary_dialogs(window) -> None:
    window.history_dialog = HistoryDialog(window, window.app_language)
    window.history_dialog.history_list.itemClicked.connect(window._on_history_clicked)
    window.history_dialog.export_button.clicked.connect(window._export_history)
    window.history_dialog.clear_button.clicked.connect(window._clear_history)
    window.skills_dialog = SkillsDialog(window, window.app_language)
