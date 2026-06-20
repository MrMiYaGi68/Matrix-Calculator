from __future__ import annotations

from core.natural_query.types import CLARIFICATION_EXPRESSION, NaturalQueryResult


DOMAIN_CLARIFICATIONS = [
    (
        "Zins/Rechnung mit Geld",
        ["zins", "jahreszins", "darlehen", "kredit", "rate", "raten", "mehrwertsteuer", "mwst", "rabatt", "skonto", "marge"],
        "Ich erkenne eine Finanzaufgabe, aber nicht eindeutig genug.",
        "Bitte nenne Kapital/Preis, Prozentsatz und was gesucht ist, z. B. 'Zinsbetrag bei 1000 Euro, 11% Jahreszins, 24 Monate' oder 'Endpreis bei 200 Euro und 15% Rabatt'.",
    ),
    (
        "Zeit/Strecke/Geschwindigkeit",
        ["geschwindigkeit", "tempo", "kmh", "km/h", "m/s", "strecke", "wie weit", "wie lange"],
        "Ich erkenne eine Aufgabe zu Strecke, Zeit oder Geschwindigkeit, aber die Rollen der Zahlen sind nicht eindeutig.",
        "Bitte nenne die Einheiten direkt an den Zahlen, z. B. '600 km mit 50 km/h' oder '50 km/h für 3 Stunden'.",
    ),
    (
        "Physik",
        ["kraft", "dichte", "leistung", "watt", "joule", "beschleunigung", "spannung", "strom"],
        "Ich erkenne eine Physikaufgabe, aber eine Größe oder Einheit ist nicht eindeutig.",
        "Bitte formuliere z. B. 'Kraft bei 12 kg und 3 m/s2', 'Dichte bei 10 kg und 2 m3' oder 'Leistung bei 1000 Joule in 20 Sekunden'.",
    ),
    (
        "Geometrie",
        ["fläche", "flaeche", "umfang", "radius", "durchmesser", "volumen", "oberfläche", "oberflaeche", "dreieck", "rechteck", "zylinder", "kugel", "kegel"],
        "Ich erkenne eine Geometrieaufgabe, aber nicht eindeutig, welche Größe gegeben und welche gesucht ist.",
        "Bitte nenne Form und gesuchte Größe, z. B. 'Kreisfläche mit Radius 5' oder 'Zylindervolumen Radius 3 Höhe 10'.",
    ),
    (
        "Prozentrechnung",
        ["%", "prozent", "anteil", "änderung", "aenderung"],
        "Ich erkenne eine Prozentaufgabe, aber nicht eindeutig genug.",
        "Bitte formuliere z. B. '20% von 450', '100 plus 19%' oder 'prozentuale Änderung von 80 auf 100'.",
    ),
]


def build_domain_clarification(normalized: str) -> NaturalQueryResult | None:
    for _, keywords, question, hint in DOMAIN_CLARIFICATIONS:
        if any(keyword in normalized for keyword in keywords):
            return NaturalQueryResult(CLARIFICATION_EXPRESSION, question, hint)
    return None
