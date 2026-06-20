from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result, unit_factor
from core.natural_query.types import NaturalQueryResult


def solve_recurring_amount_query(normalized: str) -> NaturalQueryResult | None:
    recurring_balance_patterns = [
        r"(?P<start>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:konto|habe).*(?:jeden|pro)\s+(?P<unit>tag|tage|woche|wochen|monat|monate)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro).*(?P<verb>ausgebe|ausgibt|verdiene|verdient|bekomme|erhalte|spare).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?:tag|tagen|tage|woche|wochen|monat|monate)",
        r"(?P<start>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:konto|habe).*(?P<verb>ausgebe|ausgibt|verdiene|verdient|bekomme|erhalte|spare)\s+(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:jeden|pro)\s+(?P<unit>tag|tage|woche|wochen|monat|monate).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?:tag|tagen|tage|woche|wochen|monat|monate)",
        r"(?P<start>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:konto|habe).*(?P<verb>ausgebe|ausgibt|verdiene|verdient|bekomme|erhalte|spare).*(?:jeden|pro)\s+(?P<unit>tag|tage|woche|wochen|monat|monate).*(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?:tag|tagen|tage|woche|wochen|monat|monate)",
    ]
    for balance_pattern in recurring_balance_patterns:
        balance_change_match = re.search(balance_pattern, normalized)
        if not balance_change_match:
            continue
        start = float(balance_change_match.group("start"))
        amount = float(balance_change_match.group("amount"))
        count = float(balance_change_match.group("count"))
        verb = balance_change_match.group("verb")
        delta = amount * count
        if verb in {"ausgebe", "ausgibt"}:
            value = start - delta
            expression = f"{format_number(start)}-({format_number(amount)}*{format_number(count)})"
            explanation = "Vom Startbetrag wird die wiederkehrende Ausgabe mal Anzahl der Zeiträume abgezogen."
        else:
            value = start + delta
            expression = f"{format_number(start)}+({format_number(amount)}*{format_number(count)})"
            explanation = "Zum Startbetrag wird die wiederkehrende Einnahme mal Anzahl der Zeiträume addiert."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    recurring_amount_patterns = [
        r"(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro)?\s*(?:pro|je|jeden|jede|jedes)\s+(?P<unit>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?P<target>tag|tage|woche|wochen|monat|monate|jahr|jahre)",
        r"(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro)?\s*in\s+(?:einer|einem|1)\s+(?P<unit>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?:verdiene|verdient|bekomme|erhalte|mache|habe).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?P<target>tag|tage|woche|wochen|monat|monate|jahr|jahre)",
        r"(?P<amount>\d+(?:\.\d+)?)\s*(?:€|euro)?\s*(?:[a-zäöüß]+(?:\s+[a-zäöüß]+)*)?\s*pro\s+(?P<unit>woche|wochen|tag|tage|monat|monate|jahr|jahre).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?P<target>woche|wochen|tag|tage|monat|monate|jahr|jahre)",
        r"(?:jeden|jede|jedes)\s+(?P<unit>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?P<amount>\d+(?:\.\d+)?)\s+(?:[a-zäöüß]+(?:\s+[a-zäöüß]+)*)?.*(?:esse|isst|brauche|braucht|verbrauche|verbraucht|habe|mache).*(?:in|für)\s+(?P<count>\d+(?:\.\d+)?)\s+(?P<target>tag|tage|woche|wochen|monat|monate|jahr|jahre)",
        r"(?:wie viele|wieviele|how many).*(?:in|für)\s+(?:(?P<count>\d+(?:\.\d+)?)\s+)?(?:der|die|dem|den|a|an|einer|einem|one)?\s*(?P<target>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?:jeden|jede|jedes)\s+(?P<unit>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?P<amount>\d+(?:\.\d+)?)",
        r"(?:wie viele|wieviele|how many).*(?:in|für)\s+(?:(?P<count>\d+(?:\.\d+)?)\s+)?(?:der|die|dem|den|a|an|einer|einem|one)?\s*(?P<target>tag|tage|woche|wochen|monat|monate|jahr|jahre).*(?P<amount>\d+(?:\.\d+)?)\s+(?:[a-zäöüß]+(?:\s+[a-zäöüß]+)*)?.*(?:jeden|jede|jedes)\s+(?P<unit>tag|tage|woche|wochen|monat|monate|jahr|jahre)",
    ]
    for recurring_pattern in recurring_amount_patterns:
        recurring_amount_match = re.search(recurring_pattern, normalized)
        if not recurring_amount_match:
            continue
        amount = float(recurring_amount_match.group("amount"))
        count_text = recurring_amount_match.groupdict().get("count")
        count = float(count_text) if count_text else 1.0
        source_unit = recurring_amount_match.group("unit")
        target_unit = recurring_amount_match.group("target")
        source_factor = unit_factor(source_unit)
        target_factor = unit_factor(target_unit)
        if not source_factor or not target_factor:
            continue
        periods = (count * target_factor) / source_factor
        value = amount * periods
        expression = f"{format_number(amount)}*(({format_number(count)}*{format_number(target_factor)})/{format_number(source_factor)})"
        explanation = "Eine feste Menge pro Zeitraum wird auf den Zielzeitraum umgerechnet und dann mit der Anzahl der Zielzeiträume multipliziert."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    spending_match = re.search(
        r"(?P<start>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:jeden|pro)\s+tag\s+(?P<daily>\d+(?:\.\d+)?)\s*(?:€|euro).*(?:in|für)\s+(?P<days>\d+(?:\.\d+)?)\s+tagen?",
        normalized,
    )
    if spending_match:
        start = float(spending_match.group("start"))
        daily = float(spending_match.group("daily"))
        days = float(spending_match.group("days"))
        value = start - (daily * days)
        expression = f"{format_number(start)}-({format_number(daily)}*{format_number(days)})"
        explanation = "Vom Startbetrag wird die tägliche Ausgabe mal Anzahl der Tage abgezogen."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    return None


def solve_rule_of_three_query(normalized: str, values: list[float], *, school_style: bool = False) -> NaturalQueryResult | None:
    if school_style:
        if not (
            any(term in normalized for term in ["was kosten", "wie viel kosten", "wie teuer sind", "stück kosten"])
            and len(values) >= 3
        ):
            return None
        explanation = "Beim Dreisatz wird erst der Preis pro Einheit berechnet und dann mit der Zielmenge multipliziert."
    else:
        if not any(term in normalized for term in ["dreisatz", "wie viel kosten", "wieviel kosten", "was kosten", "entsprechen"]):
            return None
        if len(values) < 3:
            return None
        explanation = "Beim Dreisatz teilst du erst durch den bekannten Grundwert und multiplizierst dann mit dem Zielwert."

    a, b, c = values[0], values[1], values[2]
    if a == 0:
        return None
    value = b * c / a
    expression = f"({format_number(b)}*{format_number(c)})/{format_number(a)}"
    return NaturalQueryResult(*format_local_result(expression, value, explanation))
