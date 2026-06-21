# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectGovernanceTest(unittest.TestCase):
    def test_required_governance_documents_exist(self):
        expected = [
            "CHANGELOG.md",
            "LICENSE",
            "SECURITY.md",
            "docs/ARCHITECTURE.md",
            "docs/CHANGE_CONTROL.md",
            "docs/DATA_PROTECTION.md",
            "docs/PRIVACY.md",
            "docs/PRODUCT_BRIEF.md",
            "docs/RISK_REGISTER.md",
            "docs/ROADMAP.md",
            "docs/RUNBOOK.md",
            "docs/SUPPORT.md",
            "docs/TEST_STRATEGY.md",
            "docs/adr/0001-local-first-api-key-handling.md",
        ]
        for relative_path in expected:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).is_file())

    def test_ci_workflow_exists(self):
        workflow = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover", text)
        self.assertIn("desktop-file-validate", text)
        self.assertIn("PYTHONPYCACHEPREFIX", text)
        self.assertIn("__pycache__", text)

    def test_release_zip_builder_exists(self):
        script = PROJECT_ROOT / "tools" / "build_release_zip.py"
        self.assertTrue(script.is_file())
        text = script.read_text(encoding="utf-8")
        self.assertIn("validate_release_zip", text)
        self.assertIn("__pycache__", text)
        self.assertIn(".pyc", text)
        self.assertIn('"dist"', text)
        self.assertIn(".egg-info", text)
        self.assertIn(".whl", text)


if __name__ == "__main__":
    unittest.main()
