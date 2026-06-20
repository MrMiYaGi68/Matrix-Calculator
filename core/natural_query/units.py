from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import UNIT_FACTORS, format_local_result, unit_factor
from core.natural_query.types import NaturalQueryResult


UNIT_PATTERN = "|".join(re.escape(unit) for unit in sorted(UNIT_FACTORS, key=len, reverse=True))
CONVERSION_WORD_PATTERN = r"in|zu|nach|als|->|=>|=|-"
VALUE_PATTERN = r"\d+(?:\.\d+)?"


def solve_unit_conversion_query(normalized: str) -> NaturalQueryResult | None:
    unit_match = _match_value_first(normalized) or _match_value_last(normalized)
    if not unit_match:
        return None
    value = float(unit_match.group("value"))
    from_unit = unit_match.group("from")
    to_unit = unit_match.group("to")
    from_factor = unit_factor(from_unit)
    to_factor = unit_factor(to_unit)
    if from_factor is None or to_factor is None:
        return None
    converted = value * from_factor / to_factor
    expression = f"{format_number(value)} {from_unit} -> {to_unit}"
    explanation = f"Die Einheit wurde über einen gemeinsamen Basisfaktor von {from_unit} nach {to_unit} umgerechnet."
    return NaturalQueryResult(*format_local_result(expression, converted, explanation))


def _match_value_first(normalized: str) -> re.Match[str] | None:
    return re.search(
        rf"(?P<value>{VALUE_PATTERN})\s*(?P<from>{UNIT_PATTERN})\s*(?:{CONVERSION_WORD_PATTERN})\s*(?P<to>{UNIT_PATTERN})(?![a-zäöüß])",
        normalized,
    )


def _match_value_last(normalized: str) -> re.Match[str] | None:
    return re.search(
        rf"(?P<from>{UNIT_PATTERN})\s*(?:{CONVERSION_WORD_PATTERN})\s*(?P<to>{UNIT_PATTERN})\s*(?P<value>{VALUE_PATTERN})(?![a-zäöüß])",
        normalized,
    )
