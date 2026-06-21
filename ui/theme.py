# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from string import Template

from ui.button_config import DEFAULT_THEME


_PALETTES: dict[str, dict[str, str]] = {
    "graphite": {
        "window": "#101317", "panel": "#191d23", "side": "#15191f", "assistant": "#1c2128",
        "display": "#0f141a", "display_border": "#334052", "output": "#171d25", "raised": "#242a33",
        "status_bg": "#20262e", "input": "#1d2631", "input_focus": "#233044",
        "border": "#2a313b", "strong_border": "#343c48", "button_border": "#3a4451",
        "text": "#f4f6f8", "soft_text": "#dbe1e8", "muted": "#9ca7b5",
        "button": "#252b34", "button_hover": "#303845", "number": "#2d333d", "number_hover": "#39424e",
        "number_border": "#3b4450", "function": "#404957", "function_hover": "#4a5464",
        "function_border": "#505a68", "memory": "#374457", "memory_border": "#46566d",
        "mode": "#303946", "mode_border": "#414c5a", "danger_soft": "#484f5b",
        "danger_soft_border": "#58616f", "clear": "#bd4040", "clear_border": "#dd6262",
        "clear_hover": "#cf5151", "accent": "#ff9f0a", "accent_hover": "#ffae2e",
        "accent_border": "#ffc05d", "accent_text": "#101317", "blue": "#7da2ff",
        "focus": "#8bb4ff",
        "blue_bg": "#1b2836", "blue_border": "#2f557d", "blue_text": "#dceaff",
        "scrollbar": "#4b5563", "scrollbar_hover": "#647184",
        "chip_accent": "#27313d", "chip_good": "#22392e", "chip_warm": "#ff9f0a",
    },
    "matrix": {
        "window": "#0d1513", "panel": "#14201d", "side": "#101a18", "assistant": "#172420",
        "display": "#0a1211", "display_border": "#2d5548", "output": "#101a18", "raised": "#1c2d28",
        "status_bg": "#192821", "input": "#162721", "input_focus": "#1b342b",
        "border": "#243b34", "strong_border": "#2d5145", "button_border": "#355d50",
        "text": "#eff8f5", "soft_text": "#d7eee6", "muted": "#9bb7ad",
        "button": "#1e312b", "button_hover": "#294239", "number": "#263c35", "number_hover": "#304d43",
        "number_border": "#35584c", "function": "#344b43", "function_hover": "#405b51",
        "function_border": "#4e6f63", "memory": "#30485b", "memory_border": "#3f5d75",
        "mode": "#283c35", "mode_border": "#3d5d51", "danger_soft": "#4b514b",
        "danger_soft_border": "#60695f", "clear": "#be4444", "clear_border": "#de6969",
        "clear_hover": "#cf5656", "accent": "#ff9f0a", "accent_hover": "#ffb02f",
        "accent_border": "#ffc060", "accent_text": "#0d1513", "blue": "#7fc7ff",
        "focus": "#8fd4ff",
        "blue_bg": "#15293a", "blue_border": "#2e617e", "blue_text": "#dff4ff",
        "scrollbar": "#45635a", "scrollbar_hover": "#5d8175",
        "chip_accent": "#203932", "chip_good": "#1d4335", "chip_warm": "#ff9f0a",
    },
    "high contrast": {
        "window": "#000000", "panel": "#101010", "side": "#070707", "assistant": "#141414",
        "display": "#000000", "display_border": "#747474", "output": "#050505", "raised": "#1f1f1f",
        "status_bg": "#181818", "input": "#0a0a0a", "input_focus": "#121a25",
        "border": "#424242", "strong_border": "#6a6a6a", "button_border": "#727272",
        "text": "#ffffff", "soft_text": "#f2f2f2", "muted": "#d0d0d0",
        "button": "#222222", "button_hover": "#333333", "number": "#202020", "number_hover": "#353535",
        "number_border": "#737373", "function": "#333333", "function_hover": "#444444",
        "function_border": "#868686", "memory": "#2b3b4f", "memory_border": "#7195c4",
        "mode": "#242424", "mode_border": "#777777", "danger_soft": "#3d3d3d",
        "danger_soft_border": "#858585", "clear": "#d43b3b", "clear_border": "#ff8f8f",
        "clear_hover": "#e74f4f", "accent": "#ffb000", "accent_hover": "#ffc13d",
        "accent_border": "#ffe08a", "accent_text": "#000000", "blue": "#8ec5ff",
        "focus": "#ffffff",
        "blue_bg": "#061d35", "blue_border": "#69aee9", "blue_text": "#ffffff",
        "scrollbar": "#777777", "scrollbar_hover": "#9b9b9b",
        "chip_accent": "#202020", "chip_good": "#143b28", "chip_warm": "#ffb000",
    },
    "light": {
        "window": "#eef1f4", "panel": "#fbfcfd", "side": "#f6f8fa", "assistant": "#ffffff",
        "display": "#f5f7fa", "display_border": "#c9d2de", "output": "#f8fafc", "raised": "#eef2f6",
        "status_bg": "#edf2f7", "input": "#ffffff", "input_focus": "#f2f7ff",
        "border": "#d8dee8", "strong_border": "#c6cfdb", "button_border": "#c8d1de",
        "text": "#151a21", "soft_text": "#2f3b48", "muted": "#647083",
        "button": "#eef2f6", "button_hover": "#e3e9f0", "number": "#ffffff", "number_hover": "#edf3f8",
        "number_border": "#d0d8e3", "function": "#e4eaf1", "function_hover": "#d9e1ea",
        "function_border": "#c5cfda", "memory": "#dfe9f5", "memory_border": "#bfd0e5",
        "mode": "#e8edf3", "mode_border": "#c7d0dc", "danger_soft": "#eef0f3",
        "danger_soft_border": "#c9d0d8", "clear": "#c83e3e", "clear_border": "#e17878",
        "clear_hover": "#d85353", "accent": "#e88b00", "accent_hover": "#f59b16",
        "accent_border": "#c87300", "accent_text": "#151a21", "blue": "#356fd6",
        "focus": "#245fca",
        "blue_bg": "#eaf2ff", "blue_border": "#bad0f5", "blue_text": "#1e477f",
        "scrollbar": "#aeb8c5", "scrollbar_hover": "#909dad",
        "chip_accent": "#e9eef5", "chip_good": "#e6f3ec", "chip_warm": "#e88b00",
    },
}


def theme_palette(theme_name: str) -> dict[str, str]:
    return _PALETTES.get(theme_name, _PALETTES[DEFAULT_THEME])


def build_stylesheet(theme_name: str) -> str:
    colors = theme_palette(theme_name)
    return Template(
        """
        QMainWindow {
            background: $window;
        }
        QFrame#mainPanel, QFrame#sidePanel {
            background: $panel;
            border: 1px solid $border;
            border-radius: 14px;
        }
        QFrame#sidePanel {
            background: $side;
            border: 1px solid $strong_border;
        }
        QSplitter::handle {
            background: transparent;
            border-radius: 4px;
        }
        QLabel#titleLabel {
            color: $text;
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#subtitleLabel {
            color: $muted;
            font-size: 14px;
            padding-bottom: 2px;
        }
        QPushButton#iconButton {
            background: $button;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 0px;
            font-size: 18px;
            font-weight: 700;
            min-width: 38px;
            max-width: 38px;
            min-height: 38px;
            max-height: 38px;
        }
        QPushButton#iconButton:hover {
            background: $button_hover;
        }
        QPushButton#iconButton:pressed {
            background: $raised;
        }
        QLabel#panelTitle {
            color: $text;
            font-size: 20px;
            font-weight: 700;
        }
        QLabel#panelHint {
            color: $muted;
            font-size: 14px;
        }
        QLabel#helperLabel {
            color: $soft_text;
            background: $raised;
            border: 1px solid $border;
            border-radius: 10px;
            padding: 9px 11px;
            font-size: 14px;
        }
        QComboBox#modeSelect, QComboBox#themeSelect {
            background: $button;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 9px;
            padding: 7px 10px;
            font-size: 14px;
            min-width: 180px;
            min-height: 38px;
        }
        QComboBox#themeSelect {
            min-width: 128px;
            max-width: 190px;
        }
        QComboBox#modeSelect::drop-down, QComboBox#themeSelect::drop-down {
            width: 24px;
            border: none;
        }
        QComboBox#modeSelect QAbstractItemView, QComboBox#themeSelect QAbstractItemView {
            background: $panel;
            color: $text;
            border: 1px solid $button_border;
            selection-background-color: $accent;
            selection-color: $accent_text;
            padding: 4px;
            outline: 0;
        }
        QCheckBox#stepCheck {
            color: $text;
            font-size: 15px;
            spacing: 8px;
            min-height: 32px;
            padding-top: 6px;
            padding-bottom: 6px;
        }
        QCheckBox#stepCheck::indicator {
            width: 20px;
            height: 20px;
        }
        QLabel#statusBarLabel {
            color: $soft_text;
            background: $status_bg;
            border: 1px solid $border;
            border-radius: 9px;
            padding: 7px 10px;
            font-size: 13px;
        }
        QLabel#statusBarLabel[state="info"] {
            color: $blue_text;
            background: $blue_bg;
            border: 1px solid $blue_border;
        }
        QLabel#statusBarLabel[state="success"] {
            color: $text;
            background: $chip_good;
            border: 1px solid $blue_border;
        }
        QLabel#statusBarLabel[state="warning"] {
            color: $text;
            background: $status_bg;
            border: 1px solid $accent_border;
        }
        QLabel#statusBarLabel[state="error"] {
            color: $text;
            background: $danger_soft;
            border: 1px solid $clear_border;
        }
        QLabel#previewLabel {
            color: $muted;
            font-size: 13px;
        }
        QLabel#previewLabel[state="info"] {
            color: $blue_text;
        }
        QLabel#previewLabel[state="success"] {
            color: $soft_text;
            font-weight: 650;
        }
        QLabel#previewLabel[state="warning"] {
            color: $accent_border;
            font-weight: 650;
        }
        QLabel#previewLabel[state="error"] {
            color: $clear_hover;
            font-weight: 700;
        }
        QLabel#expressionLabel {
            color: $muted;
            font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace;
            font-size: 18px;
            min-height: 32px;
        }
        QLabel#resultLabel {
            color: $text;
            font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace;
            font-size: 46px;
            font-weight: 700;
            min-height: 58px;
        }
        QLabel#sideTitle {
            color: $text;
            font-size: 22px;
            font-weight: 700;
        }
        QLabel#sideSubtitle, QLabel#historyInfo {
            color: $muted;
            font-size: 15px;
        }
        QFrame#controlsPanel {
            background: transparent;
            border: none;
        }
        QFrame#basicGroupSeparator {
            background: $border;
            border: none;
        }
        QFrame#displayPanel {
            background: $display;
            border: 1px solid $display_border;
            border-radius: 12px;
        }
        QFrame#displayPanel[scientific="true"] {
            border-radius: 10px;
        }
        QFrame#assistantPanel, QFrame#historyPanel {
            background: $assistant;
            border: 1px solid $strong_border;
            border-radius: 12px;
        }
        QFrame#assistantPanel {
            background: transparent;
            border: none;
            border-radius: 0px;
        }
        QLabel#assistantContext {
            color: $soft_text;
            background: $raised;
            border: 1px solid $border;
            border-radius: 8px;
            padding: 8px 10px;
            font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace;
            font-size: 13px;
        }
        QDialog {
            background: $panel;
            color: $text;
        }
        QLabel#settingsTitle {
            color: $text;
            font-size: 22px;
            font-weight: 700;
        }
        QTabWidget#settingsTabs::pane {
            background: $raised;
            border: 1px solid $border;
            border-top-left-radius: 0px;
            border-top-right-radius: 12px;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            top: -1px;
        }
        QTabWidget#settingsTabs::tab-bar {
            alignment: left;
            left: 0px;
        }
        QTabBar::tab {
            background: $button;
            color: $muted;
            border: 1px solid $button_border;
            border-bottom: none;
            padding: 8px 14px;
            min-width: 110px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 2px;
            margin-bottom: 0px;
        }
        QTabBar::tab:selected {
            background: $raised;
            color: $text;
            font-weight: 700;
            border-color: $border;
            margin-bottom: -1px;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QLabel#settingsLabel {
            color: $muted;
            font-size: 14px;
        }
        QLabel#apiStatusLabel {
            color: $soft_text;
            background: $raised;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
            min-height: 22px;
        }
        QTextBrowser#apiStatusBrowser {
            background: $raised;
            color: $soft_text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 6px 8px;
            font-size: 14px;
            line-height: 1.4;
        }
        QTextBrowser#aboutBrowser {
            background: $output;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 8px 10px;
            font-size: 14px;
            line-height: 1.45;
        }
        QLabel[chip="true"] {
            border-radius: 9px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 600;
            min-height: 28px;
        }
        QPushButton#modeSegmentButton {
            background: $button;
            color: $soft_text;
            border: 1px solid $button_border;
            border-radius: 9px;
            padding: 7px 12px;
            font-size: 14px;
            font-weight: 650;
            min-height: 38px;
            min-width: 92px;
        }
        QPushButton#modeSegmentButton:hover {
            background: $button_hover;
        }
        QPushButton#modeSegmentButton:pressed {
            background: $raised;
        }
        QPushButton#modeSegmentButton:checked {
            background: $input_focus;
            color: $text;
            border: 2px solid $focus;
        }
        QPushButton#modeSegmentButton:checked:hover {
            background: $input_focus;
        }
        QPushButton#ghostButton, QPushButton#toolButton, QPushButton#utilityButton {
            background: $button;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 9px;
            padding: 7px 12px;
            font-size: 14px;
            font-weight: 600;
            min-height: 38px;
        }
        QPushButton#toolButton {
            min-width: 150px;
        }
        QPushButton#utilityButton {
            background: transparent;
            color: $soft_text;
            border: 1px solid $border;
        }
        QPushButton#ghostButton:hover, QPushButton#toolButton:hover, QPushButton#utilityButton:hover {
            background: $button_hover;
        }
        QPushButton#ghostButton:pressed, QPushButton#toolButton:pressed, QPushButton#utilityButton:pressed {
            background: $raised;
        }
        QPushButton#assistantToggleButton {
            background: $button;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 7px 12px;
            font-size: 14px;
            font-weight: 700;
            min-height: 38px;
            min-width: 118px;
        }
        QPushButton#assistantToggleButton:hover {
            background: $button_hover;
        }
        QPushButton#assistantToggleButton:pressed {
            background: $raised;
        }
        QPushButton#assistantToggleButton[assistantVisible="true"] {
            background: $input_focus;
            color: $text;
            border: 2px solid $focus;
        }
        QPushButton#assistantToggleButton[assistantVisible="true"]:hover {
            background: $input_focus;
        }
        QPushButton#primaryButton, QPushButton#solveButton {
            background: $accent;
            color: $accent_text;
            border: 1px solid $accent_border;
            border-radius: 12px;
            padding: 10px 16px;
            font-size: 16px;
            font-weight: 700;
            min-height: 46px;
            min-width: 120px;
        }
        QPushButton#solveButton {
            background: $button;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            min-height: 42px;
        }
        QPushButton#primaryButton:hover {
            background: $accent_hover;
        }
        QPushButton#solveButton:hover {
            background: $button_hover;
        }
        QPushButton#primaryButton:pressed, QPushButton#solveButton:pressed {
            background: $raised;
        }
        QFrame#assistantQueryPanel {
            background: transparent;
            border: none;
            border-radius: 0px;
        }
        QTextEdit#queryInput, QPlainTextEdit#queryInput {
            background: $input;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 16px;
            font-weight: 500;
            min-height: 92px;
        }
        QTextEdit#queryInput:focus, QPlainTextEdit#queryInput:focus {
            border: 2px solid $focus;
            background: $input_focus;
        }
        QLabel#queryPreview {
            color: $soft_text;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 9px;
            padding: 7px 10px;
            font-size: 13px;
            line-height: 1.35;
        }
        QLabel#queryPreview[state="info"] {
            color: $blue_text;
            background: $blue_bg;
            border: 1px solid $blue_border;
        }
        QLabel#queryPreview[state="warning"] {
            color: $text;
            background: $status_bg;
            border: 1px solid $accent_border;
        }
        QLabel#queryPreview[state="error"] {
            color: $text;
            background: $danger_soft;
            border: 1px solid $clear_border;
        }
        QFrame#assistantExamples {
            background: transparent;
            border: none;
        }
        QLabel#assistantExamplesLabel {
            color: $muted;
            font-size: 13px;
            padding: 2px 2px 4px 2px;
        }
        QPushButton#exampleButton {
            background: transparent;
            color: $soft_text;
            border: 1px solid $border;
            border-radius: 8px;
            padding: 7px 10px;
            text-align: left;
            font-size: 14px;
            min-height: 34px;
        }
        QPushButton#exampleButton:hover {
            background: $blue_bg;
            color: $blue_text;
            border-color: $blue_border;
        }
        QPushButton#exampleButton:pressed {
            background: $raised;
            color: $text;
            border-color: $button_border;
        }
        QTextEdit#assistantOutput, QTextBrowser#assistantOutput {
            background: $output;
            color: $text;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 6px;
            font-size: 15px;
        }
        QListWidget#historyList {
            background: $output;
            border: 1px solid $button_border;
            border-radius: 10px;
            padding: 8px;
            color: $text;
            font-size: 16px;
            outline: none;
        }
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 12px;
            margin: 8px 4px 8px 0;
        }
        QScrollBar::handle:vertical {
            background: $scrollbar;
            border-radius: 6px;
            min-height: 48px;
        }
        QScrollBar::handle:vertical:hover {
            background: $scrollbar_hover;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        QListWidget#historyList::item {
            border-radius: 8px;
            padding: 10px;
            margin: 3px 0;
            background: $raised;
        }
        QListWidget#historyList::item:selected {
            background: $accent;
            color: $accent_text;
        }
        CalcButton {
            border: none;
        }
        QPushButton[role="number"] {
            background: $number;
            color: $text;
            border: 1px solid $number_border;
            border-radius: 11px;
            font-size: 24px;
            font-weight: 750;
        }
        QPushButton[role="number"]:hover {
            background: $number_hover;
        }
        QPushButton[role="number"]:pressed {
            background: $raised;
        }
        QPushButton[role="operator"] {
            background: $function;
            color: $text;
            border: 1px solid $function_border;
            border-radius: 11px;
            font-size: 20px;
            font-weight: 700;
        }
        QPushButton[role="operator"]:hover {
            background: $function_hover;
        }
        QPushButton[role="operator"]:pressed {
            background: $raised;
        }
        QPushButton[role="operator"][primaryOperator="true"] {
            background: $accent;
            color: $accent_text;
            border: 1px solid $accent_border;
        }
        QPushButton[role="operator"][primaryOperator="true"]:hover {
            background: $accent_hover;
        }
        QPushButton[role="operator"][primaryOperator="true"]:pressed {
            background: $accent;
        }
        QPushButton[role="function"] {
            background: $function;
            color: $text;
            border: 1px solid $function_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
        }
        QPushButton[role="function"]:hover {
            background: $function_hover;
        }
        QPushButton[role="function"]:pressed {
            background: $raised;
        }
        QPushButton[basicGroup="entry"] {
            background: $raised;
            border-color: $button_border;
        }
        QPushButton[basicGroup="function"] {
            background: $function;
            border-color: $function_border;
        }
        QPushButton[role="memory"] {
            background: $memory;
            color: $text;
            border: 1px solid $memory_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
        }
        QPushButton[role="memory"]:hover {
            background: $button_hover;
        }
        QPushButton[role="memory"]:pressed {
            background: $raised;
        }
        QPushButton[role="danger"] {
            background: $danger_soft;
            color: $text;
            border: 1px solid $danger_soft_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
        }
        QPushButton[role="danger"]:hover {
            background: $function_hover;
        }
        QPushButton[role="danger"]:pressed {
            background: $raised;
        }
        QPushButton[role="clear"] {
            background: $clear;
            color: #ffffff;
            border: 1px solid $clear_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
        }
        QPushButton[role="clear"]:hover {
            background: $clear_hover;
        }
        QPushButton[role="clear"]:pressed {
            background: $clear;
        }
        QPushButton[role="mode"] {
            background: $mode;
            color: $text;
            border: 1px solid $mode_border;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
        }
        QPushButton[role="mode"]:hover {
            background: $button_hover;
        }
        QPushButton[role="mode"]:pressed {
            background: $raised;
        }
        QPushButton[role="mode"][modeActive="true"] {
            background: $input_focus;
            color: $text;
            border: 2px solid $focus;
        }
        QPushButton[role="mode"][modeActive="true"]:hover {
            background: $input_focus;
        }
        QPushButton[role="equal"] {
            background: $accent;
            color: $accent_text;
            border: 1px solid $accent_border;
            border-radius: 11px;
            font-size: 22px;
            font-weight: 700;
        }
        QPushButton[role="equal"]:hover {
            background: $accent_hover;
        }
        QPushButton[role="equal"]:pressed {
            background: $accent;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="mode"] {
            background: $mode;
            border-color: $mode_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="mode"][modeActive="true"] {
            background: $input_focus;
            border: 2px solid $focus;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="memory"][role="memory"] {
            background: $memory;
            border-color: $memory_border;
            color: $soft_text;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="power"][role="function"] {
            background: $function;
            border-color: $function_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="trig"][role="function"] {
            background: $button;
            border-color: $button_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="complex"][role="function"] {
            background: $memory;
            border-color: $memory_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="keypad"][role="number"] {
            background: $number;
            border-color: $number_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="keypad"][primaryOperator="true"],
        QFrame#mainPanel[scientific="true"] QPushButton[scientificGroup="keypad"][role="equal"] {
            background: $accent;
            color: $accent_text;
            border-color: $accent_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[role="clear"] {
            background: $clear;
            color: #ffffff;
            border-color: $clear_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[role="danger"] {
            background: $danger_soft;
            color: $text;
            border-color: $danger_soft_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[role="operator"] {
            background: $function;
            color: $text;
            border-color: $function_border;
        }
        QFrame#mainPanel[scientific="true"] QPushButton[role="operator"][primaryOperator="true"],
        QFrame#mainPanel[scientific="true"] QPushButton[role="equal"] {
            background: $accent;
            color: $accent_text;
            border-color: $accent_border;
        }
        QPushButton:focus, QComboBox:focus, QCheckBox:focus, QTabBar::tab:focus,
        QListWidget:focus, QTextBrowser:focus {
            border: 2px solid $focus;
        }
        QPushButton:disabled, QComboBox:disabled, QCheckBox:disabled,
        QTextEdit:disabled, QPlainTextEdit:disabled {
            color: $muted;
            background: $status_bg;
            border-color: $border;
        }
        QFrame#mainPanel[compact="true"] QLabel#titleLabel {
            font-size: 20px;
        }
        QFrame#mainPanel[compact="true"] QLabel[chip="true"] {
            min-height: 24px;
            padding: 4px 8px;
        }
        QFrame#mainPanel[compact="true"] QPushButton#modeSegmentButton,
        QFrame#mainPanel[compact="true"] QPushButton#utilityButton,
        QFrame#mainPanel[compact="true"] QPushButton#assistantToggleButton {
            min-height: 34px;
            padding: 6px 9px;
        }
        QPushButton[basicSymbol="true"] {
            font-size: 24px;
            font-weight: 750;
        }
        """
    ).substitute(colors)
