# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os

from core.assistant_service import AssistantService
from core.i18n import tr


def normalize_assistant_mode(text: str) -> str:
    mapping = {
        "Lokal zuerst": "browser_fallback",
        "Lokal, dann Browser": "browser_fallback",
        tr("en", "mode_browser"): "browser_fallback",
        tr("es", "mode_browser"): "browser_fallback",
        tr("fr", "mode_browser"): "browser_fallback",
        tr("it", "mode_browser"): "browser_fallback",
        tr("tr", "mode_browser"): "browser_fallback",
        "OpenAI direkt": "api_direct",
        "Direkt per API (Erweitert)": "api_direct",
        tr("en", "mode_api"): "api_direct",
        tr("es", "mode_api"): "api_direct",
        tr("fr", "mode_api"): "api_direct",
        tr("it", "mode_api"): "api_direct",
        tr("tr", "mode_api"): "api_direct",
    }
    return mapping.get(text, "browser_fallback")


def assistant_mode_label(mode: str | None, *, active_mode: str, translate) -> str:
    if (mode or active_mode) == "api_direct":
        return translate("mode_api")
    return translate("mode_browser")


def solve_natural_query(window) -> None:
    query = window.ai_input.text().strip()
    if not query:
        window._append_ai_message("system", window._tr("enter_query"))
        return

    window.last_ai_query = query
    window._append_ai_message("user", query)
    window.ai_input.clear()
    window._update_ai_live_preview("")
    decision = AssistantService(
        translate=window._tr,
        local_solver=window._solve_local_natural_query,
        query_help_builder=window._build_query_help,
        mode_normalizer=window._normalize_assistant_mode,
        step_by_step=getattr(window, "ai_step_by_step", True),
        app_language=getattr(window, "app_language", "de"),
    ).solve(
        query=query,
        pending_clarification=getattr(window, "pending_clarification", None),
        mode_text=window.mode_preference.currentText() if hasattr(window, "mode_preference") else window._tr("mode_browser"),
        has_api_key=bool((getattr(window, "ai_api_key", "") or os.getenv("OPENAI_API_KEY", "")).strip()),
    )
    window.pending_clarification = decision.pending_clarification
    for role, text in decision.messages:
        window._append_ai_message(role, text)
    if decision.status:
        window.ai_status.setText(decision.status)
    if decision.expression_to_evaluate:
        window._set_expression_and_evaluate(decision.expression_to_evaluate)
    if decision.openai_query:
        window._ask_openai(decision.openai_query)
