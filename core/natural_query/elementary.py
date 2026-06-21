from __future__ import annotations

import math
import re

from core.formatting import format_number
from core.natural_query.types import NaturalQueryResult


def solve_power_query(normalized: str) -> NaturalQueryResult | None:
    explicit_power = re.search(
        r"(?:potenz\s+)?(?P<base>\d+(?:\.\d+)?)\s+(?:hoch|to the power of)\s+(?P<exponent>\d+(?:\.\d+)?)",
        normalized,
    )
    if explicit_power and ("potenz" in normalized or "hoch" in normalized or "to the power of" in normalized):
        base = float(explicit_power.group("base"))
        exponent = float(explicit_power.group("exponent"))
        value = base**exponent
        expression = f"{format_number(base)}^{format_number(exponent)}"
        answer = format_number(value)
        explanation = f"{format_number(base)} hoch {format_number(exponent)} ist {answer}."
        return NaturalQueryResult(expression, answer, explanation)

    square_match = re.search(r"(?:quadrat von|zum quadrat)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if square_match:
        value = float(square_match.group("value"))
        expression = f"{format_number(value)}^2"
        answer = format_number(value * value)
        explanation = f"Das Quadrat von {format_number(value)} ist {format_number(value)}²."
        return NaturalQueryResult(expression, answer, explanation)

    cube_match = re.search(r"(?:kubik von|hoch 3)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if cube_match:
        value = float(cube_match.group("value"))
        expression = f"{format_number(value)}^3"
        answer = format_number(value * value * value)
        explanation = f"Die dritte Potenz von {format_number(value)} ist {format_number(value)}³."
        return NaturalQueryResult(expression, answer, explanation)

    return None


def solve_root_query(normalized: str) -> NaturalQueryResult | None:
    nth_root_patterns = [
        r"(?P<degree>\d+)(?:te|ten|\.?)\s+(?:wurzel)\s+(?:von|aus)\s+(?P<value>\d+(?:\.\d+)?)",
        r"(?P<degree_word>dritte|vierte|fünfte|fuenfte|sechste|siebte|achte|neunte|zehnte)\s+(?:wurzel)\s+(?:von|aus)\s+(?P<value>\d+(?:\.\d+)?)",
    ]
    degree_words = {
        "dritte": 3,
        "vierte": 4,
        "fünfte": 5,
        "fuenfte": 5,
        "sechste": 6,
        "siebte": 7,
        "achte": 8,
        "neunte": 9,
        "zehnte": 10,
    }
    for pattern in nth_root_patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        degree = int(match.groupdict().get("degree") or degree_words[match.group("degree_word")])
        value = float(match.group("value"))
        if degree <= 0:
            return None
        result = value ** (1 / degree)
        expression = f"{format_number(value)}^(1/{format_number(degree)})"
        answer = format_number(result)
        explanation = f"Die {format_number(degree)}. Wurzel von {format_number(value)} ist {answer}."
        return NaturalQueryResult(expression, answer, explanation)

    root_patterns = [
        r"(?:was ist |wie viel ist |berechne )?(?:die )?(?:quadratwurzel|wurzel)\s+(?:von|aus)\s+(?P<value>\d+(?:\.\d+)?)",
        r"(?:was ist |wie viel ist |berechne )?(?:die )?(?:quadratwurzel|wurzel)\s+(?P<value>\d+(?:\.\d+)?)",
        r"(?:square root|root)\s+(?:of\s+)?(?P<value>\d+(?:\.\d+)?)",
        r"sqrt\s*\(?\s*(?P<value>\d+(?:\.\d+)?)\s*\)?",
    ]
    for pattern in root_patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        value = float(match.group("value"))
        expression = f"sqrt({format_number(value)})"
        answer = format_number(math.sqrt(value))
        explanation = f"Die Wurzel von {format_number(value)} ist {answer}."
        return NaturalQueryResult(expression, answer, explanation)
    return None
