from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import NaturalQueryResult


_NAME = r"[a-zäöüß][a-zäöüß0-9_-]*"
_NUMBER = r"-?\d+(?:\.\d+)?"
_FILLER_WORDS = {
    "die",
    "der",
    "das",
    "ein",
    "eine",
    "einer",
    "einem",
    "einen",
    "the",
    "a",
    "an",
}


def solve_relationship_query(normalized: str) -> NaturalQueryResult | None:
    """Solve small word problems where two named quantities are related."""
    text = _normalize_relationship_text(normalized)
    relation = _extract_relation(text)
    if relation is None:
        return None

    left, right, kind, amount = relation
    total = _extract_total(text, left, right)
    if total is None:
        return None

    if kind == "factor":
        if amount == -1:
            right_value = total * 2
            left_value = right_value / 2
        elif amount > 0:
            right_value = total / (amount + 1)
            left_value = amount * right_value
        else:
            return None
        expression = f"{format_number(total)}/({format_number(amount)}+1)" if amount > 0 else f"{format_number(total)}*2"
        explanation = (
            f"Aus der Beziehung {left} = {format_number(amount)} * {right} und der Summe "
            f"{format_number(total)} wird erst {right} berechnet."
        )
    else:
        right_value = (total - amount) / 2
        left_value = right_value + amount
        expression = f"({format_number(total)}-{format_number(amount)})/2"
        explanation = (
            f"Aus der Beziehung {left} = {right} + {format_number(amount)} und der Summe "
            f"{format_number(total)} wird erst {right} berechnet."
        )

    values = {left: left_value, right: right_value}
    target = _extract_target(text, left, right)
    if target:
        target_expression = _target_expression(expression, target, left, kind, amount)
        return NaturalQueryResult(*format_local_result(target_expression, values[target], explanation))

    answer = f"{left} = {format_number(left_value)}, {right} = {format_number(right_value)}"
    return NaturalQueryResult(
        f"{left}={format_number(left_value)}, {right}={format_number(right_value)}",
        answer,
        explanation,
    )


def _normalize_relationship_text(normalized: str) -> str:
    replacements = {
        "twice as much as": "doppelt so viel wie",
        "twice as old as": "doppelt so alt wie",
        "twice as": "doppelt so",
        "three times as much as": "dreimal so viel wie",
        "three times as old as": "dreimal so alt wie",
        "half as much as": "halb so viel wie",
        "half as old as": "halb so alt wie",
        "more than": "mehr als",
        "less than": "weniger als",
        "older than": "älter als",
        "younger than": "jünger als",
        "together": "zusammen",
        "total": "zusammen",
        "sum": "zusammen",
        "how old is": "wie alt ist",
        "how much is": "wie viel ist",
        "what is": "wie viel ist",
    }
    text = f" {normalized} "
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = re.sub(rf"(?<![a-z]){re.escape(source)}(?![a-z])", target, text)
    text = re.sub(r"[?,;]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_relation(text: str) -> tuple[str, str, str, float] | None:
    factor_match = re.search(
        rf"\b(?P<left>{_NAME})\s+(?:ist|hat|besitzt|is|has)\s+"
        rf"(?P<factor>doppelt|dreimal|halb)\s+(?:so\s+)?(?:alt|viel|groß|gross|teuer|schwer)?\s*"
        rf"(?:wie|als|as)\s+(?P<right>{_NAME})\b",
        text,
    )
    if factor_match:
        factor = {"doppelt": 2.0, "dreimal": 3.0, "halb": -1.0}[factor_match.group("factor")]
        return _clean_name(factor_match.group("left")), _clean_name(factor_match.group("right")), "factor", factor

    delta_match = re.search(
        rf"\b(?P<left>{_NAME})\s+(?:ist|hat|besitzt|is|has)\s+"
        rf"(?P<amount>{_NUMBER})\s*(?:jahre?|euro|€|stücke?|stuecke?|punkte?)?\s+"
        rf"(?P<direction>mehr|weniger|älter|aelter|jünger|juenger|größer|groesser|kleiner)\s+"
        rf"(?:als|wie|than)\s+(?P<right>{_NAME})\b",
        text,
    )
    if delta_match:
        amount = float(delta_match.group("amount"))
        if delta_match.group("direction") in {"weniger", "jünger", "juenger", "kleiner"}:
            amount = -amount
        return _clean_name(delta_match.group("left")), _clean_name(delta_match.group("right")), "delta", amount

    return None


def _extract_total(text: str, left: str, right: str) -> float | None:
    total_patterns = [
        rf"\b(?:{re.escape(left)}|{re.escape(right)})\b.*\b(?:und|and)\b.*\b(?:{re.escape(left)}|{re.escape(right)})\b.*\bzusammen(?:\s+(?:sind|haben|hat|ist|are|have))?(?:\s+[a-zäöüß]+){{0,3}}\s+(?P<total>{_NUMBER})",
        rf"\bzusammen(?:\s+(?:sind|haben|hat|ist|are|have))?(?:\s+[a-zäöüß]+){{0,3}}\s+(?P<total>{_NUMBER})",
        rf"\b(?:gesamt|insgesamt)(?:\s+(?:sind|haben|hat|ist))?(?:\s+[a-zäöüß]+){{0,3}}\s+(?P<total>{_NUMBER})",
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group("total"))
    return None


def _extract_target(text: str, left: str, right: str) -> str | None:
    for name in (left, right):
        escaped = re.escape(name)
        if re.search(rf"\b(?:wie viel|wie alt|was)\s+(?:ist|hat|hatte|besitzt)?\s*{escaped}\b", text):
            return name
        if re.search(rf"\b{escaped}\s+(?:gesucht|finden|berechnen)\b", text):
            return name
    return None


def _target_expression(base_expression: str, target: str, left: str, kind: str, amount: float) -> str:
    if target != left:
        return base_expression
    if kind == "factor":
        if amount == -1:
            return f"({base_expression})/2"
        return f"({base_expression})*{format_number(amount)}"
    return f"({base_expression})+{format_number(amount)}"


def _clean_name(name: str) -> str:
    return name if name not in _FILLER_WORDS else ""
