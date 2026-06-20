from __future__ import annotations

import math
import re

from core.formatting import format_number
from core.natural_query.types import NaturalQueryResult


def solve_power_query(normalized: str) -> NaturalQueryResult | None:
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
