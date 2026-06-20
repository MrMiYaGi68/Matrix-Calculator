from __future__ import annotations

import re

from core.formatting import format_number
from core.natural_query.common import format_local_result, unit_factor
from core.natural_query.types import NaturalQueryResult


def solve_motion_query(normalized: str, values: list[float]) -> NaturalQueryResult | None:
    # Extract with units
    speed_match = re.search(r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>km/h|kmh|m/s)", normalized)
    time_match = re.search(r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>stunden|stunde|h|sekunden|sekunde|s|minuten|minute|min)", normalized)
    dist_match = re.search(r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>kilometer|km|meter|m)(?![/h])", normalized)
    
    s_val = float(speed_match.group("val")) if speed_match else None
    s_unit = speed_match.group("unit") if speed_match else None
    
    t_val = float(time_match.group("val")) if time_match else None
    t_unit = time_match.group("unit") if time_match else None
    
    d_val = float(dist_match.group("val")) if dist_match else None
    d_unit = dist_match.group("unit") if dist_match else None

    # Normalization
    def to_si(val, unit, kind):
        if val is None: return None
        if kind == "speed":
            return val / 3.6 if unit in ["km/h", "kmh"] else val
        factor = unit_factor(unit)
        return val * factor if factor else val

    s_si = to_si(s_val, s_unit, "speed")
    t_si = to_si(t_val, t_unit, "time")
    d_si = to_si(d_val, d_unit, "distance")

    # 1. Time Calculation
    if any(term in normalized for term in ["wie lange", "wie viel zeit", "brauche ich"]):
        # Heuristic for numbers without units but clear question
        if d_si is None and s_si is None and len(values) >= 2:
            # Check if ambiguous (test expects clarification for "wie lange brauche ich bei 600 und 50")
            from core.natural_query.types import CLARIFICATION_EXPRESSION
            return NaturalQueryResult(
                CLARIFICATION_EXPRESSION, 
                "Ich erkenne eine Zeitberechnung (Strecke/Geschwindigkeit), aber die Einheiten fehlen.", 
                f"Meinst du {format_number(values[0])} km und {format_number(values[1])} km/h?"
            )
        
        if d_si is not None and s_si is not None and s_si != 0:
            res_s = d_si / s_si
            # Return in hours if result is large
            res = res_s / 3600 if res_s >= 60 else res_s
            expression = f"{format_number(d_si)}/{format_number(s_si)}"
            explanation = f"Zeit = Strecke / Geschwindigkeit. ({format_number(res_s)} s)"
            return NaturalQueryResult(expression, format_number(res), explanation)

    # 2. Distance Calculation
    if any(term in normalized for term in ["wie weit", "welche strecke", "wie viele kilometer"]) and s_si is not None and t_si is not None:
        res_m = s_si * t_si
        res = res_m / 1000 if res_m >= 1000 else res_m
        expression = f"{format_number(s_si)}*{format_number(t_si)}"
        explanation = f"Strecke = Geschwindigkeit * Zeit. ({format_number(res_m)} m)"
        return NaturalQueryResult(expression, format_number(res), explanation)

    # 3. Speed Calculation
    if any(term in normalized for term in ["geschwindigkeit", "tempo", "wie schnell"]) and d_si is not None and t_si is not None:
        if t_si != 0:
            res_ms = d_si / t_si
            res = res_ms * 3.6 if res_ms >= 1 else res_ms
            expression = f"{format_number(d_si)}/{format_number(t_si)}"
            explanation = f"Geschwindigkeit = Strecke / Zeit. ({format_number(res_ms)} m/s)"
            return NaturalQueryResult(expression, format_number(res), explanation)

    return None
