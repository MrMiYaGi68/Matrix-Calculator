# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectStructureTest(unittest.TestCase):
    def test_root_calculator_is_the_single_app_entrypoint(self):
        self.assertTrue((PROJECT_ROOT / "calculator.py").is_file())
        self.assertFalse((PROJECT_ROOT / "meine-app" / "calculator.py").exists())

    def test_expected_source_modules_exist(self):
        expected = [
            "core/formatting.py",
            "core/assistant_service.py",
            "core/expression_parser.py",
            "core/openai_client.py",
            "core/openai_support.py",
            "core/settings.py",
            "core/natural_query/algebra.py",
            "core/natural_query/common.py",
            "core/natural_query/elementary.py",
            "core/natural_query/language.py",
            "core/natural_query/response.py",
            "core/natural_query/simple_arithmetic.py",
            "core/natural_query/statistics.py",
            "core/natural_query/types.py",
            "ui/button_config.py",
            "ui/dialogs.py",
        ]
        for relative_path in expected:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
