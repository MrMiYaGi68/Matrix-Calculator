from __future__ import annotations

import re

from core.expression_parser import CalculatorError, ExpressionParser
from core.formatting import format_number, pretty_expression
from core.natural_query.common import normalize_natural_query
from core.natural_query.types import NaturalQueryResult


def prepare_simple_expression(text: str) -> str:
    cleaned = f" {normalize_natural_query(text)} "
    phrase_replacements = {
        " wie viel ist ": " ",
        " wieviel ist ": " ",
        " was ist ": " ",
        " was sind ": " ",
        " rechne bitte ": " ",
        " rechne ": " ",
        " rechnen bitte ": " ",
        " rechnen ": " ",
        " berechne bitte ": " ",
        " berechne ": " ",
        " calculate ": " ",
        " compute ": " ",
        " can you calculate ": " ",
        " could you calculate ": " ",
        " kannst du ": " ",
        " bitte ": " ",
        " mal ": " ",
        " einfach ": " ",
        " denn ": " ",
        " für mich ": " ",
    }
    for source, target in phrase_replacements.items():
        cleaned = cleaned.replace(source, target)

    replacements = {
        " mal ": " * ",
        " plus ": " + ",
        " minus ": " - ",
        " geteilt durch ": " / ",
        " geteilt ": " / ",
        " hoch ": " ^ ",
        " von ": " * ",
        " wurzel aus ": " sqrt(",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)

    # Smart percent logic for "100 + 19%"
    # We find patterns like "NUMBER [+-] NUMBER %"
    def replace_percent_logic(match: re.Match[str]) -> str:
        base = match.group("base")
        op = match.group("op")
        pct = match.group("pct")
        return f"{base}{op}({base}*{pct}/100)"

    cleaned_with_space = f" {cleaned} "
    # Regex to find: base (+ or -) percent %
    # Example: 100 + 19 %
    cleaned_with_space = re.sub(
        r"(?P<base>\d+(?:\.\d+)?)\s*(?P<op>[+-])\s*(?P<pct>\d+(?:\.\d+)?)\s*%",
        replace_percent_logic,
        cleaned_with_space
    )
    cleaned = cleaned_with_space.strip()

    cleaned = cleaned.replace("%", "/100")
    cleaned = re.sub(r"[?!=;,]", " ", cleaned)
    cleaned = re.sub(r"[^0-9a-z+\-*/^(). _]", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def solve_simple_arithmetic(text: str, degrees: bool) -> NaturalQueryResult | None:
    cleaned = prepare_simple_expression(text)
    if not cleaned:
        return None
    try:
        result = ExpressionParser(cleaned, degrees).parse()
    except (CalculatorError, ValueError, OverflowError):
        return None
    explanation = f"Direkt ausgewertet als {pretty_expression(cleaned)}."
    return NaturalQueryResult(cleaned, format_number(result), explanation)
