from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import NaturalQueryResult


def solve_percent_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    patterns = [
        r"was sind (?P<pct>\d+(?:\.\d+)?)\s*%\s+von\s+(?P<base>\d+(?:\.\d+)?)",
        r"wie viel sind (?P<pct>\d+(?:\.\d+)?)\s*%\s+von\s+(?P<base>\d+(?:\.\d+)?)",
        r"wie viel ist (?P<pct>\d+(?:\.\d+)?)\s*%\s+von\s+(?P<base>\d+(?:\.\d+)?)",
        r"(?P<pct>\d+(?:\.\d+)?)\s*%\s+von\s+(?P<base>\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            pct = float(match.group("pct"))
            base = float(match.group("base"))
            expression = f"{format_number(base)}*{format_number(pct/100)}"
            answer = format_number(base * pct / 100)
            explanation = f"{format_number(pct)}% von {format_number(base)} bedeutet {format_number(base)} × {format_number(pct/100)}."
            return NaturalQueryResult(expression, answer, explanation)

    share_match = re.search(
        r"(?:wie gro[ßs] ist der anteil|welcher anteil sind)\s+(?P<part>\d+(?:\.\d+)?)\s+(?:von|an)\s+(?P<base>\d+(?:\.\d+)?)",
        normalized,
    )
    if share_match:
        part = float(share_match.group("part"))
        base = float(share_match.group("base"))
        if base != 0:
            expression = f"({format_number(part)}/{format_number(base)})*100"
            answer = format_number((part / base) * 100)
            explanation = "Der prozentuale Anteil ist Teil geteilt durch Ganzes mal 100."
            return NaturalQueryResult(expression, answer, explanation)

    delta_match = re.search(r"(?P<base>\d+(?:\.\d+)?)\s+(?P<op>plus|minus)\s+(?P<pct>\d+(?:\.\d+)?)\s*%", normalized)
    if delta_match:
        base = float(delta_match.group("base"))
        pct = float(delta_match.group("pct"))
        op = "+" if delta_match.group("op") == "plus" else "-"
        part = base * pct / 100
        expression = f"{format_number(base)}{op}{format_number(part)}"
        answer = format_number(base + part if op == "+" else base - part)
        explanation = f"Zuerst {format_number(pct)}% von {format_number(base)} = {format_number(part)}, dann {format_number(base)} {op} {format_number(part)}."
        return NaturalQueryResult(expression, answer, explanation)

    if len(values) >= 2:
        if any(term in normalized for term in ["rabatt", "nachlass", "skonto"]):
            base, rate = values[0], values[1]
            discount = base * rate / 100
            if any(term in normalized for term in ["endpreis", "neuer preis", "nach rabatt", "mit rabatt", "preis nach rabatt"]):
                expression = f"{format_number(base)}-{format_number(discount)}"
                explanation = "Der Endpreis ist Grundpreis minus Rabattbetrag."
                return NaturalQueryResult(*format_local_result(expression, base - discount, explanation))
        if any(term in normalized for term in ["mehrwertsteuer", "mwst", "umsatzsteuer"]) and values:
            net = values[0]
            rate = values[1] if len(values) > 1 else 19
            if any(term in normalized for term in ["brutto", "inklusive", "mit mwst", "mit mehrwertsteuer"]):
                expression = f"{format_number(net)}*(1+{format_number(rate/100)})"
                explanation = f"Brutto ist Netto plus {format_number(rate)}% Mehrwertsteuer."
                return NaturalQueryResult(*format_local_result(expression, net * (1 + rate / 100), explanation))
        if any(term in normalized for term in ["prozentänderung", "prozentaenderung", "prozentuale änderung", "prozentuale aenderung"]) and values[0] != 0:
            old, new = values[0], values[1]
            expression = f"(({format_number(new)}-{format_number(old)})/{format_number(old)})*100"
            explanation = "Die prozentuale Änderung ist (neu - alt) / alt × 100."
            return NaturalQueryResult(*format_local_result(expression, ((new - old) / old) * 100, explanation))

    return None


def solve_percent_change_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if not (
        any(term in normalized for term in ["prozentänderung", "prozentaenderung", "prozentuale änderung", "prozentuale aenderung", "änderung", "aenderung"])
        or ("von" in normalized and "auf" in normalized and "%" not in normalized and len(values) >= 2)
    ):
        return None
    if len(values) < 2 or values[0] == 0:
        return None
    old, new = values[0], values[1]
    value = ((new - old) / old) * 100
    expression = f"(({format_number(new)}-{format_number(old)})/{format_number(old)})*100"
    explanation = "Die prozentuale Änderung ist (neu - alt) / alt × 100."
    return NaturalQueryResult(*format_local_result(expression, value, explanation))
