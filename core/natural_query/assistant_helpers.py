# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import re
from typing import Callable
from urllib.parse import quote

from core.natural_query.algebra import solve_equation_query, solve_fraction_query
from core.natural_query.clarification import build_domain_clarification
from core.natural_query.common import (
    extract_numbers,
    format_local_result,
    local_smalltalk_response,
    normalize_natural_query,
)
from core.natural_query.elementary import solve_power_query, solve_root_query
from core.natural_query.everyday import solve_recurring_amount_query, solve_rule_of_three_query
from core.natural_query.finance import solve_finance_query, solve_interest_query, solve_school_finance_query
from core.natural_query.geometry import solve_geometry_query, solve_pythagoras_query
from core.natural_query.heuristic_intelligence import (
    improve_query_heuristically,
    solve_broad_heuristic_query,
)
from core.natural_query.language import is_english_query
from core.natural_query.motion import solve_motion_query
from core.natural_query.percent import solve_percent_change_query, solve_percent_query
from core.natural_query.physics import solve_physics_query
from core.natural_query.relationships import solve_relationship_query
from core.natural_query.simple_arithmetic import solve_simple_arithmetic
from core.natural_query.statistics import solve_average_query, solve_distribution_query, solve_summary_query
from core.natural_query.types import CLARIFICATION_EXPRESSION
from core.natural_query.units import solve_unit_conversion_query


NumberFormatter = Callable[[float | complex | str], str]
LocalSolver = Callable[[str], tuple[str, str, str] | None]
PrettyExpressionFormatter = Callable[[str], str]

_ACCOUNT_TERMS = ["konto", "account"]
_EXPENSE_TERMS = ["ausgebe", "ausgibt", "spend", "spends", "spent"]
_INCOME_TERMS = ["verdiene", "verdient", "earn", "earns", "earned", "bekomme", "erhalte"]
_DAY_TERMS = ["jeden tag", "per day", "every day"]
_WEEK_TERMS = ["jede woche", "per week", "every week"]
_MONTH_TERMS = ["jeden monat", "pro monat", "per month", "every month"]
_PERIOD_TERMS = ["tage", "tag", "days", "day", "wochen", "woche", "weeks", "week", "monate", "monat", "months", "month"]
_ROOT_TERMS = ["wurzel", "root"]
_PERCENT_TERMS = ["prozent", "percent", "rabatt", "discount", "mehrwertsteuer", "vat"]
_GEOMETRY_TERMS = ["radius", "durchmesser", "umfang", "fläche", "area", "circumference"]
_MOTION_TERMS = ["wie lange", "how long", "wie weit", "how far", "wie schnell", "how fast", "kmh", "km/h"]
_SAVING_TERMS = ["konto", "ausgebe", "ausgibt", "spare", "spend", "spends", "per day", "pro tag"]
_EARNING_TERMS = ["verdiene", "verdient", "bekomme", "erhalte", "make", "earn", "earns", "earned", "pro woche", "per week", "pro monat", "per month", "pro jahr", "per year"]
_GENERIC_RATE_TERMS = [" pro ", "per ", "woche", "wochen", "tag", "tage", "monat", "monate", "year", "week", "day", "month"]
_GEOMETRY_HELP_TERMS = ["radius", "durchmesser", "umfang", "fläche", "circle", "circumference", "diameter", "area"]
_ENGLISH_TIME_PATTERN = re.compile(
    r"how long.*?(?:for|with)\s+(?P<distance>\d+(?:\.\d+)?)\s*(?:km|kilometers?|m|meters?).*?(?:with|at)\s+(?P<speed>\d+(?:\.\d+)?)\s*(?:km/h|kmh|m/s)"
)
_ENGLISH_REPLACEMENTS = {
    "given:": " ",
    "find:": " ",
    "calculate": "berechne",
    "compute": "berechne",
    "solve": "berechne",
    "what is": "wie viel ist",
    "what are": "wie viel sind",
    "what do": "was",
    "how much is": "wie viel ist",
    "how much are": "wie viel sind",
    "how much": "wie viel",
    "how many": "wie viele",
    "how far": "wie weit",
    "how long": "wie lange",
    "how fast": "wie schnell",
    "do i need": "brauche ich",
    "do i pay": "muss ich zahlen",
    "do you get": "kommt man",
    "do 7 pieces cost": "kosten 7 stück",
    "percentage change": "prozentuale änderung",
    "percent change": "prozentuale änderung",
    "change": "änderung",
    "discount": "rabatt",
    "compound interest": "zinseszins",
    "simple interest": "zinsbetrag",
    "annual interest": "jahreszins",
    "yearly interest": "jahreszins",
    "interest amount": "zinsbetrag",
    "interest only": "nur zinsen",
    "interest": "zins",
    "vat": "mehrwertsteuer",
    "value added tax": "mehrwertsteuer",
    "sales tax": "mehrwertsteuer",
    "tax": "steuer",
    "gross price": "brutto",
    "gross amount": "brutto",
    "gross": "brutto",
    "net price": "netto",
    "net amount": "netto",
    "including": "inklusive",
    "included": "inklusive",
    "inclusive": "inklusive",
    "total amount": "endbetrag",
    "final amount": "endbetrag",
    "amount at the end": "endbetrag",
    "at the end": "am ende",
    "account": "konto",
    "spend": "ausgebe",
    "spends": "ausgibt",
    "spent": "ausgegeben",
    "earn": "verdiene",
    "earns": "verdient",
    "earned": "verdient",
    "left": "übrig",
    "remaining": "übrig",
    "every day": "jeden tag",
    "every week": "jede woche",
    "average": "durchschnitt",
    "mean": "mittelwert",
    "median": "median",
    "variance": "varianz",
    "standard deviation": "standardabweichung",
    "profit margin": "marge",
    "margin": "marge",
    "profit": "gewinn",
    "speed": "geschwindigkeit",
    "distance": "strecke",
    "time": "zeit",
    "force": "kraft",
    "density": "dichte",
    "work": "arbeit",
    "power": "leistung",
    "acceleration": "beschleunigung",
    "voltage": "spannung",
    "current": "strom",
    "rectangle": "rechteck",
    "triangle": "dreieck",
    "cuboid": "quader",
    "box": "quader",
    "circle": "kreis",
    "sphere": "kugel",
    "cylinder": "zylinder",
    "cone": "kegel",
    "surface area": "oberfläche",
    "volume": "volumen",
    "final price": "endpreis",
    "radius": "radius",
    "r": "radius",
    "height": "höhe",
    "length": "länge",
    "width": "breite",
    "base": "basis",
    "side": "seite",
    "leg": "kathete",
    "angle": "winkel",
    "adjacent": "ankathete",
    "sine rule": "sinussatz",
    "cosine rule": "kosinussatz",
    "diameter": "durchmesser",
    "circumference": "umfang",
    "area": "fläche",
    "root": "wurzel",
    "square root": "wurzel",
    "square of": "quadrat von",
    "cube of": "kubik von",
    "plus": "plus",
    "minus": "minus",
    "times": "mal",
    "divided by": "geteilt durch",
    "percent": "%",
    "of": "von",
    "for": "für",
    "from": "von",
    "to": "auf",
    "on": "von",
    "with": "mit",
    "in": "in",
    "per": "pro",
    "hour": "stunde",
    "hours": "stunden",
    "week": "woche",
    "weeks": "wochen",
    "day": "tag",
    "days": "tage",
    "month": "monat",
    "months": "monate",
    "year": "jahr",
    "years": "jahre",
    "egg": "eier",
    "eggs": "eier",
    "price": "preis",
    "cost": "kosten",
    "costs": "kosten",
    "article": "artikel",
    "product": "produkt",
    "saves": "spart",
    "save": "spare",
    "invests": "investiert",
    "invest": "investiert",
    "eat": "esse",
    "eats": "isst",
    "ate": "gegessen",
    "need": "brauche",
    "needs": "braucht",
    "consume": "verbrauche",
    "consumes": "verbraucht",
    "piece": "stück",
    "pieces": "stück",
    "value": "wert",
    "middle value": "mittlerer wert",
    "diagonal": "diagonale",
    "hypotenuse": "hypotenuse",
}


def build_live_query_preview(
    query: str,
    *,
    local_solver: LocalSolver,
    pretty_expression: PrettyExpressionFormatter,
    format_number: NumberFormatter,
) -> str:
    cleaned = query.strip()
    if not cleaned:
        return "Live-Erkennung erscheint hier."

    local = local_solver(cleaned)
    if local is not None:
        expression, answer, _ = local
        if expression == CLARIFICATION_EXPRESSION:
            return f"Live-Erkennung: Rückfrage nötig - {answer}"
        pretty = pretty_expression(expression)
        return f"Live-Erkennung: {pretty} = {answer}"

    lowered = cleaned.lower().replace(",", ".")
    values = extract_numbers(lowered)
    parts: list[str] = []

    if any(term in lowered for term in _ACCOUNT_TERMS) and values:
        parts.append(f"Startbetrag {format_number(values[0])}")
    if any(term in lowered for term in _EXPENSE_TERMS) and len(values) >= 2:
        parts.append(f"Ausgabe {format_number(values[1])}")
    if any(term in lowered for term in _INCOME_TERMS) and len(values) >= 2:
        parts.append(f"Einnahme {format_number(values[1])}")
    if any(term in lowered for term in _DAY_TERMS):
        parts.append("Rhythmus Tag")
    elif any(term in lowered for term in _WEEK_TERMS):
        parts.append("Rhythmus Woche")
    elif any(term in lowered for term in _MONTH_TERMS):
        parts.append("Rhythmus Monat")
    if any(term in lowered for term in _PERIOD_TERMS) and len(values) >= 2:
        parts.append(f"Zeitraum {format_number(values[-1])}")
    if any(term in lowered for term in _ROOT_TERMS):
        parts.append("Operation Wurzel")
    if "%" in lowered or any(term in lowered for term in _PERCENT_TERMS):
        parts.append("Operation Prozent")
    if any(term in lowered for term in _GEOMETRY_TERMS):
        parts.append("Bereich Geometrie")
    if any(term in lowered for term in _MOTION_TERMS):
        parts.append("Bereich Strecke/Zeit")

    if parts:
        return "Live-Erkennung: " + " | ".join(parts[:5])
    return "Live-Erkennung: Eingabe wird gelesen, aber die Formel ist noch nicht eindeutig."


def build_query_help(query: str, *, format_number: NumberFormatter) -> str:
    english = is_english_query(query)
    lowered = query.lower().replace(",", ".")
    values = extract_numbers(lowered)
    suggestions: list[str] = []

    if any(term in lowered for term in _SAVING_TERMS):
        a = format_number(values[0]) if len(values) > 0 else "1500"
        b = format_number(values[1]) if len(values) > 1 else "34.5"
        c = format_number(values[2]) if len(values) > 2 else "30"
        if english:
            suggestions.extend(
                [
                    f"Did you mean: If I have {a} euro in my account and spend {b} euro per day for {c} days, how much is left?",
                    f"Did you mean: {a} - ({b} × {c})?",
                    f"Did you mean: How much money is left after {c} days at {b} euro per day?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Wenn ich {a} Euro auf dem Konto habe und {b} Euro pro Tag ausgebe, wie viel bleibt nach {c} Tagen?",
                    f"Meintest du: {a} - ({b} × {c})?",
                    f"Meintest du: Wie viel Geld bleibt nach {c} Tagen bei {b} Euro pro Tag übrig?",
                ]
            )
    elif any(term in lowered for term in _EARNING_TERMS):
        a = format_number(values[0]) if len(values) > 0 else "200"
        b = format_number(values[1]) if len(values) > 1 else "1"
        if english:
            suggestions.extend(
                [
                    f"Did you mean: If I earn {a} euro per week, how much is that in {b} year?",
                    f"Did you mean: {a} euro per month for {b} years?",
                    f"Did you mean: I make {a} euro in one week. What is that in {b} year?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Wenn ich {a} Euro pro Woche verdiene, wie viel ist das in {b} Jahr?",
                    f"Meintest du: {a} Euro pro Monat für {b} Jahre?",
                    f"Meintest du: Ich verdiene {a} Euro in einer Woche. Was ist das in {b} Jahr?",
                ]
            )
    elif any(term in lowered for term in _GENERIC_RATE_TERMS):
        a = format_number(values[0]) if len(values) > 0 else "200"
        b = format_number(values[1]) if len(values) > 1 else "54"
        if english:
            suggestions.extend(
                [
                    f"Did you mean: If I have {a} eggs per week, how many do I have in {b} weeks?",
                    f"Did you mean: If I make {a} per day, how much is that in {b} days?",
                    f"Did you mean: {a} per month for {b} months?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Wenn ich {a} Eier pro Woche habe, wie viele habe ich in {b} Wochen?",
                    f"Meintest du: Wenn ich {a} pro Tag habe, wie viel ist das in {b} Tagen?",
                    f"Meintest du: {a} pro Monat für {b} Monate?",
                ]
            )
    elif any(term in lowered for term in _GEOMETRY_HELP_TERMS):
        value = format_number(values[0]) if values else "10"
        if english:
            suggestions.extend(
                [
                    f"Did you mean: What is the radius from diameter {value}?",
                    f"Did you mean: What is the circle area with radius {value}?",
                    f"Did you mean: What is the circumference with radius {value}?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Was ist der Radius bei Durchmesser {value}?",
                    f"Meintest du: Was ist die Kreisfläche mit Radius {value}?",
                    f"Meintest du: Was ist der Umfang mit Radius {value}?",
                ]
            )
    elif any(term in lowered for term in ["zeit", "stunde", "kmh", "km/h", "wie lange", "wie weit", "wie schnell", "speed", "distance", "time"]):
        a = format_number(values[0]) if len(values) > 0 else "50"
        b = format_number(values[1]) if len(values) > 1 else "3"
        if english:
            suggestions.extend(
                [
                    f"Did you mean: How long do I need for {a} km with {b} km/h?",
                    f"Did you mean: How far do you get with {a} km/h in {b} hours?",
                    f"Did you mean: How fast am I for {a} km in {b} hours?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Wie lange brauche ich für {a} km mit {b} km/h?",
                    f"Meintest du: Wie weit komme ich mit {a} km/h in {b} Stunden?",
                    f"Meintest du: Wie schnell bin ich bei {a} km in {b} Stunden?",
                ]
            )
    elif len(values) >= 2:
        a = format_number(values[0])
        b = format_number(values[1])
        if english:
            suggestions.extend(
                [
                    f"Did you mean: What is 20% of {b}?",
                    f"Did you mean: What is the square root of {a}?",
                    f"Did you mean: How far do you get with {a} km/h in {b} hours?",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Meintest du: Was sind 20% von {b}?",
                    f"Meintest du: Was ist die Wurzel von {a}?",
                    f"Meintest du: Wie weit kommt man mit {a} km/h in {b} Stunden?",
                ]
            )
    else:
        if english:
            suggestions.extend(
                [
                    "Did you mean: What is 20% of 450?",
                    "Did you mean: What is the square root of 100?",
                    "Did you mean: Given: 4 pieces cost 10 euro. Find: what do 7 pieces cost?",
                ]
            )
        else:
            suggestions.extend(
                [
                    "Meintest du: Was sind 20% von 450?",
                    "Meintest du: Was ist die Wurzel von 100?",
                    "Meintest du: Gegeben: 4 Stück kosten 10 Euro. Gesucht: Was kosten 7 Stück?",
                ]
            )

    header = (
        "I could not interpret that reliably locally. Try one of these clearer formulations:"
        if english
        else "Ich konnte das lokal nicht sicher verstehen. Versuche eine klarere Formulierung wie:"
    )
    chatgpt_url = f"https://chatgpt.com/?q={quote(query)}"
    footer = f"\n\n{chatgpt_url}"
    return header + "\n\n" + "\n".join(suggestions[:3]) + footer


def solve_local_natural_query(
    query: str,
    *,
    degrees: bool,
    format_number: NumberFormatter,
) -> tuple[str, str, str] | None:
    smalltalk = local_smalltalk_response(query)
    if smalltalk is not None:
        return smalltalk

    raw_lower = normalize_natural_query(query)
    english_time_match = _ENGLISH_TIME_PATTERN.search(raw_lower)
    if english_time_match:
        distance = float(english_time_match.group("distance"))
        speed = float(english_time_match.group("speed"))
        if speed != 0:
            value = distance / speed
            expression = f"{format_number(distance)}/{format_number(speed)}"
            explanation = "Die Zeit ist Strecke geteilt durch Geschwindigkeit."
            return format_local_result(expression, value, explanation)

    normalized = raw_lower.replace("prozent", "%")
    for source, target in sorted(_ENGLISH_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = r"(?<![a-zäöüß])" + re.escape(source) + r"(?![a-zäöüß])"
        normalized = re.sub(pattern, target, normalized)
    normalized = normalized.replace("gegeben:", " ")
    normalized = normalized.replace("gesucht:", " ")
    normalized = normalized.replace("gegeben", " ")
    normalized = normalized.replace("gesucht", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.replace("wieviel", "wie viel")
    normalized = normalized.replace(" dann ", " ")
    normalized = normalized.replace(" noch ", " ")
    normalized = normalized.replace(" übrig ", " ")
    normalized = normalized.replace("plus ", "plus ")
    normalized = re.sub(r"[?]", "", normalized)
    normalized = improve_query_heuristically(normalized)

    school_values = extract_numbers(normalized)

    heuristic_result = solve_broad_heuristic_query(normalized, school_values)
    if heuristic_result is not None:
        return heuristic_result.as_tuple()

    school_finance_result = solve_school_finance_query(normalized, school_values)
    if school_finance_result is not None:
        return school_finance_result.as_tuple()

    recurring_result = solve_recurring_amount_query(normalized)
    if recurring_result is not None:
        return recurring_result.as_tuple()

    school_rule_result = solve_rule_of_three_query(normalized, school_values, school_style=True)
    if school_rule_result is not None:
        return school_rule_result.as_tuple()

    power_result = solve_power_query(normalized)
    if power_result is not None:
        return power_result.as_tuple()

    average_result = solve_average_query(normalized)
    if average_result is not None:
        return average_result.as_tuple()

    summary_result = solve_summary_query(normalized)
    if summary_result is not None:
        return summary_result.as_tuple()

    interest_result = solve_interest_query(normalized)
    if interest_result is not None:
        return interest_result.as_tuple()

    distribution_result = solve_distribution_query(normalized)
    if distribution_result is not None:
        return distribution_result.as_tuple()

    relationship_result = solve_relationship_query(normalized)
    if relationship_result is not None:
        return relationship_result.as_tuple()

    values = extract_numbers(normalized)

    finance_result = solve_finance_query(normalized, values)
    if finance_result is not None:
        return finance_result.as_tuple()

    percent_change_result = solve_percent_change_query(normalized, values)
    if percent_change_result is not None:
        return percent_change_result.as_tuple()

    rule_of_three_result = solve_rule_of_three_query(normalized, values)
    if rule_of_three_result is not None:
        return rule_of_three_result.as_tuple()

    pythagoras_result = solve_pythagoras_query(normalized)
    if pythagoras_result is not None:
        return pythagoras_result.as_tuple()

    equation_result = solve_equation_query(normalized)
    if equation_result is not None:
        return equation_result.as_tuple()

    fraction_result = solve_fraction_query(normalized)
    if fraction_result is not None:
        return fraction_result.as_tuple()

    unit_result = solve_unit_conversion_query(normalized)
    if unit_result is not None:
        return unit_result.as_tuple()

    motion_result = solve_motion_query(normalized, values)
    if motion_result is not None:
        return motion_result.as_tuple()

    physics_result = solve_physics_query(normalized, values)
    if physics_result is not None:
        return physics_result.as_tuple()

    geometry_result = solve_geometry_query(normalized)
    if geometry_result is not None:
        return geometry_result.as_tuple()

    root_result = solve_root_query(normalized)
    if root_result is not None:
        return root_result.as_tuple()

    percent_result = solve_percent_query(normalized, values)
    if percent_result is not None:
        return percent_result.as_tuple()

    clarification = build_domain_clarification(normalized)
    if clarification is not None:
        return clarification.as_tuple()

    simple_result = solve_simple_arithmetic(normalized, degrees)
    return simple_result.as_tuple() if simple_result else None
