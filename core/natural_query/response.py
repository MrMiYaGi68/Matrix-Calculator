from __future__ import annotations

from core.formatting import pretty_expression
from core.natural_query.language import is_english_query, translate_local_text
from core.natural_query.types import CLARIFICATION_EXPRESSION


def build_local_answer(
    query: str,
    expression: str,
    answer: str,
    explanation: str,
    step_by_step: bool,
    language: str | None = None,
) -> str:
    lines: list[str] = []
    query_lower = query.lower()
    english = language == "en" or (language is None and is_english_query(query))
    if any(term in query_lower for term in ["gegeben", "gesucht", "given", "find"]):
        lines.append(translate_local_text("Aufgabe erkannt", english))
    if expression == CLARIFICATION_EXPRESSION:
        lines.append(answer)
        if explanation:
            lines.append("")
            lines.append(explanation)
        return "\n".join(lines)
    lines.append(f"{translate_local_text('Ergebnis', english)}: {answer}")
    if expression and not expression.startswith("x="):
        lines.append(f"{translate_local_text('Rechnung', english)}: {pretty_expression(expression)}")
    elif expression:
        lines.append(f"{translate_local_text('Lösung', english)}: {expression}")
    if step_by_step and explanation:
        lines.append("")
        translated_explanation = translate_local_text(explanation, english)
        if any(term in query_lower for term in ["gegeben", "gesucht", "given", "find"]):
            lines.append(f"{translate_local_text('Vorgehen', english)}: {translated_explanation}")
        else:
            lines.append(f"{translate_local_text('Erklärung', english)}: {translated_explanation}")
    return "\n".join(lines)
