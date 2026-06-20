from __future__ import annotations

import math
import re

from core.formatting import format_number
from core.natural_query.common import format_local_result
from core.natural_query.types import NaturalQueryResult


def solve_pythagoras_query(normalized: str) -> NaturalQueryResult | None:
    pythagoras_hyp = re.search(
        r"(?:pythagoras|hypotenuse).*(?:kathete a|seite a|a)\s+(?P<a>\d+(?:\.\d+)?).*(?:kathete b|seite b|b)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    if pythagoras_hyp:
        a = float(pythagoras_hyp.group("a"))
        b = float(pythagoras_hyp.group("b"))
        value = math.sqrt(a * a + b * b)
        expression = f"sqrt({format_number(a)}^2+{format_number(b)}^2)"
        explanation = "Nach Pythagoras gilt c = √(a² + b²)."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    pythagoras_leg = re.search(
        r"(?:pythagoras|kathete).*(?:hypotenuse|c)\s+(?P<c>\d+(?:\.\d+)?).*(?:kathete|seite)\s+(?P<a>\d+(?:\.\d+)?)",
        normalized,
    )
    if pythagoras_leg:
        c = float(pythagoras_leg.group("c"))
        a = float(pythagoras_leg.group("a"))
        if c > a:
            value = math.sqrt(c * c - a * a)
            expression = f"sqrt({format_number(c)}^2-{format_number(a)}^2)"
            explanation = "Für die fehlende Kathete gilt a = √(c² - b²)."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))

    return None


def solve_geometry_query(normalized: str) -> NaturalQueryResult | None:
    rectangle_area = re.search(
        r"(?:rechteckfl[aä]che|fl[aä]che des rechtecks).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    rectangle_area_alt = re.search(
        r"(?:rechteck.*fl[aä]che|fl[aä]che.*rechteck).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    if rectangle_area or rectangle_area_alt:
        match = rectangle_area or rectangle_area_alt
        a = float(match.group("a"))
        b = float(match.group("b"))
        return NaturalQueryResult(f"{format_number(a)}*{format_number(b)}", format_number(a * b), "Die Rechteckfläche ist Länge × Breite.")

    rectangle_perimeter = re.search(
        r"(?:umfang des rechtecks|rechteckumfang).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    rectangle_perimeter_alt = re.search(
        r"(?:rechteck.*umfang|umfang.*rechteck).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    if rectangle_perimeter or rectangle_perimeter_alt:
        match = rectangle_perimeter or rectangle_perimeter_alt
        a = float(match.group("a"))
        b = float(match.group("b"))
        return NaturalQueryResult(f"2*({format_number(a)}+{format_number(b)})", format_number(2 * (a + b)), "Der Rechteckumfang ist 2 × (Länge + Breite).")

    rectangle_diagonal = re.search(
        r"(?:diagonale des rechtecks|rechteck diagonal).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    if rectangle_diagonal:
        a = float(rectangle_diagonal.group("a"))
        b = float(rectangle_diagonal.group("b"))
        value = math.sqrt(a * a + b * b)
        return NaturalQueryResult(f"sqrt({format_number(a)}^2+{format_number(b)}^2)", format_number(value), "Die Rechteckdiagonale ergibt sich mit Pythagoras.")

    triangle_area = re.search(
        r"(?:dreiecksfl[aä]che|fl[aä]che des dreiecks).*(?:grundseite|basis)\s+(?P<a>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    triangle_area_alt = re.search(
        r"(?:dreieck.*fl[aä]che|fl[aä]che.*dreieck).*(?:grundseite|basis)\s+(?P<a>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<b>\d+(?:\.\d+)?)",
        normalized,
    )
    if triangle_area or triangle_area_alt:
        match = triangle_area or triangle_area_alt
        a = float(match.group("a"))
        b = float(match.group("b"))
        return NaturalQueryResult(f"({format_number(a)}*{format_number(b)})/2", format_number((a * b) / 2), "Die Dreiecksfläche ist Grundseite × Höhe ÷ 2.")

    right_triangle_height = re.search(
        r"(?:h[oö]he im dreieck|h[oö]he des dreiecks).*(?:seite|grundseite|basis)\s+(?P<a>\d+(?:\.\d+)?).*(?:winkel)\s+(?P<angle>\d+(?:\.\d+)?)",
        normalized,
    )
    if right_triangle_height:
        side = float(right_triangle_height.group("a"))
        angle = float(right_triangle_height.group("angle"))
        value = side * math.sin(math.radians(angle))
        expression = f"{format_number(side)}*sin({format_number(angle)})"
        explanation = "In einem rechtwinkligen Dreieck ergibt sich die Gegenkathete aus Hypotenuse × sin(Winkel)."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    right_triangle_adjacent = re.search(
        r"(?:ankathete|anliegende seite).*(?:hypotenuse)\s+(?P<a>\d+(?:\.\d+)?).*(?:winkel)\s+(?P<angle>\d+(?:\.\d+)?)",
        normalized,
    )
    if right_triangle_adjacent:
        hyp = float(right_triangle_adjacent.group("a"))
        angle = float(right_triangle_adjacent.group("angle"))
        value = hyp * math.cos(math.radians(angle))
        expression = f"{format_number(hyp)}*cos({format_number(angle)})"
        explanation = "In einem rechtwinkligen Dreieck ergibt sich die Ankathete aus Hypotenuse × cos(Winkel)."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    sine_rule = re.search(
        r"(?:sinussatz).*(?:seite a|a)\s+(?P<a>\d+(?:\.\d+)?).*(?:winkel a)\s+(?P<A>\d+(?:\.\d+)?).*(?:winkel b)\s+(?P<B>\d+(?:\.\d+)?)",
        normalized,
    )
    if sine_rule:
        a = float(sine_rule.group("a"))
        angle_a = float(sine_rule.group("A"))
        angle_b = float(sine_rule.group("B"))
        if math.sin(math.radians(angle_a)) != 0:
            value = a * math.sin(math.radians(angle_b)) / math.sin(math.radians(angle_a))
            expression = f"{format_number(a)}*sin({format_number(angle_b)})/sin({format_number(angle_a)})"
            explanation = "Der Sinussatz nutzt das Verhältnis von Seite zu Sinus des gegenüberliegenden Winkels."
            return NaturalQueryResult(*format_local_result(expression, value, explanation))

    cosine_rule = re.search(
        r"(?:kosinussatz).*(?:seite a|a)\s+(?P<a>\d+(?:\.\d+)?).*(?:seite b|b)\s+(?P<b>\d+(?:\.\d+)?).*(?:winkel c|gamma)\s+(?P<C>\d+(?:\.\d+)?)",
        normalized,
    )
    if cosine_rule:
        a = float(cosine_rule.group("a"))
        b = float(cosine_rule.group("b"))
        angle_c = float(cosine_rule.group("C"))
        value = math.sqrt(a * a + b * b - 2 * a * b * math.cos(math.radians(angle_c)))
        expression = f"sqrt({format_number(a)}^2+{format_number(b)}^2-2*{format_number(a)}*{format_number(b)}*cos({format_number(angle_c)}))"
        explanation = "Der Kosinussatz berechnet die dritte Seite aus zwei Seiten und dem eingeschlossenen Winkel."
        return NaturalQueryResult(*format_local_result(expression, value, explanation))

    circle_area = re.search(r"(?:kreisfl[aä]che|fl[aä]che des kreises).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    circle_area_alt = re.search(r"(?:kreis.*fl[aä]che|fl[aä]che.*kreis).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if circle_area or circle_area_alt:
        radius = float((circle_area or circle_area_alt).group("value"))
        expression = f"pi*{format_number(radius)}^2"
        answer = format_number(math.pi * radius * radius)
        explanation = f"Die Kreisfläche ist π × r² = π × {format_number(radius)}²."
        return NaturalQueryResult(expression, answer, explanation)

    circumference = re.search(r"(?:umfang).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if circumference:
        radius = float(circumference.group("value"))
        expression = f"2*pi*{format_number(radius)}"
        answer = format_number(2 * math.pi * radius)
        explanation = f"Der Umfang ist 2 × π × r = 2 × π × {format_number(radius)}."
        return NaturalQueryResult(expression, answer, explanation)

    diameter = re.search(r"(?:durchmesser).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if diameter:
        radius = float(diameter.group("value"))
        expression = f"2*{format_number(radius)}"
        answer = format_number(2 * radius)
        explanation = f"Der Durchmesser ist 2 × r = 2 × {format_number(radius)}."
        return NaturalQueryResult(expression, answer, explanation)

    radius_from_diameter = re.search(r"(?:radius).*(?:durchmesser)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if radius_from_diameter:
        value = float(radius_from_diameter.group("value"))
        expression = f"{format_number(value)}/2"
        answer = format_number(value / 2)
        explanation = f"Der Radius ist der halbe Durchmesser: {format_number(value)} ÷ 2."
        return NaturalQueryResult(expression, answer, explanation)

    radius_guess = re.search(r"(?:was ist |wie gro[ßs] ist |berechne )?(?:der )?radius\s+(?:von|bei)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if radius_guess and not any(term in normalized for term in ["fläche", "umfang"]):
        value = float(radius_guess.group("value"))
        expression = f"{format_number(value)}/2"
        answer = format_number(value / 2)
        explanation = f"Wenn {format_number(value)} der Durchmesser ist, ist der Radius die Hälfte."
        return NaturalQueryResult(expression, answer, explanation)

    radius_from_area = re.search(r"(?:radius).*(?:fl[aä]che|kreisfl[aä]che)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if radius_from_area:
        value = float(radius_from_area.group("value"))
        expression = f"sqrt({format_number(value)}/pi)"
        answer = format_number(math.sqrt(value / math.pi))
        explanation = "Aus A = πr² folgt r = √(A/π)."
        return NaturalQueryResult(expression, answer, explanation)

    radius_from_circumference = re.search(r"(?:radius).*(?:umfang)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if radius_from_circumference:
        value = float(radius_from_circumference.group("value"))
        expression = f"{format_number(value)}/(2*pi)"
        answer = format_number(value / (2 * math.pi))
        explanation = "Aus U = 2πr folgt r = U / (2π)."
        return NaturalQueryResult(expression, answer, explanation)

    sphere_volume = re.search(r"(?:volumen der kugel|kugelvolumen).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if sphere_volume:
        radius = float(sphere_volume.group("value"))
        expression = f"(4/3)*pi*{format_number(radius)}^3"
        answer = format_number((4 / 3) * math.pi * radius**3)
        return NaturalQueryResult(expression, answer, "Das Kugelvolumen ist 4/3 × π × r³.")

    cylinder_volume = re.search(
        r"(?:volumen des zylinders|zylindervolumen).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    cylinder_volume_alt = re.search(
        r"(?:volumen.*zylinder|zylinder.*volumen).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    if cylinder_volume or cylinder_volume_alt:
        match = cylinder_volume or cylinder_volume_alt
        radius = float(match.group("r"))
        height = float(match.group("h"))
        expression = f"pi*{format_number(radius)}^2*{format_number(height)}"
        answer = format_number(math.pi * radius * radius * height)
        return NaturalQueryResult(expression, answer, "Das Zylindervolumen ist π × r² × h.")

    cone_volume = re.search(
        r"(?:volumen des kegels|kegelvolumen).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    cone_volume_alt = re.search(
        r"(?:volumen.*kegel|kegel.*volumen).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    if cone_volume or cone_volume_alt:
        match = cone_volume or cone_volume_alt
        radius = float(match.group("r"))
        height = float(match.group("h"))
        expression = f"(pi*{format_number(radius)}^2*{format_number(height)})/3"
        answer = format_number((math.pi * radius * radius * height) / 3)
        return NaturalQueryResult(expression, answer, "Das Kegelvolumen ist Grundfläche × Höhe ÷ 3.")

    cuboid_volume = re.search(
        r"(?:volumen des quaders|quadervolumen).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<c>\d+(?:\.\d+)?)",
        normalized,
    )
    cuboid_volume_alt = re.search(
        r"(?:volumen.*quader|quader.*volumen).*(?:l[aä]nge)\s+(?P<a>\d+(?:\.\d+)?).*(?:breite)\s+(?P<b>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<c>\d+(?:\.\d+)?)",
        normalized,
    )
    if cuboid_volume or cuboid_volume_alt:
        match = cuboid_volume or cuboid_volume_alt
        a = float(match.group("a"))
        b = float(match.group("b"))
        c = float(match.group("c"))
        return NaturalQueryResult(f"{format_number(a)}*{format_number(b)}*{format_number(c)}", format_number(a * b * c), "Das Quadervolumen ist Länge × Breite × Höhe.")

    sphere_surface = re.search(r"(?:oberfl[aä]che der kugel|kugeloberfl[aä]che).*(?:radius)\s+(?P<value>\d+(?:\.\d+)?)", normalized)
    if sphere_surface:
        radius = float(sphere_surface.group("value"))
        expression = f"4*pi*{format_number(radius)}^2"
        answer = format_number(4 * math.pi * radius * radius)
        return NaturalQueryResult(expression, answer, "Die Kugeloberfläche ist 4 × π × r².")

    cylinder_surface = re.search(
        r"(?:oberfl[aä]che des zylinders|zylinderoberfl[aä]che).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    cylinder_surface_alt = re.search(
        r"(?:oberfl[aä]che.*zylinder|zylinder.*oberfl[aä]che).*(?:radius)\s+(?P<r>\d+(?:\.\d+)?).*(?:h[oö]he)\s+(?P<h>\d+(?:\.\d+)?)",
        normalized,
    )
    if cylinder_surface or cylinder_surface_alt:
        match = cylinder_surface or cylinder_surface_alt
        radius = float(match.group("r"))
        height = float(match.group("h"))
        expression = f"2*pi*{format_number(radius)}*({format_number(radius)}+{format_number(height)})"
        answer = format_number(2 * math.pi * radius * (radius + height))
        return NaturalQueryResult(expression, answer, "Die Zylinderoberfläche ist 2πr(r + h).")

    return None
