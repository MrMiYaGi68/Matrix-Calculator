# SPDX-License-Identifier: GPL-3.0-or-later
import os
import unittest

from core import openai_support


class OpenAISupportTest(unittest.TestCase):
    def test_normalize_model_keeps_supported_values_and_maps_old_aliases(self):
        self.assertEqual(openai_support.normalize_openai_model("gpt-5.4-mini"), "gpt-5-mini")
        self.assertEqual(openai_support.normalize_openai_model("gpt-5.4"), "gpt-5.1")
        self.assertEqual(openai_support.normalize_openai_model("gpt-5.2"), "gpt-5.2")
        self.assertEqual(openai_support.normalize_openai_model("unknown"), "gpt-5-mini")

    def test_choose_auto_model_prefers_highest_exact_gpt5(self):
        self.assertEqual(
            openai_support.choose_auto_openai_model(["gpt-5", "gpt-5-mini", "gpt-5.1", "gpt-5.2"]),
            "gpt-5.2",
        )

    def test_build_headers_adds_optional_org_and_project(self):
        old_org = os.environ.get("OPENAI_ORGANIZATION")
        old_project = os.environ.get("OPENAI_PROJECT")
        os.environ["OPENAI_ORGANIZATION"] = "org_test"
        os.environ["OPENAI_PROJECT"] = "proj_test"
        try:
            headers = openai_support.build_openai_request_headers("key_test")
        finally:
            if old_org is None:
                os.environ.pop("OPENAI_ORGANIZATION", None)
            else:
                os.environ["OPENAI_ORGANIZATION"] = old_org
            if old_project is None:
                os.environ.pop("OPENAI_PROJECT", None)
            else:
                os.environ["OPENAI_PROJECT"] = old_project

        self.assertEqual(headers["Authorization"], "Bearer key_test")
        self.assertEqual(headers["OpenAI-Organization"], "org_test")
        self.assertEqual(headers["OpenAI-Project"], "proj_test")

    def test_extract_output_text_supports_responses_shape(self):
        payload = {
            "output": [
                {
                    "content": [
                        {"text": "Teil 1"},
                        {"text": "Teil 2"},
                    ]
                }
            ]
        }
        self.assertEqual(openai_support.extract_openai_output_text(payload), "Teil 1\nTeil 2")

    def test_error_messages_are_specific(self):
        message = openai_support.describe_openai_api_error(
            429,
            {"error": {"code": "insufficient_quota", "message": "quota exceeded"}},
        )
        self.assertIn("API-Projekt", message)
        self.assertIn("Guthaben", message)


if __name__ == "__main__":
    unittest.main()
