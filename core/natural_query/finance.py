from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import CLARIFICATION_EXPRESSION, NaturalQueryResult


def _looks_like_year_only_tax_query(normalized: str, values: list[float]) -> bool:
    if len(values) != 1:
        return False
    value = values[0]
    if value < 1900 or value > 2100 or value != int(value):
        return False
    amount_context_terms = ["€", "euro", "netto", "brutto", "preis", "betrag", "kosten", "auf", "von", "bei"]
    return not any(term in normalized for term in amount_context_terms)


def parse_interest_query(normalized: str) -> tuple[float, float, float] | None:
    capital_match = re.search(r"(?P<capital>\d+(?:\.\d+)?)\s*(?:€|euro)", normalized)
    rate_match = re.search(
        r"(?P<rate>\d+(?:\.\d+)?)\s*%\s*(?:p\.?\s*a\.?|pro\s+jahr|jährlich|jaehrlich|jahreszins|zins|zinsen)?",
        normalized,
    )
    duration_match = re.search(
        r"(?:für|fuer|in|über|ueber|laufzeit)?\s*(?P<duration>\d+(?:\.\d+)?)\s*(?P<unit>monaten|monate|monat|jahren|jahre|jahr)\b",
        normalized,
    )
    if not capital_match or not rate_match or not duration_match:
        return None
    duration = float(duration_match.group("duration"))
    unit = duration_match.group("unit")
    years = duration / 12 if unit in {"monat", "monate", "monaten"} else duration
    return float(capital_match.group("capital")), float(rate_match.group("rate")), years


def interest_clarification_result(capital: float, rate: float, years: float) -> NaturalQueryResult:
    question = (
        "Meinst du den Zinsbetrag, den Endbetrag mit einfachen Zinsen oder Zinseszins?"
    )
    options = (
        f"Bitte antworte z. B. mit: 'Zinsbetrag', 'Endbetrag' oder 'Zinseszins'. "
        f"Ausgangswerte: {format_number(capital)} Euro, {format_number(rate)}% pro Jahr, {format_number(years)} Jahre."
    )
    return NaturalQueryResult(CLARIFICATION_EXPRESSION, question, options)


def _solve_interest_values(capital: float, rate: float, years: float, mode: str) -> NaturalQueryResult:
    if mode == "compound_total":
        value = capital * ((1 + rate / 100) ** years)
        expression = f"{format_number(capital)}*(1+{format_number(rate/100)})^{format_number(years)}"
        explanation = "Beim Zinseszins wird der Zinssatz in jedem Jahr auf den neuen Gesamtbetrag angewendet."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))
    interest = capital * rate / 100 * years
    if mode == "simple_total":
        value = capital + interest
        expression = f"{format_number(capital)}+({format_number(capital)}*{format_number(rate/100)}*{format_number(years)})"
        explanation = "Endbetrag bei einfacher Verzinsung ist Kapital plus Zinsen."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))
    expression = f"{format_number(capital)}*{format_number(rate/100)}*{format_number(years)}"
    total = capital + interest
    explanation = f"Einfache Zinsen sind Kapital × Zinssatz × Zeit. Der Gesamtbetrag wäre {format_number(total)}."
    return NaturalQueryResult(*format_local_result(expression, interest, explanation))


def solve_interest_choice(capital: float, rate: float, years: float, choice: str) -> NaturalQueryResult | None:
    normalized_choice = choice.lower().strip()
    if any(term in normalized_choice for term in ["zinseszins", "compound"]):
        return _solve_interest_values(capital, rate, years, "compound_total")
    if any(term in normalized_choice for term in ["endbetrag", "gesamt", "insgesamt", "kontostand", "am ende", "total"]):
        return _solve_interest_values(capital, rate, years, "simple_total")
    if any(term in normalized_choice for term in ["zinsbetrag", "nur zinsen", "zinsen", "zahlen", "interest"]):
        return _solve_interest_values(capital, rate, years, "simple_interest")
    return None


def solve_school_finance_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if (
        any(term in normalized for term in ["artikel", "jacke", "produkt", "preis"])
        and any(term in normalized for term in ["rabatt", "nachlass"])
        and any(term in normalized for term in ["wie viel kostet", "wie teuer ist", "was kostet", "preis nach", "preis mit rabatt"])
        and len(values) >= 2
    ):
        base = values[0]
        pct = values[1]
        discount = base * pct / 100
        expression = f"{format_number(base)}-{format_number(discount)}"
        explanation = "Erst wird der Rabattbetrag berechnet, danach vom Grundpreis abgezogen."
        return NaturalQueryResult(*format_local_result(expression, base - discount, explanation))

    if (
        any(term in normalized for term in ["legt", "investiert", "spart"])
        and "zins" not in normalized
        and any(term in normalized for term in ["wie viel", "wie hoch", "welcher betrag", "betrag am ende"])
        and len(values) >= 3
    ):
        capital = values[0]
        rate = values[1]
        years = values[2]
        interest = capital * rate / 100 * years
        value = capital + interest
        expression = f"{format_number(capital)}+({format_number(capital)}*{format_number(rate/100)}*{format_number(years)})"
        explanation = "Erst werden die Zinsen berechnet, dann zum Startkapital addiert."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    return None


def solve_interest_query(normalized: str) -> NaturalQueryResult | None:
    parsed = parse_interest_query(normalized)
    if not parsed:
        return None
    capital, rate, years = parsed
    if any(term in normalized for term in ["zinseszins", "zinseszinsen"]):
        return _solve_interest_values(capital, rate, years, "compound_total")
    if any(term in normalized for term in ["gesamt", "insgesamt", "am ende", "endbetrag", "kontostand"]):
        return _solve_interest_values(capital, rate, years, "simple_total")
    if any(
        term in normalized
        for term in [
            "zinsbetrag",
            "nur zinsen",
            "nur die zinsen",
            "wie viel zinsen",
            "zinsen bekomme",
            "zinsen erhalte",
            "zinsen muss ich zahlen",
            "muss ich zahlen",
            "zinsen zahlen",
        ]
    ):
        return _solve_interest_values(capital, rate, years, "simple_interest")
    return interest_clarification_result(capital, rate, years)


def solve_finance_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    parsed_interest = parse_interest_query(normalized)
    if parsed_interest is not None:
        return solve_interest_query(normalized)

    if any(term in normalized for term in ["zinseszins", "zinseszinsen"]) and len(values) >= 3:
        capital, rate, years = values[0], values[1], values[2]
        value = capital * ((1 + rate / 100) ** years)
        expression = f"{format_number(capital)}*(1+{format_number(rate/100)})^{format_number(years)}"
        explanation = "Beim Zinseszins wird der Zinssatz in jedem Jahr auf den neuen Gesamtbetrag angewendet."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["endbetrag", "gesamtbetrag", "kontostand"]) and "zins" in normalized and len(values) >= 3:
        capital, rate, years = values[0], values[1], values[2]
        interest = capital * rate / 100 * years
        value = capital + interest
        expression = f"{format_number(capital)}+({format_number(capital)}*{format_number(rate/100)}*{format_number(years)})"
        explanation = "Endbetrag bei einfacher Verzinsung ist Kapital plus Zinsen."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if "zins" in normalized and len(values) >= 3:
        if any(term in normalized for term in ["jahreszins", "monat", "monate", "laufzeit"]):
            return NaturalQueryResult(
                CLARIFICATION_EXPRESSION,
                "Ich erkenne eine Zinsaufgabe, aber Kapital, Zinssatz oder Laufzeit sind nicht eindeutig.",
                "Bitte formuliere z. B.: 'Wie viel Zinsen bei 1000 Euro, 11% Jahreszins und 24 Monaten?'",
            )
        if not any(term in normalized for term in ["zinsbetrag", "nur zinsen", "nur die zinsen", "wie viel zinsen", "zinsen bekomme", "zinsen erhalte"]):
            return interest_clarification_result(values[0], values[1], values[2])
        capital, rate, years = values[0], values[1], values[2]
        value = capital * rate / 100 * years
        expression = f"{format_number(capital)}*{format_number(rate/100)}*{format_number(years)}"
        explanation = "Einfache Zinsen sind Kapital × Zinssatz × Zeit."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["mehrwertsteuer", "mwst", "umsatzsteuer"]):
        if not values:
            return None
        if _looks_like_year_only_tax_query(normalized, values):
            return NaturalQueryResult(
                CLARIFICATION_EXPRESSION,
                "Ich erkenne eine Finanzaufgabe, aber nicht eindeutig genug.",
                "Bitte nenne einen Nettobetrag, z. B. 'Mehrwertsteuer auf 100 Euro', oder formuliere die Steuerfrage genauer.",
            )
        net = values[0]
        rate = values[1] if len(values) > 1 else 19
        if any(term in normalized for term in ["brutto", "inklusive", "mit mwst", "mit mehrwertsteuer"]):
            value = net * (1 + rate / 100)
            expression = f"{format_number(net)}*(1+{format_number(rate/100)})"
            explanation = f"Brutto ist Netto plus {format_number(rate)}% Mehrwertsteuer."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))
        if any(term in normalized for term in ["steuer", "mwst betrag", "mehrwertsteuer betrag"]):
            value = net * rate / 100
            expression = f"{format_number(net)}*{format_number(rate/100)}"
            explanation = f"Die Mehrwertsteuer ist Netto × {format_number(rate/100)}."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["gewinn", "profit", "verdienst"]) and len(values) >= 2:
        cost = values[0]
        revenue = values[1]
        value = revenue - cost
        expression = f"{format_number(revenue)}-{format_number(cost)}"
        explanation = "Der Gewinn ist Verkaufspreis minus Kosten."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["marge", "gewinnmarge", "gewinnspanne"]) and len(values) >= 2 and values[1] != 0:
        cost = values[0]
        revenue = values[1]
        value = ((revenue - cost) / revenue) * 100
        expression = f"(({format_number(revenue)}-{format_number(cost)})/{format_number(revenue)})*100"
        explanation = "Die Marge ist Gewinn geteilt durch Verkaufspreis mal 100."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["rabatt", "nachlass", "skonto"]) and len(values) >= 2:
        # Heuristic to find which one is the rate
        rate = None
        base = None
        
        # 1. Check for % sign
        pct_match = re.search(r"(?P<val>\d+(?:\.\d+)?)\s*%", normalized)
        if pct_match:
            rate = float(pct_match.group("val"))
            # base is the other value
            for v in values:
                if v != rate:
                    base = v
                    break
            if base is None: base = rate # edge case
        else:
            # 2. Heuristic: larger is base if not sure
            base, rate = (values[0], values[1]) if values[0] > values[1] else (values[1], values[0])

        discount = base * rate / 100
        if any(term in normalized for term in ["endpreis", "neuer preis", "nach rabatt", "mit rabatt", "preis nach rabatt", "finaler preis", "final preis"]):
            value = base - discount
            expression = f"{format_number(base)}-{format_number(discount)}"
            explanation = "Der Endpreis ist Grundpreis minus Rabattbetrag."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))
        
        expression = f"{format_number(base)}*{format_number(rate/100)}"
        explanation = "Der Rabattbetrag ist Grundpreis × Rabattsatz."
        return NaturalQueryResult(*format_local_result(expression, discount, explanation))

    return None
