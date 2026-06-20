# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from core.natural_query import CLARIFICATION_EXPRESSION, parse_interest_query, solve_interest_choice
from core.natural_query.response import build_local_answer


LocalSolver = Callable[[str], tuple[str, str, str] | None]
TextBuilder = Callable[[str], str]
ModeNormalizer = Callable[[str], str]
Translator = Callable[[str], str]


@dataclass
class AssistantDecision:
    messages: list[tuple[str, str]] = field(default_factory=list)
    status: str = ""
    expression_to_evaluate: str | None = None
    openai_query: str | None = None
    pending_clarification: dict[str, object] | None = None


class AssistantService:
    def __init__(
        self,
        *,
        translate: Translator,
        local_solver: LocalSolver,
        query_help_builder: TextBuilder,
        mode_normalizer: ModeNormalizer,
        step_by_step: bool,
        app_language: str,
    ):
        self.translate = translate
        self.local_solver = local_solver
        self.query_help_builder = query_help_builder
        self.mode_normalizer = mode_normalizer
        self.step_by_step = step_by_step
        self.app_language = app_language

    def solve(
        self,
        *,
        query: str,
        pending_clarification: dict[str, object] | None,
        mode_text: str,
        has_api_key: bool,
    ) -> AssistantDecision:
        followup = self._resolve_pending_clarification(query, pending_clarification)
        if followup is not None:
            expression, answer, explanation, pending = followup
            decision = AssistantDecision(
                messages=[("assistant", self._build_local_answer(query, expression, answer, explanation))],
                status=self.translate("clarification_answered"),
                pending_clarification=pending,
            )
            if expression and expression != CLARIFICATION_EXPRESSION:
                decision.expression_to_evaluate = expression
            return decision

        local = self.local_solver(query)
        if local is not None:
            expression, answer, explanation = local
            pending = self._remember_pending_clarification(query, expression, answer)
            decision = AssistantDecision(
                messages=[("assistant", self._build_local_answer(query, expression, answer, explanation))],
                pending_clarification=pending,
            )
            if expression == CLARIFICATION_EXPRESSION:
                decision.status = self.translate("clarification_needed")
            else:
                decision.status = self.translate("local_solved")
                if expression:
                    decision.expression_to_evaluate = expression
            return decision

        mode = self.mode_normalizer(mode_text)
        if mode == "api_direct" and has_api_key:
            return AssistantDecision(
                messages=[("system", self.translate("local_trying_api"))],
                openai_query=query,
                pending_clarification=None,
            )

        if mode == "api_direct" and not has_api_key:
            return AssistantDecision(
                messages=[
                    ("system", self.translate("api_direct_missing_key_message")),
                    ("system", self.query_help_builder(query)),
                ],
                status=self.translate("api_direct_missing_key_status"),
                pending_clarification=None,
            )

        return AssistantDecision(
            messages=[
                ("system", self.translate("local_not_solved_message")),
                ("system", self.query_help_builder(query)),
            ],
            status=self.translate("local_not_solved_status"),
            pending_clarification=None,
        )

    def _build_local_answer(self, query: str, expression: str, answer: str, explanation: str) -> str:
        language = "en" if self.app_language == "en" else None
        return build_local_answer(query, expression, answer, explanation, self.step_by_step, language)

    def _remember_pending_clarification(
        self,
        query: str,
        expression: str,
        answer: str,
    ) -> dict[str, object] | None:
        if expression != CLARIFICATION_EXPRESSION or "Zins" not in answer:
            return None
        parsed = parse_interest_query(query.lower().strip().replace(",", "."))
        if parsed is None:
            return None
        capital, rate, years = parsed
        return {
            "type": "interest",
            "capital": capital,
            "rate": rate,
            "years": years,
        }

    def _resolve_pending_clarification(
        self,
        query: str,
        pending: dict[str, object] | None,
    ) -> tuple[str, str, str, dict[str, object] | None] | None:
        if not pending:
            return None
        if pending.get("type") != "interest":
            return None
        result = solve_interest_choice(
            float(pending["capital"]),
            float(pending["rate"]),
            float(pending["years"]),
            query,
        )
        if result is None:
            return (
                CLARIFICATION_EXPRESSION,
                "Ich brauche noch eine eindeutige Auswahl.",
                "Bitte antworte mit 'Zinsbetrag', 'Endbetrag' oder 'Zinseszins'.",
                pending,
            )
        expression, answer, explanation = result.as_tuple()
        return expression, answer, explanation, None
