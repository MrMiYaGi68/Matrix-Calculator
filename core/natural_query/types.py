from __future__ import annotations

from dataclasses import dataclass


CLARIFICATION_EXPRESSION = "__clarification__"


@dataclass(frozen=True)
class NaturalQueryResult:
    expression: str
    answer: str
    explanation: str

    def as_tuple(self) -> tuple[str, str, str]:
        return self.expression, self.answer, self.explanation
