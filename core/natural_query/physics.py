from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result, unit_factor
from core.natural_query.types import NaturalQueryResult


def solve_physics_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    # 1. Power (Watt) - Voltage and Current
    voltage_current_power = re.search(r"(?P<volt>\d+(?:\.\d+)?)\s*v.*(?P<amp>\d+(?:\.\d+)?)\s*a", normalized)
    if any(term in normalized for term in ["leistung", "watt"]) and voltage_current_power:
        volt = float(voltage_current_power.group("volt"))
        amp = float(voltage_current_power.group("amp"))
        value = volt * amp
        expression = f"{format_number(volt)}*{format_number(amp)}"
        explanation = "Elektrische Leistung ist Spannung × Strom."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    # 2. Power (Watt) - Work and Time
    def get_val_with_unit(patterns):
        for p in patterns:
            m = re.search(p, normalized)
            if m:
                val = float(m.group("val"))
                unit = m.group("unit")
                factor = unit_factor(unit) if unit else 1.0
                if factor:
                    # Special case for mass (gram vs kg)
                    if unit in ["g", "gramm", "mg"]:
                        return (val * factor) / 1000.0
                    if unit in ["kg", "kilogramm"]:
                        return val
                    return val * factor
                return val
        return None

    if any(term in normalized for term in ["leistung", "watt"]):
        work = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>joule|j)"])
        time_val = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>sekunden|sekunde|s|minuten|minute|min|stunden|stunde|h)"])
        if work is not None and time_val and time_val != 0:
            res = work / time_val
            return NaturalQueryResult(f"{format_number(work)}/{format_number(time_val)}", format_number(res), "Leistung = Arbeit / Zeit (in Watt)")

    # 3. Force (Newton)
    if any(term in normalized for term in ["kraft", "newton"]):
        mass = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>kg|kilogramm|mg|g|gramm)(?![a-z])"])
        accel = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>m/s2|m/s\^2)"])
        if mass is not None and accel is not None:
            res = mass * accel
            return NaturalQueryResult(f"{format_number(mass)}*{format_number(accel)}", format_number(res), "Kraft = Masse * Beschleunigung (in Newton)")

    # 4. Density
    if "dichte" in normalized:
        mass = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>kg|kilogramm|mg|g|gramm)(?![a-z])"])
        volume = get_val_with_unit([r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>m3|m\^3|cm3|cm\^3|l)"])
        if mass is not None and volume is not None and volume != 0:
            res = mass / volume
            expression = f"{format_number(mass)}/{format_number(volume)}"
            explanation = "Dichte ist Masse geteilt durch Volumen."
            return NaturalQueryResult(*format_local_result(expression, res, explanation))

    # Fallback to simple logic
    if any(term in normalized for term in ["arbeit", "arbeit in joule"]) and len(values) >= 2:
        force = values[0]
        distance = values[1]
        value = force * distance
        expression = f"{format_number(force)}*{format_number(distance)}"
        explanation = "Arbeit ist Kraft mal Weg."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    # Error message if physics terms found but no clear formula
    if any(term in normalized for term in ["leistung", "kraft", "dichte", "beschleunigung", "arbeit"]):
        from core.natural_query.types import CLARIFICATION_EXPRESSION
        return NaturalQueryResult(CLARIFICATION_EXPRESSION, "Ich erkenne eine Physikaufgabe, aber eine Größe oder Einheit ist nicht eindeutig.", "Bitte gib Werte mit Einheiten an (z. B. 10 kg, 5 m/s2, 12 V). (Dichte, Kraft, Leistung)")

    return None
