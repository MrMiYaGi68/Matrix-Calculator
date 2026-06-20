# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations


ADVANCED_ROWS = {0, 2, 3, 4}
DEFAULT_THEME = "graphite"
BUTTON_COLUMN_COUNT = 7
BUTTON_COLUMN_SPANS = {
    "0": BUTTON_COLUMN_COUNT,
}

SECOND_MODE_LABELS = {
    "x²": "sqrt",
    "x³": "cbrt",
    "sin": "asin",
    "cos": "acos",
    "tan": "atan",
    "ln": "e^x",
    "log": "10^x",
}

BUTTON_ROWS = [
    ["2nd", "Deg", "mc", "mr", "m+", "m-", "ms"],
    ["(", ")", "%", "AC", "+/-", "mod", "÷"],
    ["x²", "x³", "1/x", "|x|", "n!", "π", "xʸ"],
    ["sin", "cos", "tan", "ln", "log", "Rand", "⌫"],
    ["sinh", "cosh", "tanh", "i", "Re", "Im", "pf"],
    ["7", "8", "9", "×", "e", ".", "CE"],
    ["4", "5", "6", "-", "(", ")", "Ans"],
    ["1", "2", "3", "+", "sqrt", "cbrt", "="],
    ["0"],
]

BUTTON_INSERTIONS = {
    "×": "*",
    "÷": "/",
    "π": "pi",
    "xʸ": "^",
    "n!": "!",
    "1/x": "inv(",
    "|x|": "abs(",
    "x²": "square(",
    "x³": "cube(",
    "sqrt": "sqrt(",
    "cbrt": "cbrt(",
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "asin": "asin(",
    "acos": "acos(",
    "atan": "atan(",
    "ln": "ln(",
    "log": "log(",
    "e^x": "exp(",
    "10^x": "pow10(",
    "mod": " mod ",
    "sinh": "sinh(",
    "cosh": "cosh(",
    "tanh": "tanh(",
    "i": "i",
    "Re": "real(",
    "Im": "imag(",
    "pf": "pf(",
}

BUTTON_SHORTCUT_HINTS = {
    "+": "+",
    "-": "-",
    "×": "*",
    "÷": "/",
    "=": "Enter",
    "⌫": "Backspace",
    "CE": "Entfernen",
    "AC": "Escape",
    "(": "(",
    ")": ")",
    "%": "%",
    ".": ".",
    "xʸ": "^",
}

BUTTON_TOOLTIP_KEYS = {
    "%": "tooltip_percent",
    "mod": "tooltip_mod",
    "Rand": "tooltip_rand",
    "sinh": "tooltip_sinh",
    "cosh": "tooltip_cosh",
    "tanh": "tooltip_tanh",
    "i": "tooltip_i",
    "Re": "tooltip_real",
    "Im": "tooltip_imag",
    "pf": "tooltip_prime_factor",
    "n!": "tooltip_factorial",
    "ln": "tooltip_ln",
    "log": "tooltip_log",
    "sqrt": "tooltip_sqrt",
    "cbrt": "tooltip_cbrt",
    "x²": "tooltip_square",
    "x³": "tooltip_cube",
    "1/x": "tooltip_inverse",
    "|x|": "tooltip_abs",
    "xʸ": "tooltip_power",
    "π": "tooltip_pi",
    "e": "tooltip_e",
    "Ans": "tooltip_ans",
    "2nd": "tooltip_second",
    "Deg": "tooltip_degrees",
    "Rad": "tooltip_radians",
}


def button_shortcut_hint(label: str) -> str | None:
    if label in BUTTON_SHORTCUT_HINTS:
        return BUTTON_SHORTCUT_HINTS[label]
    if label.isdigit():
        return label
    return None


def button_tooltip_key(label: str) -> str | None:
    return BUTTON_TOOLTIP_KEYS.get(label)
