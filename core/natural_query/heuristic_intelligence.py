# SPDX-License-Identifier: GPL-3.0-or-later
"""Broad local heuristics for natural calculator queries.

This module intentionally stays deterministic and offline.  It does not try to
be a chat model.  Its job is to make the local assistant smarter by:

* normalizing messy German/English user input before domain solvers see it,
* detecting likely domains with explicit confidence scores,
* solving common high-confidence everyday calculation phrasings, and
* returning clarification requests instead of guessing when the query is vague.

Keep this layer conservative: a heuristic may answer only when the pattern is
clear.  Otherwise it should leave the query to the existing specialist solvers.
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import CLARIFICATION_EXPRESSION, NaturalQueryResult


@dataclass(frozen=True)
class HeuristicCandidate:
    domain: str
    confidence: float
    reasons: tuple[str, ...]


# Deliberately small, high-value typo map.  Do not turn this into a broad spell
# checker; changing arbitrary words would make the calculator unpredictable.
_TOKEN_FIXES: dict[str, str] = {
    # German question/connector words
    "wieviel": "wie viel",
    "wivil": "wie viel",
    "wifil": "wie viel",
    "wievil": "wie viel",
    "wiefiel": "wie viel",
    "wiefil": "wie viel",
    "wass": "was",
    "sint": "sind",
    "fon": "von",
    "vohn": "von",
    "fonn": "von",
    "fuer": "für",
    "fur": "für",
    "druch": "durch",
    "duch": "durch",
    "mahll": "mal",
    "mall": "mal",
    # Domain words
    "przent": "%",
    "prozentt": "%",
    "proznet": "%",
    "mwst": "mehrwertsteuer",
    "mws": "mehrwertsteuer",
    "mehrwehrtsteuer": "mehrwertsteuer",
    "mehrwertsteur": "mehrwertsteuer",
    "rabbat": "rabatt",
    "zinseszinss": "zinseszins",
    "statistik": "statistik",
    "durchnitt": "durchschnitt",
    "durchsnitt": "durchschnitt",
    "mittelwertt": "mittelwert",
    "umrechnnen": "umrechnen",
    "umrechnen": "umrechnen",
    "kilomter": "kilometer",
    "zentimter": "zentimeter",
    "millimter": "millimeter",
    "quatrat": "quadrat",
    "quadratwurtzel": "quadratwurzel",
    "wurtzel": "wurzel",
    "pythagoras": "pythagoras",
    "hypothenuse": "hypotenuse",
    "hypothenüse": "hypotenuse",
    "hypothenuse": "hypotenuse",
    "kathete": "kathete",
    # English common typos
    "percente": "%",
    "precent": "%",
    "persent": "%",
    "whats": "what is",
    "wats": "what is",
    "calcualte": "calculate",
    "devide": "divide",
    "multipliedd": "multiplied",
}

_FUZZY_DOMAIN_TERMS = {
    "prozent",
    "percent",
    "rabatt",
    "mehrwertsteuer",
    "zins",
    "zinsen",
    "zinseszins",
    "brutto",
    "netto",
    "durchschnitt",
    "mittelwert",
    "median",
    "varianz",
    "standardabweichung",
    "umrechnen",
    "meter",
    "meters",
    "kilometer",
    "kilometers",
    "zentimeter",
    "millimeter",
    "kilogramm",
    "gramm",
    "liter",
    "watt",
    "kilowatt",
    "pythagoras",
    "hypotenuse",
    "kathete",
    "radius",
    "durchmesser",
    "umfang",
    "fläche",
    "volumen",
    "dichte",
    "kraft",
    "leistung",
    "geschwindigkeit",
    "beschleunigung",
}

_SYMBOL_REPLACEMENTS = {
    "×": " mal ",
    "✕": " mal ",
    "÷": " geteilt durch ",
    ":": " geteilt durch ",
    "−": "-",
    "–": "-",
    "—": "-",
    "€": " euro ",
}

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "percent": ("%", "prozent", "percent", "rabatt", "nachlass", "skonto", "mehrwertsteuer", "mwst", "vat"),
    "finance": ("zins", "zinsen", "zinseszins", "kredit", "rate", "rendite", "marge", "gewinn", "verlust", "brutto", "netto", "euro"),
    "unit": (" in ", " zu ", " nach ", "umrechnen", "convert", "meter", "kilometer", "cm", "mm", "kg", "gramm", "liter", "watt", "kw", "ps"),
    "geometry": ("radius", "durchmesser", "umfang", "fläche", "flaeche", "volumen", "kreis", "rechteck", "dreieck", "zylinder", "kugel", "pythagoras", "hypotenuse"),
    "statistics": ("durchschnitt", "mittelwert", "median", "varianz", "standardabweichung", "summe", "minimum", "maximum"),
    "motion": ("wie lange", "wie weit", "wie schnell", "kmh", "km/h", "geschwindigkeit", "strecke", "zeit"),
    "physics": ("dichte", "kraft", "arbeit", "leistung", "spannung", "strom", "beschleunigung", "masse"),
    "algebra": ("gleichung", "löse", "solve", "x=", " x ", "variable"),
    "arithmetic": ("plus", "minus", "mal", "geteilt", "+", "-", "*", "/", "^", "wurzel"),
}

_PERCENT_WORDS = ("prozent", "percent", "prozente", "proz", "pct")
_CURRENCY_WORDS = ("euro", "eur", "€", "dollar", "usd")
_PERSON_WORDS = ("person", "personen", "leute", "people", "personnes")


_NUMBER = r"-?\d+(?:\.\d+)?"


def improve_query_heuristically(normalized: str) -> str:
    """Return a safer, richer normalized query for specialist solvers.

    The input should already be lowercased.  This function is idempotent and
    intentionally conservative.
    """
    text = normalized.lower().strip()
    for source, target in _SYMBOL_REPLACEMENTS.items():
        text = text.replace(source, target)

    # Spoken decimal phrases commonly seen in typed German questions.
    text = re.sub(rf"(?P<a>\d+)\s+komma\s+(?P<b>\d+)", r"\g<a>.\g<b>", text)
    text = re.sub(rf"(?P<a>\d+)\s+punkt\s+(?P<b>\d+)", r"\g<a>.\g<b>", text)

    # Percent written without symbol.
    for word in _PERCENT_WORDS:
        text = re.sub(rf"(?P<n>{_NUMBER})\s*{re.escape(word)}\b", r"\g<n>%", text)

    # Common compact unit spellings.
    text = re.sub(r"\bkm\s*/\s*h\b", "km/h", text)
    text = re.sub(r"\bkm\s+h\b", "km/h", text)
    text = re.sub(r"\bkilometer\s+pro\s+stunde\b", "km/h", text)

    tokens = text.split()
    fixed_tokens: list[str] = []
    for token in tokens:
        clean = token.strip(".,;!?()[]{}")
        replacement = _TOKEN_FIXES.get(clean)
        if replacement is None:
            replacement = _fuzzy_domain_fix(clean)
        if replacement is None:
            fixed_tokens.append(token)
        else:
            fixed_tokens.append(token.replace(clean, replacement))
    text = " ".join(fixed_tokens)

    # Normalize frequent intent phrases into a shape that the explicit solvers
    # can parse more reliably.
    replacements = {
        "was ist der endpreis": "endpreis",
        "was ist der neue preis": "endpreis",
        "preis nach rabatt": "endpreis nach rabatt",
        "inkl mwst": "inklusive mehrwertsteuer",
        "inkl. mwst": "inklusive mehrwertsteuer",
        "zzgl mwst": "plus mehrwertsteuer",
        "aufteilen": "teilen",
        "geteilt auf": "teilen auf",
        "pro kopf": "pro person",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def score_query_domains(normalized: str) -> list[HeuristicCandidate]:
    """Score likely domains without executing any calculation."""
    text = f" {normalized} "
    values = re.findall(_NUMBER, normalized)
    scored: list[HeuristicCandidate] = []
    for domain, terms in _DOMAIN_KEYWORDS.items():
        reasons: list[str] = []
        score = 0.0
        for term in terms:
            if term in text:
                score += 0.18 if len(term.strip()) > 1 else 0.08
                reasons.append(term.strip())
        if values:
            score += min(0.18, 0.04 * len(values))
        if domain == "percent" and "%" in normalized:
            score += 0.28
        if domain == "unit" and re.search(rf"\b{_NUMBER}\s*[a-zäöüß/]+\s+(?:in|to|zu|nach|auf)\s+[a-zäöüß/]+", normalized):
            score += 0.35
            reasons.append("value-unit-target pattern")
        if domain == "algebra" and re.search(r"\bx\b.*=|=.*\bx\b", normalized):
            score += 0.40
            reasons.append("equation pattern")
        if domain == "arithmetic" and re.search(r"\d\s*[+\-*/^]\s*\d", normalized):
            score += 0.50
            reasons.append("symbol expression")
        if score > 0:
            scored.append(HeuristicCandidate(domain, min(score, 0.99), tuple(dict.fromkeys(reasons))))
    return sorted(scored, key=lambda item: item.confidence, reverse=True)


def solve_broad_heuristic_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    """Solve only clear high-confidence everyday cases.

    Return None when a specialist module should handle the query.
    """
    clarification = _build_high_value_clarification(normalized, values)
    if clarification is not None:
        return clarification

    for solver in (
        _solve_net_from_gross,
        _solve_vat_with_reordered_numbers,
        _solve_adjust_by_percent,
        _solve_split_amount,
        _solve_price_per_unit,
        _solve_ratio_share,
    ):
        result = solver(normalized, values)
        if result is not None:
            return result
    return None


def _fuzzy_domain_fix(token: str) -> str | None:
    if len(token) < 5 or token.isdigit():
        return None
    if any(ch.isdigit() for ch in token):
        return None
    match = get_close_matches(token, _FUZZY_DOMAIN_TERMS, n=1, cutoff=0.86)
    return match[0] if match else None


def _build_high_value_clarification(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    # Interest queries with principal/rate/time are dangerous when the user does
    # not say whether they want interest amount, final amount, simple interest or
    # compound interest.
    has_money = any(word in normalized for word in _CURRENCY_WORDS)
    has_rate = "%" in normalized or " zins" in normalized or "zinsen" in normalized
    has_time = any(word in normalized for word in ("jahr", "jahre", "monat", "monate", "tag", "tage"))
    has_interest_intent = any(word in normalized for word in ("zins", "zinsen", "zinseszins", "rendite"))
    has_clear_interest_choice = any(
        phrase in normalized
        for phrase in (
            "zinsbetrag",
            "nur zinsen",
            "wie viel zinsen",
            "wieviel zinsen",
            "endbetrag",
            "am ende",
            "zinseszins",
            "einfache zinsen",
            "simple interest",
            "compound interest",
        )
    )
    if has_money and has_rate and has_time and has_interest_intent and len(values) >= 3 and not has_clear_interest_choice:
        answer = "Meinst du den Zinsbetrag, den Endbetrag oder Zinseszins?"
        explanation = "Bei Geldbetrag, Zinssatz und Laufzeit sind mehrere Rechnungen möglich: Zinsbetrag, Endbetrag oder Zinseszins. Ich rechne erst, wenn die Zielgröße eindeutig ist."
        return NaturalQueryResult(CLARIFICATION_EXPRESSION, answer, explanation)

    # Motion without units is mathematically under-specified.
    if any(phrase in normalized for phrase in ("wie lange", "how long", "fahrzeit")) and len(values) >= 2:
        has_distance_unit = any(unit in normalized for unit in (" km", " meter", " m ", "kilometer"))
        has_speed_unit = any(unit in normalized for unit in ("km/h", "kmh", "m/s"))
        if not (has_distance_unit and has_speed_unit):
            answer = "Für die Fahrzeit brauche ich Strecke und Geschwindigkeit mit Einheiten."
            explanation = "Beispiel: '600 km mit 50 km/h'. Ohne Einheiten könnte 600 und 50 zu vielen Aufgaben gehören."
            return NaturalQueryResult(CLARIFICATION_EXPRESSION, answer, explanation)

    return None


def _solve_vat_with_reordered_numbers(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if not any(term in normalized for term in ("mehrwertsteuer", "mwst", "vat")):
        return None
    if not any(term in normalized for term in ("netto", "brutto", "plus mehrwertsteuer", "zzgl", "inklusive", "inkl")):
        return None
    if any(term in normalized for term in ("netto aus brutto", "netto von brutto", "netto berechnen", "net price")):
        return None
    if "brutto" in normalized and "netto" in normalized and any(term in normalized for term in ("inklusive", "inkl", "including")):
        return None

    # Handles: "19% mwst auf 100 netto" and "100 netto plus 19% mwst".
    pct_first = re.search(rf"(?P<rate>{_NUMBER})\s*%.*?(?P<net>{_NUMBER})\s*(?:netto|euro|eur)?", normalized)
    net_first = re.search(rf"(?P<net>{_NUMBER})\s*(?:netto|euro|eur)? .*?(?P<rate>{_NUMBER})\s*%", normalized)
    match = pct_first or net_first
    if not match:
        return None
    net = float(match.group("net"))
    rate = float(match.group("rate"))
    if not (0 <= rate <= 100):
        return None
    expression = f"{format_number(net)}*(1+{format_number(rate / 100)})"
    explanation = f"Brutto ist Netto plus {format_number(rate)}% Mehrwertsteuer."
    return NaturalQueryResult(*format_local_result(expression, net * (1 + rate / 100), explanation))


def _solve_net_from_gross(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if not any(term in normalized for term in ("mehrwertsteuer", "mwst", "vat", "brutto")):
        return None
    wants_net = any(term in normalized for term in ("netto aus brutto", "netto von brutto", "netto berechnen", "net price", "netto"))
    has_gross = any(term in normalized for term in ("brutto", "inklusive", "inkl", "including"))
    if not (wants_net and has_gross):
        return None
    match = re.search(rf"(?P<gross>{_NUMBER})\s*(?:brutto|euro|eur)?.*?(?P<rate>{_NUMBER})\s*%", normalized)
    if not match:
        match = re.search(rf"(?P<rate>{_NUMBER})\s*%.*?(?P<gross>{_NUMBER})\s*(?:brutto|euro|eur)?", normalized)
    if not match:
        return None
    gross = float(match.group("gross"))
    rate = float(match.group("rate"))
    if rate <= -100:
        return None
    expression = f"{format_number(gross)}/(1+{format_number(rate / 100)})"
    explanation = f"Netto ist Brutto geteilt durch 1 plus {format_number(rate)}% Mehrwertsteuer."
    return NaturalQueryResult(*format_local_result(expression, gross / (1 + rate / 100), explanation))


def _solve_adjust_by_percent(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if "%" not in normalized:
        return None
    if any(term in normalized for term in ("mehrwertsteuer", "mwst", "vat")):
        return None
    increase = any(term in normalized for term in ("erhöhe", "erhoehe", "erhöhen", "increase", "plus", "aufschlag", "mehr"))
    decrease = any(term in normalized for term in ("reduziere", "senke", "verringere", "decrease", "minus", "rabatt", "weniger", "nachlass"))
    if increase == decrease:
        return None
    match = re.search(rf"(?P<rate>{_NUMBER})\s*%.*?(?:von|auf|bei)\s*(?P<base>{_NUMBER})", normalized)
    if not match:
        match = re.search(rf"(?P<base>{_NUMBER})(?!\s*%).*?(?P<rate>{_NUMBER})\s*%", normalized)
    if not match:
        return None
    base = float(match.group("base"))
    rate = float(match.group("rate"))
    delta = base * rate / 100
    if decrease:
        expression = f"{format_number(base)}-{format_number(delta)}"
        explanation = f"{format_number(rate)}% von {format_number(base)} sind {format_number(delta)}; dieser Betrag wird abgezogen."
        return NaturalQueryResult(*format_local_result(expression, base - delta, explanation))
    expression = f"{format_number(base)}+{format_number(delta)}"
    explanation = f"{format_number(rate)}% von {format_number(base)} sind {format_number(delta)}; dieser Betrag wird addiert."
    return NaturalQueryResult(*format_local_result(expression, base + delta, explanation))


def _solve_split_amount(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if len(values) < 2:
        return None
    if not any(term in normalized for term in ("teilen", "aufteilen", "split", "pro person", "jeder", "each")):
        return None
    if not any(word in normalized for word in _PERSON_WORDS):
        return None
    amount, people = values[0], values[1]
    if people == 0:
        return None
    expression = f"{format_number(amount)}/{format_number(people)}"
    explanation = "Der Gesamtbetrag wird gleichmäßig auf die Personen verteilt."
    return NaturalQueryResult(*format_local_result(expression, amount / people, explanation))


def _solve_price_per_unit(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if len(values) < 2:
        return None
    if not any(term in normalized for term in ("pro stück", "pro stk", "stückpreis", "price per", "per piece", "ein stück", "1 stück")):
        return None
    if not any(term in normalized for term in ("kosten", "kostet", "preis", "euro", "eur")):
        return None

    # Prefer explicit "12 stück kosten 30 euro" order.  Fallback to first two
    # numbers when the wording is already classified as price-per-unit.
    match = re.search(rf"(?P<count>{_NUMBER})\s*(?:stück|stk|pieces?).*?(?:kosten|kostet|price|preis).*?(?P<total>{_NUMBER})", normalized)
    if match:
        count = float(match.group("count"))
        total = float(match.group("total"))
    else:
        count, total = values[0], values[1]
    if count == 0:
        return None
    expression = f"{format_number(total)}/{format_number(count)}"
    explanation = "Der Stückpreis ist Gesamtpreis geteilt durch Anzahl."
    return NaturalQueryResult(*format_local_result(expression, total / count, explanation))


def _solve_ratio_share(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    if len(values) < 3:
        return None
    if not any(term in normalized for term in ("verhältnis", "verhaeltnis", "ratio", "aufteilen")):
        return None
    match = re.search(rf"(?P<a>{_NUMBER})\s*(?:zu|:|/)\s*(?P<b>{_NUMBER}).*?(?P<total>{_NUMBER})", normalized)
    if not match:
        return None
    a = float(match.group("a"))
    b = float(match.group("b"))
    total = float(match.group("total"))
    denom = a + b
    if denom == 0:
        return None
    first = total * a / denom
    second = total * b / denom
    answer = f"{format_number(first)} und {format_number(second)}"
    expression = f"{format_number(total)}*{format_number(a)}/({format_number(a)}+{format_number(b)})"
    explanation = "Bei einer Verhältnisaufteilung wird der Gesamtwert proportional auf die Anteile verteilt."
    return NaturalQueryResult(expression, answer, explanation)
