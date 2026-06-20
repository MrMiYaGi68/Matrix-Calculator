# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication


def toggle_ai_panel(window) -> None:
    set_ai_panel_visible(window, not window.ai_panel_visible, resize_window=True)


def handle_change_event(window, event_type) -> None:
    if event_type == window.QEVENT_WINDOW_STATE_CHANGE and not window.ai_panel_visible:
        QTimer.singleShot(0, window._enforce_collapsed_window_state)
        QTimer.singleShot(50, window._enforce_collapsed_window_state)


def set_ai_panel_visible(window, visible: bool, resize_window: bool = True) -> None:
    if visible == window.ai_panel_visible:
        if hasattr(window, "header_settings_button"):
            window.header_settings_button.setVisible(not visible)
        return
    if not visible:
        sizes = window.content_splitter.sizes()
        if len(sizes) == 2 and sizes[1] > 0:
            window._last_ai_splitter_sizes = sizes
            window._last_ai_panel_width = max(sizes[1], window.right_panel.width(), window.DEFAULT_AI_PANEL_WIDTH)
    window.ai_panel_visible = visible
    if visible:
        set_maximize_available(window, True)
        available = current_screen_available_geometry(window)
        target_width = window.EXPANDED_WINDOW_WIDTH
        if available is not None:
            target_width = min(target_width, available_content_window_width(window, available))
        expanded_minimum = min(window.EXPANDED_MINIMUM_WIDTH, target_width)
        window.setMinimumSize(expanded_minimum, window.WINDOW_MINIMUM_HEIGHT)
        window.setMaximumSize(16777215, 16777215)
        window.content_splitter.setMinimumWidth(0)
        window.content_splitter.setMaximumWidth(16777215)
        window.left_panel.setMaximumWidth(16777215)
        window.content_splitter.setHandleWidth(window.SPLITTER_HANDLE_WIDTH)
        window.right_panel.setMinimumWidth(window.RIGHT_PANEL_MINIMUM_WIDTH)
        window.right_panel.setMaximumWidth(16777215)
        window.right_panel.setVisible(True)
        if resize_window and not window.isMaximized() and not window.isFullScreen():
            resize_and_center(window, target_width, window.height())
        window.content_splitter.setSizes(last_expanded_splitter_sizes(window))
        window.ai_input.setFocus()
        if resize_window:
            fit_window_to_available_screen(window)
            QTimer.singleShot(0, window._fit_window_to_available_screen)
            QTimer.singleShot(50, window._fit_window_to_available_screen)
            QTimer.singleShot(150, window._fit_window_to_available_screen)
    else:
        collapsed_content = collapsed_content_width(window)
        if resize_window and (window.isMaximized() or window.isFullScreen()):
            window.showNormal()
        set_maximize_available(window, False)
        window.content_splitter.setMinimumWidth(collapsed_content)
        window.content_splitter.setMaximumWidth(collapsed_content)
        window.left_panel.setMaximumWidth(collapsed_content)
        window.content_splitter.setHandleWidth(0)
        window.right_panel.setMinimumWidth(0)
        window.right_panel.setMaximumWidth(0)
        window.right_panel.setVisible(False)
        window.setFixedSize(window.COLLAPSED_WINDOW_WIDTH, collapsed_window_height(window))
        if resize_window and not window.isMaximized() and not window.isFullScreen():
            resize_and_center(window, window.COLLAPSED_WINDOW_WIDTH, collapsed_window_height(window))
        window.content_splitter.setSizes([collapsed_content, 0])
        if resize_window:
            fit_window_to_available_screen(window)
            QTimer.singleShot(0, window._fit_window_to_available_screen)
            QTimer.singleShot(50, window._fit_window_to_available_screen)
            QTimer.singleShot(150, window._fit_window_to_available_screen)
    if hasattr(window, "header_settings_button"):
        window.header_settings_button.setVisible(not window.ai_panel_visible)
    refresh_ai_toggle_button(window)


def set_maximize_available(window, available: bool) -> None:
    flags = window.windowFlags()
    next_flags = (
        Qt.Window
        | Qt.CustomizeWindowHint
        | Qt.WindowTitleHint
        | Qt.WindowSystemMenuHint
        | Qt.WindowMinimizeButtonHint
        | Qt.WindowCloseButtonHint
    )
    if available:
        next_flags |= Qt.WindowMaximizeButtonHint
    else:
        next_flags |= Qt.MSWindowsFixedSizeDialogHint
    if next_flags == flags:
        return
    was_visible = window.isVisible()
    window.setWindowFlags(next_flags)
    if was_visible:
        window.show()


def enforce_collapsed_window_state(window) -> None:
    if window.ai_panel_visible:
        return
    if window.isMaximized() or window.isFullScreen():
        window.showNormal()
        QTimer.singleShot(0, window._enforce_collapsed_window_width)
        QTimer.singleShot(50, window._enforce_collapsed_window_width)
        return
    enforce_collapsed_window_width(window)


def enforce_collapsed_window_width(window) -> None:
    if window.ai_panel_visible or window.isMaximized() or window.isFullScreen():
        return
    if window.width() != window.COLLAPSED_WINDOW_WIDTH:
        resize_and_center(window, window.COLLAPSED_WINDOW_WIDTH, collapsed_window_height(window))


def collapsed_content_width(window) -> int:
    return window.COLLAPSED_WINDOW_WIDTH - window.OUTER_HORIZONTAL_MARGIN


def collapsed_window_height(window) -> int:
    available = current_screen_available_geometry(window)
    if available is None:
        return window.COLLAPSED_WINDOW_HEIGHT
    return min(window.COLLAPSED_WINDOW_HEIGHT, available.height())


def expanded_splitter_sizes(window) -> list[int]:
    return [window.LEFT_PANEL_WIDTH, window.DEFAULT_AI_PANEL_WIDTH]


def last_expanded_splitter_sizes(window) -> list[int]:
    sizes = getattr(window, "_last_ai_splitter_sizes", expanded_splitter_sizes(window))
    if len(sizes) != 2 or sizes[0] <= 0 or sizes[1] <= 0:
        return expanded_splitter_sizes(window)
    return sizes


def refresh_ai_toggle_button(window) -> None:
    if not hasattr(window, "ai_toggle_button"):
        return
    text_key = "hide_ai_panel" if window.ai_panel_visible else "show_ai_panel"
    tooltip_key = "hide_ai_panel_tooltip" if window.ai_panel_visible else "show_ai_panel_tooltip"
    prefix = "◀" if window.ai_panel_visible else "▶"
    available_width = window.left_panel.width() if hasattr(window, "left_panel") else 0
    if available_width and available_width < 760:
        button_text = prefix
    elif available_width and available_width < 920:
        button_text = f"{prefix} KI"
    else:
        button_text = f"{prefix} {window._tr(text_key)}"
    window.ai_toggle_button.setText(button_text)
    window.ai_toggle_button.setToolTip(window._tr(tooltip_key))
    window.ai_toggle_button.setProperty("assistantVisible", window.ai_panel_visible)
    window.ai_toggle_button.style().unpolish(window.ai_toggle_button)
    window.ai_toggle_button.style().polish(window.ai_toggle_button)


def current_screen_available_geometry(window):
    screen = window.screen() or QApplication.primaryScreen()
    if screen is None:
        return None
    return screen.availableGeometry()


def resize_and_center(window, width: int, height: int) -> None:
    available = current_screen_available_geometry(window)
    if available is None:
        window.resize(width, height)
        return
    target_width = min(width, available_content_window_width(window, available))
    target_height = min(height, available.height())
    x = available.x() + max(window.SCREEN_EDGE_MARGIN, (available.width() - target_width) // 2)
    y = available.y() + max(0, (available.height() - target_height) // 2)
    window.resize(target_width, target_height)
    window.move(x, y)


def fit_window_to_available_screen(window) -> None:
    if window.isMaximized() or window.isFullScreen():
        return
    screen = window.screen() or QApplication.primaryScreen()
    if screen is None:
        return
    available = screen.availableGeometry()
    frame = window.frameGeometry()
    max_frame_width = max(1, available.width() - window.SCREEN_EDGE_MARGIN * 2)
    if frame.width() > max_frame_width:
        excess = frame.width() - max_frame_width
        window.resize(max(1, window.width() - excess), min(window.height(), available.height()))
        frame = window.frameGeometry()

    x = available.x() + max(window.SCREEN_EDGE_MARGIN, (available.width() - frame.width()) // 2)
    if frame.right() > available.right() - window.SCREEN_EDGE_MARGIN:
        x -= frame.right() - (available.right() - window.SCREEN_EDGE_MARGIN)
    if x < available.x() + window.SCREEN_EDGE_MARGIN:
        x = available.x() + window.SCREEN_EDGE_MARGIN
    y = available.y() + max(0, (available.height() - frame.height()) // 2)
    window.move(x, y)


def available_content_window_width(window, available) -> int:
    margin = window.SCREEN_EDGE_MARGIN * 2 + window.WINDOW_FRAME_SAFETY_MARGIN
    return max(window.COLLAPSED_WINDOW_WIDTH, available.width() - margin)
