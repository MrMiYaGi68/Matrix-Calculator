# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTextEdit


class QueryInput(QTextEdit):
    returnPressed = Signal()
    textChangedValue = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.textChanged.connect(self._emit_text_changed)
        self.setAcceptRichText(False)

    def _emit_text_changed(self) -> None:
        self.textChangedValue.emit(self.text())

    def text(self) -> str:
        return self.toPlainText()

    def setText(self, value: str) -> None:
        self.setPlainText(value)

    def setCursorPosition(self, position: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(max(0, min(position, len(self.text()))))
        self.setTextCursor(cursor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in {Qt.Key_Return, Qt.Key_Enter} and not (event.modifiers() & Qt.ShiftModifier):
            self.returnPressed.emit()
            event.accept()
            return
        super().keyPressEvent(event)
