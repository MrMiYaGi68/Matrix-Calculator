from __future__ import annotations

import math

from core.formatting import format_number
from core.natural_query.common import extract_numbers, format_local_result
from core.natural_query.types import NaturalQueryResult


def solve_average_query(normalized: str) -> NaturalQueryResult | None:
    if not any(term in normalized for term in ["durchschnitt", "mittelwert", "im schnitt"]):
        return None
    values = extract_numbers(normalized)
    if not values:
        return None
    expression = f"({'+'.join(format_number(value) for value in values)})/{len(values)}"
    answer = format_number(sum(values) / len(values))
    explanation = f"Der Durchschnitt ist die Summe aller Werte geteilt durch {len(values)}."
    return NaturalQueryResult(expression, answer, explanation)


def solve_distribution_query(normalized: str) -> NaturalQueryResult | None:
    if any(term in normalized for term in ["median", "mittlerer wert", "mittlere wert"]):
        values = sorted(extract_numbers(normalized))
        if not values:
            return None
        middle = len(values) // 2
        if len(values) % 2:
            value = values[middle]
        else:
            value = (values[middle - 1] + values[middle]) / 2
        expression = "median(" + ",".join(format_number(item) for item in values) + ")"
        explanation = "Der Median ist der mittlere Wert der sortierten Liste."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["varianz", "variance", "streuung"]):
        values = extract_numbers(normalized)
        if not values:
            return None
        mean = sum(values) / len(values)
        value = sum((item - mean) ** 2 for item in values) / len(values)
        expression = "var(" + ",".join(format_number(item) for item in values) + ")"
        explanation = "Die Varianz ist der Durchschnitt der quadrierten Abweichungen vom Mittelwert."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    if any(term in normalized for term in ["standardabweichung", "stdabw", "standard abweichung"]):
        values = extract_numbers(normalized)
        if not values:
            return None
        mean = sum(values) / len(values)
        variance = sum((item - mean) ** 2 for item in values) / len(values)
        value = math.sqrt(variance)
        expression = "std(" + ",".join(format_number(item) for item in values) + ")"
        explanation = "Die Standardabweichung ist die Quadratwurzel der Varianz."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    return None
