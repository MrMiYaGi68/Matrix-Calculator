# SPDX-License-Identifier: GPL-3.0-or-later
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from core.assistant_flow import assistant_mode_label, normalize_assistant_mode, solve_natural_query
import ui.dialogs as dialogs_module
from ui.dialogs import ChatGPTWebDialog
from ui.history_actions import (
    clear_history,
    on_history_clicked,
    open_chatgpt_web_for_current_query,
    open_history_dialog,
    open_skills_dialog,
)


class RefactoredModulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_normalize_assistant_mode_understands_known_labels(self):
        self.assertEqual(normalize_assistant_mode("Lokal zuerst"), "browser_fallback")
        self.assertEqual(normalize_assistant_mode("Direkt per API (Erweitert)"), "api_direct")
        self.assertEqual(normalize_assistant_mode("unknown"), "browser_fallback")

    def test_assistant_mode_label_uses_translator(self):
        translate = lambda key: {"mode_api": "API", "mode_browser": "Browser"}[key]
        self.assertEqual(assistant_mode_label(None, active_mode="browser_fallback", translate=translate), "Browser")
        self.assertEqual(assistant_mode_label("api_direct", active_mode="browser_fallback", translate=translate), "API")

    def test_solve_natural_query_empty_input_only_posts_hint(self):
        messages = []

        class DummyInput:
            def text(self):
                return "   "

        window = type("Window", (), {})()
        window.ai_input = DummyInput()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._tr = lambda key: {"enter_query": "Bitte Eingabe"}[key]

        solve_natural_query(window)

        self.assertEqual(messages, [("system", "Bitte Eingabe")])

    def test_solve_natural_query_routes_expression_and_openai_request(self):
        messages = []
        statuses = []
        evaluated = []
        asked = []

        class DummyInput:
            def __init__(self):
                self.value = "komplexe frage"

            def text(self):
                return self.value

            def clear(self):
                self.value = ""

        class DummyMode:
            def currentText(self):
                return "Direkt per API (Erweitert)"

        window = type("Window", (), {})()
        window.ai_input = DummyInput()
        window.mode_preference = DummyMode()
        window.ai_api_key = "test-key"
        window.ai_step_by_step = True
        window.app_language = "de"
        window.pending_clarification = None
        window.last_ai_query = ""
        window.ai_status = type("Status", (), {"setText": lambda self, text: statuses.append(text)})()
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._update_ai_live_preview = lambda text: None
        window._solve_local_natural_query = lambda query: ("2+2", "4", "Direkt ausgewertet.")
        window._build_query_help = lambda query: f"help:{query}"
        window._normalize_assistant_mode = normalize_assistant_mode
        window._build_local_answer = lambda query, expression, answer, explanation: f"{expression}={answer}"
        window._set_expression_and_evaluate = lambda expression: evaluated.append(expression)
        window._ask_openai = lambda query=None: asked.append(query)
        window._tr = lambda key: {
            "mode_browser": "Lokal, dann Browser",
            "clarification_answered": "ok",
            "clarification_needed": "need",
            "local_solved": "solved",
            "local_trying_api": "api",
            "api_direct_missing_key_message": "missing",
            "api_direct_missing_key_status": "missing-status",
            "local_not_solved_message": "nope",
            "local_not_solved_status": "nope-status",
        }[key]

        solve_natural_query(window)

        self.assertEqual(window.last_ai_query, "komplexe frage")
        self.assertEqual(evaluated, ["2+2"])
        self.assertEqual(asked, [])
        self.assertTrue(any(role == "assistant" and "Ergebnis: 4" in text for role, text in messages))
        self.assertIn("solved", statuses)

    def test_on_history_clicked_restores_expression(self):
        updated = []

        class DummyLabel:
            def __init__(self):
                self.value = ""

            def setText(self, text):
                self.value = text

            def text(self):
                return self.value

        window = type("Window", (), {})()
        window.expression = ""
        window.result_label = DummyLabel()
        window.preview_label = DummyLabel()
        window.just_evaluated = True
        window._tr = lambda key: {"history_loaded": "Verlauf geladen"}[key]
        window._update_display = lambda: updated.append(window.expression)

        item = QListWidgetItem("demo")
        item.setData(Qt.UserRole, ("1+1", "2"))

        on_history_clicked(window, item)

        self.assertEqual(window.expression, "1+1")
        self.assertEqual(window.result_label.text(), "2")
        self.assertEqual(window.preview_label.text(), "Verlauf geladen")
        self.assertFalse(window.just_evaluated)
        self.assertEqual(updated, ["1+1"])

    def test_clear_history_resets_dialog_and_preview(self):
        class DummyList:
            def __init__(self):
                self.cleared = False

            def clear(self):
                self.cleared = True

        class DummyLabel:
            def __init__(self):
                self.value = ""

            def setText(self, text):
                self.value = text

            def text(self):
                return self.value

        dialog = type("Dialog", (), {"history_list": DummyList(), "info_label": DummyLabel()})()
        window = type("Window", (), {})()
        window.history_items = [("1+1", "2")]
        window.history_dialog = dialog
        window.preview_label = DummyLabel()
        window._tr = lambda key: {"no_history": "Keine Historie", "history_cleared": "Verlauf gelöscht"}[key]

        clear_history(window)

        self.assertEqual(window.history_items, [])
        self.assertTrue(dialog.history_list.cleared)
        self.assertEqual(dialog.info_label.text(), "Keine Historie")
        self.assertEqual(window.preview_label.text(), "Verlauf gelöscht")

    def test_open_history_and_skills_dialog_noop_when_missing(self):
        window = type("Window", (), {"history_dialog": None, "skills_dialog": None, "history_items": []})()
        open_history_dialog(window)
        open_skills_dialog(window)

    def test_open_chatgpt_web_for_current_query_uses_last_query(self):
        messages = []
        statuses = []

        class DummyInput:
            def text(self):
                return ""

        window = type("Window", (), {})()
        window.ai_input = DummyInput()
        window.last_ai_query = "letzte frage"
        window._append_ai_message = lambda role, text: messages.append((role, text))
        window._open_chatgpt_in_app = lambda query: query == "letzte frage"
        window.ai_status = type("Status", (), {"setText": lambda self, text: statuses.append(text)})()
        window._tr = lambda key: {
            "chatgpt_need_query": "frage fehlt",
            "chatgpt_opened": "geöffnet",
            "chatgpt_unavailable_message": "nicht verfügbar",
            "chatgpt_unavailable_status": "status nv",
        }[key]

        open_chatgpt_web_for_current_query(window)

        self.assertEqual(messages, [])
        self.assertEqual(statuses, ["geöffnet"])

    def test_chatgpt_web_profile_configures_persistent_storage_paths(self):
        class FakeProfile:
            ForcePersistentCookies = object()
            DiskHttpCache = object()

            def __init__(self, name, parent):
                self.name = name
                self.parent = parent
                self._storage_path = ""
                self._cache_path = ""
                self.cache_type = None
                self.cookies_policy = None

            def setPersistentStoragePath(self, path):
                self._storage_path = path

            def setCachePath(self, path):
                self._cache_path = path

            def setHttpCacheType(self, cache_type):
                self.cache_type = cache_type

            def setPersistentCookiesPolicy(self, policy):
                self.cookies_policy = policy

            def persistentStoragePath(self):
                return self._storage_path

            def cachePath(self):
                return self._cache_path

        original_profile_class = dialogs_module.QWebEngineProfile
        original_home = dialogs_module.Path.home
        ChatGPTWebDialog._shared_profile = None
        with tempfile.TemporaryDirectory() as tmpdir:
            dialogs_module.QWebEngineProfile = FakeProfile
            dialogs_module.Path.home = staticmethod(lambda: Path(tmpdir))
            try:
                profile = ChatGPTWebDialog._web_profile()
                self.assertIsNotNone(profile)
                self.assertIn("chatgpt-web-profile/storage", profile.persistentStoragePath())
                self.assertIn("chatgpt-web-profile/cache", profile.cachePath())
                self.assertTrue(Path(profile.persistentStoragePath()).is_dir())
                self.assertTrue(Path(profile.cachePath()).is_dir())
                self.assertIs(profile.cache_type, FakeProfile.DiskHttpCache)
                self.assertIs(profile.cookies_policy, FakeProfile.ForcePersistentCookies)
            finally:
                ChatGPTWebDialog._shared_profile = None
                dialogs_module.QWebEngineProfile = original_profile_class
                dialogs_module.Path.home = original_home


if __name__ == "__main__":
    unittest.main()
