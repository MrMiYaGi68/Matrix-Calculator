# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from core.expression_parser import CalculatorError
from core.openai_support import (
    OPENAI_MODELS_URL,
    OPENAI_RESPONSES_URL,
    build_openai_request_headers,
    choose_auto_openai_model,
    describe_openai_api_error,
    extract_openai_output_text,
)


class OpenAIClient:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()

    def has_api_key(self) -> bool:
        return bool(self.api_key)

    def headers(self) -> dict[str, str]:
        return build_openai_request_headers(self.api_key)

    def fetch_available_models(self) -> list[str]:
        if not self.api_key:
            return []
        try:
            import requests
        except ImportError:
            return []

        try:
            response = requests.get(OPENAI_MODELS_URL, headers=self.headers(), timeout=20)
        except requests.exceptions.RequestException:
            return []

        if response.status_code >= 400:
            return []
        try:
            data = response.json()
        except ValueError:
            return []
        return [item.get("id", "") for item in data.get("data", []) if item.get("id")]

    def resolve_model(self, fallback: str) -> str:
        if not self.api_key:
            return fallback
        return choose_auto_openai_model(self.fetch_available_models())

    def perform_request(
        self,
        *,
        query_input: str,
        model: str,
        response_language: str,
        step_by_step: bool,
        max_output_tokens: int,
        missing_key_error: str,
        requests_missing_error: str,
        empty_response_error: str,
    ) -> str:
        if not self.api_key:
            raise CalculatorError(missing_key_error)

        try:
            import requests
        except ImportError as exc:
            raise CalculatorError(requests_missing_error) from exc

        instructions = (
            f"Du bist ein präziser Rechenassistent. Antworte auf {response_language}. "
            "Löse Rechenfragen kurz und korrekt. "
            "Gib immer erst das Ergebnis. "
            + (
                "Danach erkläre die Rechenschritte knapp und geordnet. "
                if step_by_step
                else "Danach höchstens eine sehr kurze Erklärung. "
            )
            + "Wenn sinnvoll, gib den verwendeten Ausdruck an."
        )
        payload = {
            "model": model,
            "instructions": instructions,
            "input": query_input,
            "max_output_tokens": max_output_tokens,
        }

        try:
            response = requests.post(
                OPENAI_RESPONSES_URL,
                headers=self.headers(),
                json=payload,
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            raise CalculatorError(
                "Keine Verbindung zu OpenAI möglich. Bitte prüfe Internetzugang, Firewall, DNS oder Proxy."
            ) from exc

        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code >= 400:
            raise CalculatorError(describe_openai_api_error(response.status_code, data))

        output_text = extract_openai_output_text(data or {})
        if not output_text:
            raise CalculatorError(empty_response_error)
        return output_text
