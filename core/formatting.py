# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations


def pretty_expression(text: str) -> str:
    return text.replace("*", " × ").replace("/", " ÷ ").replace("^", " ^ ")


def format_number(value: float | complex | str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, complex):
        real = 0.0 if abs(value.real) < 1e-14 else value.real
        imag = 0.0 if abs(value.imag) < 1e-14 else value.imag
        if imag == 0:
            return format_number(real)
        if real == 0:
            if imag == 1:
                return "i"
            if imag == -1:
                return "-i"
            return f"{format_number(imag)}i"
        sign = "+" if imag > 0 else "-"
        magnitude = abs(imag)
        imag_text = "i" if magnitude == 1 else f"{format_number(magnitude)}i"
        return f"{format_number(real)} {sign} {imag_text}"
    if abs(value) < 1e-14:
        value = 0.0
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.12g}"
