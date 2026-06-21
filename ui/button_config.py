# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations


ADVANCED_ROWS = {0, 2, 3, 4}
BASIC_VISIBLE_ADVANCED_BUTTONS = {"x²", "x³", "π", "⌫"}
BASIC_HIDDEN_BUTTONS = {"CE", "Ans"}
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

SCIENTIFIC_BUTTON_GROUPS = {
    "2nd": "mode", "Deg": "mode",
    "mc": "memory", "mr": "memory", "m+": "memory", "m-": "memory", "ms": "memory",
    "(": "entry", ")": "entry", "%": "entry", "AC": "entry", "+/-": "entry",
    "mod": "entry", "÷": "entry", "⌫": "entry", "CE": "entry", "Ans": "entry",
    "x²": "power", "x³": "power", "1/x": "power", "|x|": "power", "n!": "power",
    "π": "power", "xʸ": "power", "e": "power", "sqrt": "power", "cbrt": "power",
    "Rand": "power",
    "sin": "trig", "cos": "trig", "tan": "trig", "ln": "trig", "log": "trig",
    "sinh": "trig", "cosh": "trig", "tanh": "trig",
    "i": "complex", "Re": "complex", "Im": "complex", "pf": "complex",
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

BASIC_BUTTON_POSITIONS = {
    (1, 4): (1, 0, 1),  # sign
    (1, 2): (1, 1, 1),  # percent
    (2, 5): (1, 2, 1),  # pi
    (3, 6): (1, 3, 1),  # backspace
    (1, 0): (1, 4, 1),  # open parenthesis
    (1, 1): (1, 5, 1),  # close parenthesis
    (1, 3): (1, 6, 1),  # clear all
    (5, 5): (8, 5, 1),  # decimal point
    (2, 0): (5, 0, 1),  # square
    (2, 1): (5, 1, 1),  # cube
    (1, 6): (5, 2, 1),  # division
    (5, 0): (5, 3, 1),
    (5, 1): (5, 4, 1),
    (5, 2): (5, 5, 1),
    (5, 3): (5, 6, 1),
    (6, 4): (6, 0, 1),
    (6, 5): (6, 1, 1),
    (1, 5): (6, 2, 1),  # remainder
    (6, 0): (6, 3, 1),
    (6, 1): (6, 4, 1),
    (6, 2): (6, 5, 1),
    (6, 3): (6, 6, 1),
    (5, 4): (7, 0, 1),  # Euler's number
    (7, 4): (7, 1, 1),  # square root
    (7, 5): (7, 2, 1),  # cube root
    (7, 0): (7, 3, 1),
    (7, 1): (7, 4, 1),
    (7, 2): (7, 5, 1),
    (7, 3): (7, 6, 1),
    (8, 0): (8, 0, 5),
    (7, 6): (8, 6, 1),
}

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
    "AC": "tooltip_clear_all",
    "CE": "tooltip_clear_entry",
    "+/-": "tooltip_toggle_sign",
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


def scientific_button_group(label: str) -> str:
    if label.isdigit() or label in {".", "+", "-", "×", "="}:
        return "keypad"
    return SCIENTIFIC_BUTTON_GROUPS.get(label, "function")


def scientific_button_position(row: int, column: int, label: str) -> tuple[int, int, int]:
    return row, column, BUTTON_COLUMN_SPANS.get(label, 1)
