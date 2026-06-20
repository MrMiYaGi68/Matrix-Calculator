# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from core.i18n import LANGUAGES, language_label, normalize_language, tr

from PySide6.QtCore import QUrl
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    QWebEnginePage = None
    QWebEngineProfile = None
    QWebEngineView = None


class AssistantSettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, language: str = "de") -> None:
        super().__init__(parent)
        self.language = normalize_language(language)
        self.setWindowTitle(tr(self.language, "settings_title"))
        self.setModal(True)
        self.setMinimumSize(620, 620)
        self.resize(760, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel(tr(self.language, "configure_assistant"))
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        layout.addWidget(self.tabs, 1)

        general_tab, general_layout = self._create_tab_page()
        self.tabs.addTab(general_tab, "Allgemein" if self.language == "de" else "General")

        language_label_widget = QLabel(tr(self.language, "language"))
        language_label_widget.setObjectName("settingsLabel")
        general_layout.addWidget(language_label_widget)

        self.language_select = QComboBox()
        self.language_select.setObjectName("modeSelect")
        for code, label in LANGUAGES.items():
            self.language_select.addItem(label, code)
        self.language_select.setCurrentText(language_label(self.language))
        general_layout.addWidget(self.language_select)

        theme_label = QLabel("Darstellung" if self.language == "de" else "Theme")
        theme_label.setObjectName("settingsLabel")
        general_layout.addWidget(theme_label)

        self.theme_select = QComboBox()
        self.theme_select.setObjectName("themeSelect")
        self.theme_select.addItems(["Graphite", "Matrix", "High Contrast", "Light"])
        general_layout.addWidget(self.theme_select)

        mode_label = QLabel(tr(self.language, "answer_mode"))
        mode_label.setObjectName("settingsLabel")
        general_layout.addWidget(mode_label)

        self.mode_select = QComboBox()
        self.mode_select.setObjectName("modeSelect")
        self.mode_select.addItems([tr(self.language, "mode_browser"), tr(self.language, "mode_api")])
        general_layout.addWidget(self.mode_select)

        model_label = QLabel(tr(self.language, "online_model"))
        model_label.setObjectName("settingsLabel")
        general_layout.addWidget(model_label)

        self.model_value_label = QLabel(tr(self.language, "automatic"))
        self.model_value_label.setObjectName("apiStatusLabel")
        self.model_value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.model_value_label.setWordWrap(True)
        general_layout.addWidget(self.model_value_label)
        general_layout.addStretch()

        options_tab, options_layout = self._create_tab_page()
        self.tabs.addTab(options_tab, "Optionen" if self.language == "de" else "Options")

        self.step_checkbox = QCheckBox(tr(self.language, "step_by_step"))
        self.step_checkbox.setObjectName("stepCheck")
        options_layout.addWidget(self.step_checkbox)

        self.context_checkbox = QCheckBox(tr(self.language, "chat_context"))
        self.context_checkbox.setObjectName("stepCheck")
        options_layout.addWidget(self.context_checkbox)
        options_layout.addStretch()

        api_tab, api_layout = self._create_tab_page()
        self.tabs.addTab(api_tab, "OpenAI API")

        self.api_button_grid = QGridLayout()
        self.api_button_grid.setContentsMargins(0, 0, 0, 0)
        self.api_button_grid.setHorizontalSpacing(10)
        self.api_button_grid.setVerticalSpacing(10)
        self.api_button_grid.setColumnStretch(0, 1)
        self.api_button_grid.setColumnStretch(1, 1)
        api_layout.addLayout(self.api_button_grid)

        self.api_button = QPushButton(tr(self.language, "enter_api_key"))
        self.api_button.setObjectName("ghostButton")
        self.api_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.api_button_grid.addWidget(self.api_button, 0, 0)

        self.api_help_button = QPushButton(tr(self.language, "api_help"))
        self.api_help_button.setObjectName("ghostButton")
        self.api_help_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.api_button_grid.addWidget(self.api_help_button, 0, 1)

        self.api_test_button = QPushButton(tr(self.language, "test_api"))
        self.api_test_button.setObjectName("ghostButton")
        self.api_test_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.api_button_grid.addWidget(self.api_test_button, 1, 0, 1, 2)

        self.api_status_browser = QTextBrowser()
        self.api_status_browser.setObjectName("apiStatusBrowser")
        self.api_status_browser.setReadOnly(True)
        self.api_status_browser.setOpenExternalLinks(True)
        self.api_status_browser.setMinimumHeight(112)
        self.api_status_browser.setMaximumHeight(152)
        self.api_status_browser.document().setDocumentMargin(6)
        api_layout.addWidget(self.api_status_browser)

        self.api_hint_label = QLabel(tr(self.language, "api_hint"))
        self.api_hint_label.setObjectName("helperLabel")
        self.api_hint_label.setWordWrap(True)
        self.api_hint_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        api_layout.addWidget(self.api_hint_label)
        api_layout.addStretch()

        about_tab, about_layout = self._create_tab_page()
        self.tabs.addTab(about_tab, "Über" if self.language == "de" else "About")

        self.about_browser = QTextBrowser()
        self.about_browser.setObjectName("aboutBrowser")
        self.about_browser.setReadOnly(True)
        self.about_browser.setOpenExternalLinks(True)
        self.about_browser.setMinimumHeight(320)
        self.about_browser.document().setDocumentMargin(8)
        about_layout.addWidget(self.about_browser, 1)

        self.about_status_label = QLabel("")
        self.about_status_label.setObjectName("helperLabel")
        self.about_status_label.setWordWrap(True)
        self.about_status_label.hide()
        about_layout.addWidget(self.about_status_label)

        self.about_button_grid = QGridLayout()
        self.about_button_grid.setContentsMargins(0, 0, 0, 0)
        self.about_button_grid.setHorizontalSpacing(10)
        self.about_button_grid.setVerticalSpacing(10)
        self.about_button_grid.setColumnStretch(0, 1)
        self.about_button_grid.setColumnStretch(1, 1)
        about_layout.addLayout(self.about_button_grid)

        self.check_updates_button = QPushButton("Auf Updates prüfen" if self.language == "de" else "Check for updates")
        self.check_updates_button.setObjectName("ghostButton")
        self.check_updates_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.about_button_grid.addWidget(self.check_updates_button, 0, 0)

        self.readme_button = QPushButton("README.md öffnen" if self.language == "de" else "Open README.md")
        self.readme_button.setObjectName("ghostButton")
        self.readme_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.about_button_grid.addWidget(self.readme_button, 0, 1)

        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._style_dialog_buttons(self.dialog_buttons)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch()
        button_row.addWidget(self.dialog_buttons)
        button_row.addStretch()
        layout.addLayout(button_row)

    def _style_dialog_buttons(self, buttons: QDialogButtonBox) -> None:
        buttons.setCenterButtons(False)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        if ok_button is not None:
            ok_button.setObjectName("primaryButton")
            ok_button.setAutoDefault(False)
            ok_button.setDefault(False)
            ok_button.setMinimumWidth(136)
            ok_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        if cancel_button is not None:
            cancel_button.setObjectName("ghostButton")
            cancel_button.setAutoDefault(False)
            cancel_button.setDefault(False)
            cancel_button.setMinimumWidth(136)
            cancel_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def _create_tab_page(self) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(14)
        return page, layout


class HistoryDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, language: str = "de") -> None:
        super().__init__(parent)
        self.language = normalize_language(language)
        self.setWindowTitle(tr(self.language, "history"))
        self.setMinimumSize(500, 500)
        self.resize(520, 560)
        self.setModal(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel(tr(self.language, "history_title"))
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        self.info_label = QLabel(tr(self.language, "no_history"))
        self.info_label.setObjectName("settingsLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        layout.addWidget(self.history_list, 1)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        layout.addLayout(button_row)

        self.export_button = QPushButton(tr(self.language, "export_history"))
        self.export_button.setObjectName("ghostButton")
        self.export_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_row.addWidget(self.export_button)

        self.clear_button = QPushButton(tr(self.language, "clear_history"))
        self.clear_button.setObjectName("ghostButton")
        self.clear_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_row.addWidget(self.clear_button)


class SkillsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, language: str = "de") -> None:
        super().__init__(parent)
        self.language = normalize_language(language)
        self.setWindowTitle(tr(self.language, "skills_title"))
        self.setMinimumSize(680, 620)
        self.resize(760, 720)
        self.setModal(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel(tr(self.language, "skills_heading"))
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        hint = QLabel(tr(self.language, "skills_hint"))
        hint.setObjectName("settingsLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.content = QTextBrowser()
        self.content.setReadOnly(True)
        self.content.setOpenExternalLinks(True)
        self.content.setObjectName("assistantOutput")
        self.content.setHtml(tr(self.language, "skills_content_html"))
        layout.addWidget(self.content, 1)


class ChatGPTWebDialog(QDialog):
    _shared_profile = None

    def __init__(self, parent: QWidget | None = None, language: str = "de") -> None:
        super().__init__(parent)
        self.language = normalize_language(language)
        self.setWindowTitle("ChatGPT Web")
        self.setMinimumSize(900, 680)
        self.resize(1080, 820)
        self.setModal(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel(tr(self.language, "chatgpt_title"))
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        hint = QLabel(tr(self.language, "chatgpt_hint"))
        hint.setObjectName("settingsLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        security_note = QLabel(tr(self.language, "chatgpt_security_note"))
        security_note.setObjectName("helperLabel")
        security_note.setWordWrap(True)
        layout.addWidget(security_note)

        if QWebEngineView is None:
            self.browser = None
            fallback = QLabel(tr(self.language, "webengine_missing"))
            fallback.setObjectName("apiStatusLabel")
            fallback.setWordWrap(True)
            layout.addWidget(fallback, 1)
        else:
            self.browser = QWebEngineView()
            if QWebEnginePage is not None:
                self.browser.setPage(QWebEnginePage(self._web_profile(), self.browser))
            layout.addWidget(self.browser, 1)

    def load_query(self, query: str) -> bool:
        if self.browser is None:
            return False
        self.browser.setUrl(QUrl(f"https://chatgpt.com/?q={quote(query)}"))
        return True

    @classmethod
    def _web_profile(cls):
        if QWebEngineProfile is None:
            return None
        if cls._shared_profile is not None:
            return cls._shared_profile

        profile_root = Path.home() / ".config" / "matrix-calculator" / "chatgpt-web-profile"
        storage_path = profile_root / "storage"
        cache_path = profile_root / "cache"
        cls._ensure_private_dir(profile_root)
        cls._ensure_private_dir(storage_path)
        cls._ensure_private_dir(cache_path)

        profile = QWebEngineProfile("matrix-chatgpt", None)
        profile.setPersistentStoragePath(str(storage_path))
        profile.setCachePath(str(cache_path))
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        cls._shared_profile = profile
        return profile

    @staticmethod
    def _ensure_private_dir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(path, 0o700)
        except OSError:
            pass
