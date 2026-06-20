# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.openai_client import OpenAIClient


class OpenAIClientTest(unittest.TestCase):
    def test_without_api_key_has_no_key_and_uses_fallback_model(self):
        client = OpenAIClient("")
        self.assertFalse(client.has_api_key())
        self.assertEqual(client.resolve_model("gpt-5-mini"), "gpt-5-mini")

    def test_headers_use_api_key(self):
        client = OpenAIClient("key_test")
        self.assertEqual(client.headers()["Authorization"], "Bearer key_test")


if __name__ == "__main__":
    unittest.main()
