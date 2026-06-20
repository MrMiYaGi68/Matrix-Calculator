# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math
import cmath
from dataclasses import dataclass


class CalculatorError(Exception):
    pass


@dataclass
class Token:
    kind: str
    value: str


Number = float | complex


class ExpressionParser:
    MAX_DEPTH = 100
    MAX_FACTORIAL = 2000

    def __init__(self, text: str, degrees: bool):
        self.text = text
        self.degrees = degrees
        self.tokens = self._tokenize(text)
        self.index = 0
        self._depth = 0

    def parse(self) -> Number:
        if not self.tokens:
            raise CalculatorError("Leerer Ausdruck")
        self._depth = 0
        value = self._expression()
        if self._peek().kind != "EOF":
            raise CalculatorError("Ungültige Eingabe")
        return value

    def _tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        i = 0
        while i < len(text):
            char = text[i]
            if char.isspace():
                i += 1
                continue
            if char.isdigit() or char == ".":
                start = i
                dot_count = 0
                while i < len(text) and (text[i].isdigit() or text[i] == "."):
                    if text[i] == ".":
                        dot_count += 1
                    i += 1
                if dot_count > 1:
                    raise CalculatorError("Zu viele Dezimalpunkte")
                if i < len(text) and text[i] in "eE":
                    i += 1
                    if i < len(text) and text[i] in "+-":
                        i += 1
                    exp_start = i
                    while i < len(text) and text[i].isdigit():
                        i += 1
                    if exp_start == i:
                        raise CalculatorError("Ungültige Exponentialzahl")
                tokens.append(Token("NUMBER", text[start:i]))
                continue
            if char.isalpha() or char == "_":
                start = i
                while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                    i += 1
                tokens.append(Token("IDENT", text[start:i]))
                continue
            if text.startswith("**", i):
                tokens.append(Token("OP", "^"))
                i += 2
                continue
            if char in "+-*/^(),!%":
                kind = "OP" if char != "," else "COMMA"
                tokens.append(Token(kind, char))
                i += 1
                continue
            raise CalculatorError(f"Unbekanntes Zeichen: {char}")
        tokens.append(Token("EOF", ""))
        return tokens

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _match(self, *values: str) -> bool:
        token = self._peek()
        if token.value in values:
            self._advance()
            return True
        return False

    def _expression(self) -> Number:
        self._depth += 1
        if self._depth > self.MAX_DEPTH:
            raise CalculatorError("Ausdruck zu komplex (verschachtelt)")
        try:
            value = self._term()
            while self._peek().value in {"+", "-"}:
                operator = self._advance().value
                rhs = self._term()
                if operator == "+":
                    value += rhs
                else:
                    value -= rhs
            return value
        finally:
            self._depth -= 1

    def _term(self) -> Number:
        value = self._unary()
        while True:
            token = self._peek()
            if token.value == "*":
                self._advance()
                value *= self._unary()
            elif token.value == "/":
                self._advance()
                rhs = self._unary()
                if rhs == 0:
                    raise CalculatorError("Division durch 0")
                value /= rhs
            elif token.kind == "IDENT" and token.value.lower() == "mod":
                self._advance()
                rhs = self._unary()
                value = self._modulo(value, rhs)
            elif token.kind in {"NUMBER", "IDENT"} or token.value == "(":
                value *= self._unary()
            else:
                break
        return value

    def _power(self) -> Number:
        value = self._postfix()
        if self._match("^"):
            exponent = self._unary()
            value = value ** exponent
        return value

    def _unary(self) -> Number:
        if self._match("+"):
            return self._unary()
        if self._match("-"):
            return -self._unary()
        return self._power()

    def _postfix(self) -> Number:
        value = self._primary()
        while True:
            if self._match("!"):
                real_value = self._require_real(value, "Fakultät")
                if real_value < 0 or not float(real_value).is_integer():
                    raise CalculatorError("Fakultät nur für ganze Zahlen >= 0")
                if real_value > self.MAX_FACTORIAL:
                    raise CalculatorError(f"Fakultät zu groß (max {self.MAX_FACTORIAL})")
                value = math.factorial(int(real_value))
            elif self._match("%"):
                value /= 100.0
            else:
                return value

    def _primary(self) -> Number:
        token = self._peek()
        if token.kind == "NUMBER":
            self._advance()
            return float(token.value)
        if token.kind == "IDENT":
            name = self._advance().value
            if self._match("("):
                value = self._expression()
                if not self._match(")"):
                    raise CalculatorError("Schließende Klammer fehlt")
                return self._call_function(name, value)
            return self._constant(name)
        if self._match("("):
            value = self._expression()
            if not self._match(")"):
                raise CalculatorError("Schließende Klammer fehlt")
            return value
        raise CalculatorError("Ausdruck unvollständig")

    def _constant(self, name: str) -> Number:
        constants = {"pi": math.pi, "e": math.e}
        lowered = name.lower()
        if lowered in {"i", "j"}:
            return 1j
        if lowered in constants:
            return constants[lowered]
        raise CalculatorError(f"Unbekannte Konstante: {name}")

    def _call_function(self, name: str, value: Number) -> Number:
        lowered = name.lower()
        angle_value = self._require_real(value, name) if lowered in {"sin", "cos", "tan"} and self.degrees else value
        angle = math.radians(angle_value) if self.degrees and lowered in {"sin", "cos", "tan"} else angle_value
        if lowered == "sin":
            return self._clean_complex(cmath.sin(angle))
        if lowered == "cos":
            return self._clean_complex(cmath.cos(angle))
        if lowered == "tan":
            return self._clean_complex(cmath.tan(angle))
        if lowered == "asin":
            result = cmath.asin(value)
            return self._angle_result(result)
        if lowered == "acos":
            result = cmath.acos(value)
            return self._angle_result(result)
        if lowered == "atan":
            result = cmath.atan(value)
            return self._angle_result(result)
        if lowered == "sinh":
            return self._clean_complex(cmath.sinh(value))
        if lowered == "cosh":
            return self._clean_complex(cmath.cosh(value))
        if lowered == "tanh":
            return self._clean_complex(cmath.tanh(value))
        if lowered == "asinh":
            return self._clean_complex(cmath.asinh(value))
        if lowered == "acosh":
            return self._clean_complex(cmath.acosh(value))
        if lowered == "atanh":
            return self._clean_complex(cmath.atanh(value))
        if lowered == "ln":
            return self._clean_complex(cmath.log(value))
        if lowered == "log":
            return self._clean_complex(cmath.log10(value))
        if lowered == "sqrt":
            return self._clean_complex(cmath.sqrt(value))
        if lowered == "cbrt":
            value = self._require_real(value, name)
            return math.copysign(abs(value) ** (1 / 3), value)
        if lowered == "square":
            return value * value
        if lowered == "cube":
            return value * value * value
        if lowered == "inv":
            if value == 0:
                raise CalculatorError("Division durch 0")
            return 1 / value
        if lowered == "abs":
            return abs(value)
        if lowered in {"real", "re"}:
            return value.real if isinstance(value, complex) else value
        if lowered in {"imag", "im"}:
            return value.imag if isinstance(value, complex) else 0.0
        if lowered == "arg":
            result = cmath.phase(value)
            return math.degrees(result) if self.degrees else result
        if lowered == "conj":
            return value.conjugate() if isinstance(value, complex) else value
        if lowered == "exp":
            return self._clean_complex(cmath.exp(value))
        if lowered == "pow10":
            return self._clean_complex(10 ** value)
        raise CalculatorError(f"Unbekannte Funktion: {name}")

    def _modulo(self, lhs: Number, rhs: Number) -> float:
        left = self._require_real(lhs, "Modulo")
        right = self._require_real(rhs, "Modulo")
        if right == 0:
            raise CalculatorError("Modulo durch 0")
        return math.fmod(left, right)

    def _require_real(self, value: Number, context: str) -> float:
        if isinstance(value, complex):
            if abs(value.imag) > 1e-14:
                raise CalculatorError(f"{context} braucht einen reellen Wert")
            return value.real
        return value

    def _clean_complex(self, value: Number) -> Number:
        if isinstance(value, complex):
            real = 0.0 if abs(value.real) < 1e-14 else value.real
            imag = 0.0 if abs(value.imag) < 1e-14 else value.imag
            if imag == 0:
                return real
            return complex(real, imag)
        return value

    def _angle_result(self, value: Number) -> Number:
        if not self.degrees:
            return self._clean_complex(value)
        return self._clean_complex(value * (180 / math.pi))
