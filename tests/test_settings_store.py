# SPDX-License-Identifier: GPL-3.0-or-later
import json
import tempfile
import unittest
from pathlib import Path

from core.settings import AppSettings, SettingsStore


class SettingsStoreTest(unittest.TestCase):
    def test_read_migrates_legacy_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(
                json.dumps({"openai_api_key": "sk-legacy", "theme_name": "light"}),
                encoding="utf-8",
            )

            data = SettingsStore(path).read()

            self.assertEqual(data["theme_name"], "light")
            self.assertNotIn("openai_api_key", data)
            self.assertNotIn("sk-legacy", path.read_text(encoding="utf-8"))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_write_does_not_persist_api_key_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            SettingsStore(path).write(
                AppSettings(
                    openai_model="gpt-5-mini",
                    assistant_mode="Lokal, dann Browser",
                    app_language="de",
                    ai_step_by_step=True,
                    ai_use_context=True,
                    theme_name="graphite",
                )
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("openai_api_key", data)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
