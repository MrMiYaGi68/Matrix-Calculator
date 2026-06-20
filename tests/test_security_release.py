# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import tempfile
import tomllib
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from calculator import MatrixCalculatorWindow


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SecurityReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_save_settings_does_not_persist_openai_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            window = MatrixCalculatorWindow.__new__(MatrixCalculatorWindow)
            window.CONFIG_PATH = Path(tmp) / "settings.json"
            window.ai_api_key = "sk-test-secret"
            window.ai_model = "gpt-5-mini"
            window.assistant_mode = "browser_fallback"
            window.app_language = "de"
            window.ai_step_by_step = True
            window.ai_use_context = True
            window.theme_name = "graphite"
            window._normalize_openai_model = MatrixCalculatorWindow._normalize_openai_model.__get__(
                window, MatrixCalculatorWindow
            )
            window._assistant_mode_label = MatrixCalculatorWindow._assistant_mode_label.__get__(
                window, MatrixCalculatorWindow
            )

            MatrixCalculatorWindow._save_settings(window)

            data = json.loads(window.CONFIG_PATH.read_text(encoding="utf-8"))
            self.assertNotIn("openai_api_key", data)
            self.assertNotIn("sk-test-secret", window.CONFIG_PATH.read_text(encoding="utf-8"))
            self.assertEqual(window.CONFIG_PATH.stat().st_mode & 0o777, 0o600)

    def test_desktop_file_has_no_absolute_user_paths(self):
        desktop_file = PROJECT_ROOT / "MatrixCalculator.desktop"
        text = desktop_file.read_text(encoding="utf-8")
        self.assertNotIn(str(Path.home()), text)
        self.assertIn("Exec=matrix-calculator", text)

    def test_discover_desktop_file_uses_reverse_dns_app_id(self):
        desktop_file = PROJECT_ROOT / "io.github.MrMiYaGi68.MatrixCalculator.desktop"
        text = desktop_file.read_text(encoding="utf-8")
        self.assertIn("Exec=matrix-calculator", text)
        self.assertIn("Icon=io.github.MrMiYaGi68.MatrixCalculator", text)
        self.assertNotIn(str(Path.home()), text)

    def test_appstream_metadata_tracks_release_and_launcher(self):
        metainfo_file = PROJECT_ROOT / "io.github.MrMiYaGi68.MatrixCalculator.metainfo.xml"
        text = metainfo_file.read_text(encoding="utf-8")
        self.assertIn("<id>io.github.MrMiYaGi68.MatrixCalculator</id>", text)
        self.assertIn(
            "<launchable type=\"desktop-id\">io.github.MrMiYaGi68.MatrixCalculator.desktop</launchable>",
            text,
        )
        self.assertIn("<release version=\"1.0.1\" date=\"2026-04-29\"/>", text)

    def test_release_metadata_is_1_0_ready(self):
        pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = pyproject["project"]
        self.assertEqual(project["version"], "1.0.1")
        self.assertIn("Development Status :: 5 - Production/Stable", project["classifiers"])
        self.assertIn("PySide6>=6.6", project["dependencies"])
        self.assertNotIn("requests>=2.31", project["dependencies"])

        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## 1.0.1 - 2026-04-29", changelog)
        self.assertNotIn("Unreleased", changelog)

    def test_load_settings_removes_legacy_openai_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "openai_api_key": "sk-legacy-secret",
                        "openai_model": "gpt-5-mini",
                        "assistant_mode": "Lokal, dann Browser",
                        "app_language": "de",
                        "ai_step_by_step": True,
                        "ai_use_context": True,
                        "theme_name": "graphite",
                    }
                ),
                encoding="utf-8",
            )

            window = MatrixCalculatorWindow()
            window.CONFIG_PATH = config_path
            window.ai_api_key = ""
            window._load_settings()

            text = config_path.read_text(encoding="utf-8")
            self.assertNotIn("openai_api_key", text)
            self.assertNotIn("sk-legacy-secret", text)
            self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)

    def test_load_settings_tolerates_invalid_scalar_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "openai_model": 123,
                        "assistant_mode": None,
                        "app_language": 45,
                        "ai_step_by_step": True,
                        "ai_use_context": True,
                        "theme_name": None,
                    }
                ),
                encoding="utf-8",
            )

            window = MatrixCalculatorWindow()
            window.CONFIG_PATH = config_path
            window._load_settings()

            self.assertEqual(window.ai_model, "gpt-5-mini")
            self.assertEqual(window.theme_name, "graphite")

    def test_privacy_defaults_disable_chat_context_until_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_config_path = MatrixCalculatorWindow.CONFIG_PATH
            MatrixCalculatorWindow.CONFIG_PATH = Path(tmp) / "settings.json"
            try:
                window = MatrixCalculatorWindow()
            finally:
                MatrixCalculatorWindow.CONFIG_PATH = old_config_path
            self.assertFalse(window.ai_use_context)

    def test_openai_request_requires_transfer_confirmation(self):
        messages = []
        statuses = []
        window = MatrixCalculatorWindow.__new__(MatrixCalculatorWindow)
        window.ai_input = type("Input", (), {"text": lambda self: ""})()
        window.ai_api_key = "sk-test"
        window._confirm_online_ai_transfer = lambda: False
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window.ai_status = type("Status", (), {"setText": lambda self, text: statuses.append(text)})()
        window._tr = MatrixCalculatorWindow._tr.__get__(window, MatrixCalculatorWindow)
        window.app_language = "de"
        window.ai_worker = None
        window._resolve_openai_model = lambda: self.fail("OpenAI model resolution should not run")
        window._perform_openai_request = lambda *args, **kwargs: self.fail("OpenAI request should not run")

        MatrixCalculatorWindow._ask_openai(window, "personenbezogene daten")

        self.assertTrue(any("Datenübermittlung" in text for _, text in messages))
        self.assertIn("Online-KI abgebrochen.", statuses)


if __name__ == "__main__":
    unittest.main()
