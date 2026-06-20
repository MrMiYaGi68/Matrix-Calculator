# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from core.assistant_service import AssistantService
from core.natural_query import CLARIFICATION_EXPRESSION


class AssistantServiceTest(unittest.TestCase):
    def _service(self, local_solver):
        translations = {
            "clarification_answered": "Rückfrage beantwortet.",
            "clarification_needed": "Rückfrage nötig.",
            "local_solved": "Lokal gelöst.",
            "local_trying_api": "Lokal nicht sicher erkannt. Ich versuche die API.",
            "api_direct_missing_key_message": "Für den API-Modus fehlt ein API-Key.",
            "api_direct_missing_key_status": "Kein API-Key für Direktmodus vorhanden.",
            "local_not_solved_message": "Lokal nicht sicher erkannt.",
            "local_not_solved_status": "Lokaler Parser konnte die Anfrage nicht sicher lösen.",
        }
        return AssistantService(
            translate=lambda key: translations[key],
            local_solver=local_solver,
            query_help_builder=lambda query: f"help:{query}",
            mode_normalizer=lambda text: "api_direct" if text == "api" else "browser_fallback",
            step_by_step=True,
            app_language="de",
        )

    def test_local_solution_returns_assistant_message_and_expression(self):
        service = self._service(lambda query: ("2+2", "4", "Direkt ausgewertet."))

        decision = service.solve(
            query="2+2",
            pending_clarification=None,
            mode_text="browser",
            has_api_key=False,
        )

        self.assertEqual(decision.status, "Lokal gelöst.")
        self.assertEqual(decision.expression_to_evaluate, "2+2")
        self.assertEqual(decision.messages[0][0], "assistant")
        self.assertIn("4", decision.messages[0][1])

    def test_api_mode_with_key_requests_openai(self):
        service = self._service(lambda query: None)

        decision = service.solve(
            query="komplex",
            pending_clarification=None,
            mode_text="api",
            has_api_key=True,
        )

        self.assertEqual(decision.openai_query, "komplex")
        self.assertEqual(decision.messages, [("system", "Lokal nicht sicher erkannt. Ich versuche die API.")])

    def test_clarification_can_keep_pending_state(self):
        service = self._service(lambda query: None)

        decision = service.solve(
            query="unklar",
            pending_clarification={"type": "interest", "capital": 1000, "rate": 5, "years": 3},
            mode_text="browser",
            has_api_key=False,
        )

        self.assertEqual(decision.expression_to_evaluate, None)
        self.assertEqual(decision.pending_clarification["type"], "interest")
        self.assertIn("eindeutige Auswahl", decision.messages[0][1])


if __name__ == "__main__":
    unittest.main()
