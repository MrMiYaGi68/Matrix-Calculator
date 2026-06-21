# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from functools import lru_cache
from math import cos, pi, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


@lru_cache(maxsize=64)
def line_icon(name: str, color: str, size: int = 24) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(size / 24.0, size / 24.0)
    pen = QPen(QColor(color), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    if name == "settings":
        painter.drawEllipse(QPointF(12, 12), 3.2, 3.2)
        painter.drawEllipse(QPointF(12, 12), 7.0, 7.0)
        for index in range(8):
            angle = index * pi / 4
            painter.drawLine(
                QPointF(12 + cos(angle) * 7.2, 12 + sin(angle) * 7.2),
                QPointF(12 + cos(angle) * 9.0, 12 + sin(angle) * 9.0),
            )
    elif name == "history":
        painter.drawEllipse(QPointF(12, 12), 8.0, 8.0)
        painter.drawLine(QPointF(12, 12), QPointF(12, 7.5))
        painter.drawLine(QPointF(12, 12), QPointF(15.5, 14))
    elif name == "chat":
        painter.drawRoundedRect(QRectF(3.5, 4.5, 17, 13), 3, 3)
        path = QPainterPath(QPointF(8, 17.5))
        path.lineTo(QPointF(6.5, 20))
        path.lineTo(QPointF(11, 17.5))
        painter.drawPath(path)
    elif name == "trash":
        painter.drawRoundedRect(QRectF(6.5, 7, 11, 13), 1.5, 1.5)
        painter.drawLine(QPointF(5, 7), QPointF(19, 7))
        painter.drawLine(QPointF(9, 4.5), QPointF(15, 4.5))
        painter.drawLine(QPointF(10, 10), QPointF(10, 17))
        painter.drawLine(QPointF(14, 10), QPointF(14, 17))
    elif name == "backspace":
        path = QPainterPath(QPointF(3.5, 12))
        path.lineTo(QPointF(8.5, 6))
        path.lineTo(QPointF(20.5, 6))
        path.lineTo(QPointF(20.5, 18))
        path.lineTo(QPointF(8.5, 18))
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(QPointF(12, 9.5), QPointF(16.5, 14.5))
        painter.drawLine(QPointF(16.5, 9.5), QPointF(12, 14.5))

    painter.end()
    return QIcon(pixmap)


def apply_window_icons(window) -> None:
    color = window._theme_palette()["soft_text"]
    icon_specs = (
        ("header_settings_button", "settings", 18),
        ("history_button", "history", 16),
        ("settings_button", "settings", 16),
        ("chatgpt_web_button", "chat", 16),
        ("clear_ai_button", "trash", 16),
    )
    for attribute, icon_name, size in icon_specs:
        button = getattr(window, attribute, None)
        if button is not None:
            button.setIcon(line_icon(icon_name, color, size))

    for button in getattr(window, "all_calc_buttons", []):
        if button.property("baseLabel") == "⌫":
            button.setIcon(line_icon("backspace", color, 20))
