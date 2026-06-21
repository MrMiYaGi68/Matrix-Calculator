from __future__ import annotations

import math
import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import NaturalQueryResult


def solve_equation_query(normalized: str) -> NaturalQueryResult | None:
    # 1. Linear simple: ax = c or x = c
    linear_simple_match = re.search(
        r"^(?:(?P<a>-?\d+(?:\.\d+)?)\s*\*?\s*)?x\s*=\s*(?P<c>-?\d+(?:\.\d+)?)$",
        normalized,
    )
    if linear_simple_match:
        a = float(linear_simple_match.group("a") or 1)
        c = float(linear_simple_match.group("c"))
        if a != 0:
            value = c / a
            expression = f"{format_number(c)}/{format_number(a)}"
            explanation = f"x = {format_number(c)} / {format_number(a)}"
            return NaturalQueryResult(*format_local_result(expression, value, explanation))

    # 2. Quadratic: ax^2 + bx + c = 0 (supports missing a, b coefficients)
    quadratic_match = re.search(
        r"(?:(?P<a>-?\d+(?:\.\d+)?)\s*\*?\s*)?x\^?2\s*(?:(?P<op1>[+-])\s*(?:(?P<b>\d+(?:\.\d+)?)\s*\*?\s*)?x)?\s*(?:(?P<op2>[+-])\s*(?P<c>\d+(?:\.\d+)?))?\s*=\s*0",
        normalized,
    )
    if quadratic_match:
        a = float(quadratic_match.group("a") or 1)
        b_str = quadratic_match.group("b")
        b = float(b_str or 1) if quadratic_match.group("op1") else 0
        if quadratic_match.group("op1") == "-":
            b = -b
        c_str = quadratic_match.group("c")
        c = float(c_str) if quadratic_match.group("op2") else 0
        if quadratic_match.group("op2") == "-":
            c = -c
        
        if a != 0:
            discriminant = b * b - 4 * a * c
            if discriminant >= 0:
                root = math.sqrt(discriminant)
                x1 = (-b + root) / (2 * a)
                x2 = (-b - root) / (2 * a)
                if x1 == x2:
                    answer = f"x = {format_number(x1)}"
                    expression = f"x={format_number(x1)}"
                else:
                    answer = f"x1 = {format_number(x1)}, x2 = {format_number(x2)}"
                    expression = f"x1={format_number(x1)}, x2={format_number(x2)}"
                explanation = "Die quadratische Gleichung wurde mit der Mitternachtsformel gelöst."
                return NaturalQueryResult(expression, answer, explanation)
            else:
                # Complex roots
                real = -b / (2 * a)
                imag = math.sqrt(-discriminant) / (2 * a)
                x1 = complex(real, imag)
                x2 = complex(real, -imag)
                answer = f"x1 = {format_number(x1)}, x2 = {format_number(x2)}"
                expression = f"x1={format_number(x1)}, x2={format_number(x2)}"
                explanation = "Die quadratische Gleichung hat komplexe Lösungen."
                return NaturalQueryResult(expression, answer, explanation)

    # 3. Linear: ax + b = c
    linear_match = re.search(
        r"(?:(?P<a>-?\d+(?:\.\d+)?)\s*\*?\s*)?x(?!\s*\^?2)\s*(?P<op>[+-])\s*(?P<b>\d+(?:\.\d+)?)\s*=\s*(?P<c>-?\d+(?:\.\d+)?)",
        normalized,
    )
    if linear_match:
        a = float(linear_match.group("a") or 1)
        b = float(linear_match.group("b"))
        c = float(linear_match.group("c"))
        if linear_match.group("op") == "-":
            b = -b
        if a != 0:
            value = (c - b) / a
            expression = f"({format_number(c)}-{format_number(b)})/{format_number(a)}"
            explanation = "Die lineare Gleichung wird nach x umgestellt: x = (c - b) / a."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))

    system_match = re.search(
        r"(?P<a1>-?\d+(?:\.\d+)?)x\s*(?P<op1>[+-])\s*(?P<b1>\d+(?:\.\d+)?)y\s*=\s*(?P<c1>-?\d+(?:\.\d+)?).*(?P<a2>-?\d+(?:\.\d+)?)x\s*(?P<op2>[+-])\s*(?P<b2>\d+(?:\.\d+)?)y\s*=\s*(?P<c2>-?\d+(?:\.\d+)?)",
        normalized,
    )
    if system_match:
        a1 = float(system_match.group("a1"))
        b1 = float(system_match.group("b1")) * (-1 if system_match.group("op1") == "-" else 1)
        c1 = float(system_match.group("c1"))
        a2 = float(system_match.group("a2"))
        b2 = float(system_match.group("b2")) * (-1 if system_match.group("op2") == "-" else 1)
        c2 = float(system_match.group("c2"))
        det = a1 * b2 - a2 * b1
        if det != 0:
            x_value = (c1 * b2 - c2 * b1) / det
            y_value = (a1 * c2 - a2 * c1) / det
            expression = f"x={format_number(x_value)}, y={format_number(y_value)}"
            answer = f"x = {format_number(x_value)}, y = {format_number(y_value)}"
            explanation = "Das lineare Gleichungssystem wurde mit dem Determinantenverfahren gelöst."
            return NaturalQueryResult(expression, answer, explanation)

    x_right_match = re.search(r"x\s*=\s*(?P<value>-?\d+(?:\.\d+)?)", normalized)
    if x_right_match:
        value = float(x_right_match.group("value"))
        expression = format_number(value)
        explanation = "Die Gleichung ist bereits nach x aufgelöst."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    return None


def solve_fraction_query(normalized: str) -> NaturalQueryResult | None:
    written_fraction = _solve_written_fraction_of_query(normalized)
    if written_fraction is not None:
        return written_fraction

    fraction_match = re.search(
        r"(?P<a>\d+)\s*/\s*(?P<b>\d+)\s*(?P<op>[+\-*/])\s*(?P<c>\d+)\s*/\s*(?P<d>\d+)",
        normalized,
    )
    if not fraction_match:
        return None
    a = float(fraction_match.group("a"))
    b = float(fraction_match.group("b"))
    c = float(fraction_match.group("c"))
    d = float(fraction_match.group("d"))
    op = fraction_match.group("op")
    if b == 0 or d == 0:
        return None
    left = a / b
    right = c / d
    value = {
        "+": left + right,
        "-": left - right,
        "*": left * right,
        "/": left / right if right != 0 else None,
    }[op]
    if value is None:
        return None
    expression = f"({format_number(a)}/{format_number(b)}){op}({format_number(c)}/{format_number(d)})"
    explanation = "Die Bruchrechnung wurde als Rechenoperation zwischen zwei Brüchen ausgewertet."
    return NaturalQueryResult(*format_local_result(expression, value, explanation))


def _solve_written_fraction_of_query(normalized: str) -> NaturalQueryResult | None:
    denominator_words = {
        "hälfte": 2,
        "haelfte": 2,
        "halb": 2,
        "drittel": 3,
        "viertel": 4,
        "fünftel": 5,
        "fuenftel": 5,
        "sechstel": 6,
        "siebtel": 7,
        "achtel": 8,
        "neuntel": 9,
        "zehntel": 10,
    }
    denominator_pattern = "|".join(sorted((re.escape(key) for key in denominator_words), key=len, reverse=True))
    match = re.search(
        rf"(?:die\s+)?(?:(?P<numerator>ein|eine|\d+(?:\.\d+)?)\s+)?(?P<denominator>{denominator_pattern})\s+von\s+(?P<base>\d+(?:\.\d+)?)",
        normalized,
    )
    if not match:
        return None
    numerator_text = match.group("numerator")
    numerator = 1.0 if numerator_text in {None, "ein", "eine"} else float(numerator_text)
    denominator = float(denominator_words[match.group("denominator")])
    base = float(match.group("base"))
    value = numerator / denominator * base
    expression = f"({format_number(numerator)}/{format_number(denominator)})*{format_number(base)}"
    explanation = "Der ausgeschriebene Bruchteil wird als Zähler ÷ Nenner × Grundwert berechnet."
    return NaturalQueryResult(*format_local_result(expression, value, explanation))
