# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math
import random
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from core.expression_parser import CalculatorError, ExpressionParser
from ui.button_config import BUTTON_INSERTIONS


def handle_button(window, label: str) -> None:
    if label == "2nd":
        window.second_mode = not window.second_mode
        window._refresh_mode_labels()
        return
    if label in {"Deg", "Rad"}:
        window.degrees = not window.degrees
        window._refresh_mode_labels()
        window._update_display()
        return
    if label == "AC":
        clear_all(window)
        return
    if label == "CE":
        window.expression = ""
        window.just_evaluated = False
        window._update_display()
        return
    if label == "⌫":
        window.expression = window.expression[:-1]
        window.just_evaluated = False
        window._update_display()
        return
    if label == "=":
        evaluate_expression(window)
        return
    if label == "+/-":
        toggle_sign(window)
        return
    if label == "%":
        apply_percent_input(window)
        return
    if label == "mc":
        window.memory = 0.0
        window._refresh_mode_labels()
        return
    if label == "mr":
        append_text(window, window._format_number(window.memory))
        return
    if label == "m+":
        window.memory += current_numeric_value(window)
        window._refresh_mode_labels()
        return
    if label == "m-":
        window.memory -= current_numeric_value(window)
        window._refresh_mode_labels()
        return
    if label == "ms":
        window.memory = current_numeric_value(window)
        window._refresh_mode_labels()
        return
    if label == "Ans":
        append_text(window, window.result_label.text())
        return
    if label == "Rand":
        window.result_label.setText(window._format_number(random.random()))
        window.preview_label.setText(window._tr("random_value"))
        return

    if label in BUTTON_INSERTIONS:
        append_text(window, BUTTON_INSERTIONS[label], label)
    else:
        append_text(window, label, label)


def append_text(window, text: str, source_label: str | None = None) -> None:
    if window.just_evaluated and (text[:1].isdigit() or source_label in {"π", "e", ".", "("}):
        window.expression = ""
    window.just_evaluated = False

    if window.expression and text in {"+", "-", "*", "/", "^", " mod "} and window.expression[-1] in "+-*/^":
        window.expression = window.expression[:-1] + text.strip()
        if text == " mod ":
            window.expression = window.expression[:-3] + text
    else:
        if needs_implicit_multiply(window, text, source_label):
            window.expression += "*"
        window.expression += text
    window._update_display()


def clear_all(window) -> None:
    window.expression = ""
    window.just_evaluated = False
    window.result_label.setText("0")
    window.preview_label.setText(window._tr("ready_input"))
    window._update_display()


def set_expression_and_evaluate(window, expression: str) -> None:
    window.expression = expression
    window.just_evaluated = False
    window._update_display()
    window._evaluate()


def toggle_sign(window) -> None:
    if not window.expression:
        window.expression = "-"
    elif window.expression.startswith("-"):
        window.expression = window.expression[1:]
    else:
        window.expression = f"-({window.expression})"
    window.just_evaluated = False
    window._update_display()


def evaluate_expression(window) -> None:
    try:
        expression = balanced_expression(window.expression)
        factorization = try_prime_factorization(window, expression)
        if factorization is not None:
            formatted = factorization
        else:
            result = ExpressionParser(expression, window.degrees).parse()
            if not is_finite_number(result):
                raise CalculatorError(window._tr("finite_number_required"))
            formatted = window._format_number(result)
        if not formatted:
            raise CalculatorError(window._tr("finite_number_required"))
        if factorization is None:
            window.expression = formatted
        window.result_label.setText(formatted)
        window.preview_label.setText(window._tr("result_confirmed"))
        window.just_evaluated = True
        push_history(window, expression, formatted)
        window._update_display()
    except (CalculatorError, OverflowError, ValueError) as exc:
        window.result_label.setText("ERROR")
        window.preview_label.setText(str(exc))


def update_display(window) -> None:
    window.expression_label.setText(window._pretty_expression(window.expression) or " ")
    if not window.expression:
        window.preview_label.setText(window._tr("ready_input"))
        window.result_label.setText("0")
        return
    try:
        expression = balanced_expression(window.expression)
        factorization = try_prime_factorization(window, expression)
        formatted = factorization
        if formatted is None:
            preview = ExpressionParser(expression, window.degrees).parse()
            if not is_finite_number(preview):
                raise CalculatorError(window._tr("finite_number_required"))
            formatted = window._format_number(preview)
        window.preview_label.setText(f"Live: {formatted}")
        window.result_label.setText(window.result_label.text() if window.just_evaluated else formatted)
    except (CalculatorError, OverflowError, ValueError):
        opens = window.expression.count("(") - window.expression.count(")")
        if opens > 0:
            window.preview_label.setText(window._tr("waiting_for_closing_parentheses").format(count=opens))
        else:
            window.preview_label.setText(window._tr("building_expression"))
        if not window.just_evaluated:
            window.result_label.setText("0")


def balanced_expression(text: str) -> str:
    opens = text.count("(") - text.count(")")
    if opens > 0:
        return text + (")" * opens)
    return text


def try_prime_factorization(window, expression: str) -> str | None:
    text = expression.strip()
    lowered = text.lower()
    if not (lowered.startswith("pf(") or lowered.startswith("factor(")) or not text.endswith(")"):
        return None
    inner = text[text.find("(") + 1:-1]
    value = ExpressionParser(inner, window.degrees).parse()
    return prime_factorization_text(window, value)


def prime_factorization_text(window, value: float | complex) -> str:
    if isinstance(value, complex):
        if abs(value.imag) > 1e-14:
            raise CalculatorError(window._tr("prime_factor_real_required"))
        value = value.real
    if value < 0:
        prefix = ["-1"]
        value = abs(value)
    else:
        prefix = []
    if not float(value).is_integer():
        raise CalculatorError(window._tr("prime_factor_integer_required"))
    n = int(value)
    if n in {0, 1}:
        return " × ".join(prefix + [str(n)]) if prefix else str(n)
    factors: list[str] = []
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.append(str(divisor))
            n //= divisor
        divisor += 1 if divisor == 2 else 2
    if n > 1:
        factors.append(str(n))
    return " × ".join(prefix + factors)


def is_finite_number(value: float | complex) -> bool:
    if isinstance(value, complex):
        return math.isfinite(value.real) and math.isfinite(value.imag)
    return math.isfinite(value)


def needs_implicit_multiply(window, text: str, source_label: str | None = None) -> bool:
    if not window.expression:
        return False
    prev = window.expression[-1]
    if prev in "+-*/^(. ":
        return False
    starts_group = source_label in {
        "π",
        "e",
        "(",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "sinh",
        "cosh",
        "tanh",
        "ln",
        "log",
        "sqrt",
        "cbrt",
        "1/x",
        "|x|",
        "x²",
        "x³",
        "e^x",
        "10^x",
        "Re",
        "Im",
        "pf",
    }
    return starts_group or text in {"(", "pi", "e", "i"}


def apply_percent_input(window) -> None:
    if not window.expression:
        return
    match = re.search(r"(pi|e|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)$", window.expression)
    if not match:
        append_text(window, "%", "%")
        return
    start, _ = match.span()
    current_text = match.group(0)
    head = window.expression[:start]
    try:
        current_value = ExpressionParser(current_text, window.degrees).parse()
    except (CalculatorError, ValueError, OverflowError):
        append_text(window, "%", "%")
        return
    operator_index, operator = last_top_level_operator(head)
    if operator in {"+", "-"} and operator_index is not None:
        base_expr = head[:operator_index]
        try:
            base_value = ExpressionParser(balanced_expression(base_expr), window.degrees).parse()
            percent_value = base_value * current_value / 100.0
        except (CalculatorError, ValueError, OverflowError):
            percent_value = current_value / 100.0
    else:
        percent_value = current_value / 100.0
    window.expression = head + window._format_number(percent_value)
    window.preview_label.setText(window._tr("percent_adjusted"))
    window._update_display()


def last_top_level_operator(text: str) -> tuple[int | None, str | None]:
    depth = 0
    last_index: int | None = None
    last_op: str | None = None
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and char in "+-*/^":
            if char in "+-" and (index == 0 or text[index - 1] in "+-*/^("):
                continue
            last_index = index
            last_op = char
    return last_index, last_op


def current_numeric_value(window) -> float:
    try:
        return float(window.result_label.text())
    except ValueError:
        return 0.0


def push_history(window, expression: str, result: str) -> None:
    window.history_items.insert(0, (expression, result))
    window.history_items = window.history_items[:20]
    if window.history_dialog is None:
        return
    window.history_dialog.history_list.clear()
    for expr, value in window.history_items:
        item = QListWidgetItem(f"{window._pretty_expression(expr)} = {value}")
        item.setData(Qt.UserRole, (expr, value))
        window.history_dialog.history_list.addItem(item)
    window.history_dialog.info_label.setText(f"{window._tr('last_calculation')}: {window._pretty_expression(expression)}")
