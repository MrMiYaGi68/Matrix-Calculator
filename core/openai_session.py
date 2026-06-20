# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from core.openai_client import OpenAIClient


def resolve_openai_model(api_key: str, fallback_model: str) -> str:
    return OpenAIClient(api_key).resolve_model(fallback_model)


def perform_openai_request(
    api_key: str,
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
    return OpenAIClient(api_key).perform_request(
        query_input=query_input,
        model=model,
        response_language=response_language,
        step_by_step=step_by_step,
        max_output_tokens=max_output_tokens,
        missing_key_error=missing_key_error,
        requests_missing_error=requests_missing_error,
        empty_response_error=empty_response_error,
    )


def build_openai_input(
    query: str,
    *,
    use_context: bool,
    messages: list[tuple[str, str]],
    user_label: str,
    assistant_label: str,
    system_label: str,
) -> str:
    if not use_context or not messages:
        return query
    recent = messages[-8:]
    transcript = []
    for role, text in recent:
        prefix = {
            "user": user_label,
            "assistant": assistant_label,
            "system": system_label,
        }.get(role, role)
        transcript.append(f"{prefix}: {text}")
    transcript.append(f"{user_label}: {query}")
    return "\n\n".join(transcript)
