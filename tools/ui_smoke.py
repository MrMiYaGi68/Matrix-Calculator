#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTHONPYCACHEPREFIX", "/tmp/matrix-calculator-pycache")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from calculator import MatrixCalculatorWindow  # noqa: E402


GENERIC_FONT_FAMILIES = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui"}


def fail(message: str) -> None:
    raise AssertionError(message)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def rich_text_font_families(text: str) -> list[list[str]]:
    families: list[list[str]] = []
    for match in re.finditer(r"font-family\s*:\s*([^;\"']+(?:['\"][^'\"]+['\"][^;\"']*)*)", text, flags=re.I):
        stack = [part.strip().strip("'\"").lower() for part in match.group(1).split(",")]
        families.append([font for font in stack if font])
    return families


def assert_no_single_rich_text_font_stacks() -> None:
    files = [
        PROJECT_ROOT / "calculator.py",
        PROJECT_ROOT / "core" / "i18n.py",
        PROJECT_ROOT / "ui" / "assistant_rendering.py",
    ]
    offenders: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for stack in rich_text_font_families(text):
            named_fonts = [font for font in stack if font not in GENERIC_FONT_FAMILIES]
            if len(named_fonts) < 2 and "dejavu sans" in named_fonts:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {', '.join(stack)}")
    assert_true(not offenders, "single rich-text font stack found: " + "; ".join(offenders))


def save_and_check_snapshot(window: MatrixCalculatorWindow, path: Path) -> None:
    pixmap = window.grab()
    assert_true(not pixmap.isNull(), f"snapshot is null: {path}")
    assert_true(pixmap.width() >= 600 and pixmap.height() >= 700, f"unexpected snapshot size: {pixmap.size()}")
    assert_true(pixmap.save(str(path)), f"could not save snapshot: {path}")

    image = pixmap.toImage()
    sample_colors: set[int] = set()
    x_step = max(1, image.width() // 12)
    y_step = max(1, image.height() // 12)
    for x in range(0, image.width(), x_step):
        for y in range(0, image.height(), y_step):
            sample_colors.add(image.pixelColor(x, y).rgba())
    assert_true(len(sample_colors) >= 4, f"snapshot looks blank or flat: {path}")


def run_smoke(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    window = MatrixCalculatorWindow()
    try:
        window.show()
        app.processEvents()

        assert_true(not window.ai_panel_visible, "calculator should start collapsed")
        assert_true(not window.right_panel.isVisible(), "right panel should be hidden in compact mode")
        assert_true("KI" in window.ai_toggle_button.text(), "AI toggle label should remain visible")
        basic_positions = {}
        for index in range(window.controls_grid.count()):
            item = window.controls_grid.itemAt(index)
            button = item.widget()
            if button is None or not button.isVisible():
                continue
            basic_positions[button.property("baseLabel")] = window.controls_grid.getItemPosition(index)
        assert_true(
            basic_positions["0"] == (8, 0, 1, 5),
            "zero should fill the bottom row up to the decimal key",
        )
        assert_true(basic_positions["."] == (8, 5, 1, 1), "decimal should sit beside zero")
        assert_true(basic_positions["="] == (8, 6, 1, 1), "equals should finish the operator column")
        assert_true(basic_positions["AC"] == (1, 6, 1, 1), "AC should end the top row")
        assert_true(basic_positions["×"] == (5, 6, 1, 1), "multiply should end the first number row")
        assert_true(basic_positions["-"] == (6, 6, 1, 1), "minus should end the second number row")
        assert_true(basic_positions["+"] == (7, 6, 1, 1), "plus should end the third number row")
        assert_true(basic_positions["7"] == (5, 3, 1, 1), "number pad should follow the left utility block")
        assert_true(basic_positions["3"] == (7, 5, 1, 1), "number pad should stop before the operator column")
        assert_true(basic_positions["⌫"] == (1, 3, 1, 1), "backspace should stay with entry controls")
        assert_true(basic_positions["π"] == (1, 2, 1, 1), "pi should replace clear entry")
        assert_true(basic_positions["x²"] == (5, 0, 1, 1), "square should use one helper column")
        assert_true(basic_positions["x³"] == (5, 1, 1, 1), "cube should sit beside square")
        assert_true("CE" not in basic_positions, "clear entry should be hidden in basic mode")
        assert_true("Ans" not in basic_positions, "answer should be hidden in basic mode")
        assert_true(basic_positions["mod"] == (6, 2, 1, 1), "remainder should stay with function helpers")
        ac_button = next(button for button in window.all_calc_buttons if button.property("baseLabel") == "AC")
        assert_true(bool(ac_button.focusPolicy() & Qt.TabFocus), "calculator buttons should accept keyboard focus")
        save_and_check_snapshot(window, output_dir / "compact.png")

        for theme_name, file_name in (
            ("matrix", "compact-matrix.png"),
            ("light", "compact-light.png"),
            ("high contrast", "compact-high-contrast.png"),
        ):
            window.theme_name = theme_name
            window._apply_styles()
            app.processEvents()
            save_and_check_snapshot(window, output_dir / file_name)
        window.theme_name = "graphite"
        window._apply_styles()
        app.processEvents()

        window._set_layout_mode(True)
        app.processEvents()
        assert_true(window.left_panel.property("scientific"), "scientific styling state should be active")
        assert_true(
            all(button.isVisible() for button in window.all_calc_buttons),
            "scientific mode should keep every calculator function visible",
        )
        save_and_check_snapshot(window, output_dir / "scientific.png")
        window._set_layout_mode(False)
        app.processEvents()

        window._set_ai_panel_visible(True, resize_window=False)
        window.resize(1400, 920)
        app.processEvents()

        assert_true(window.ai_panel_visible, "assistant panel should open")
        assert_true(window.right_panel.isVisible(), "right panel should be visible when expanded")
        assert_true(window.assistant_query_panel.objectName() == "assistantQueryPanel", "assistant query panel missing")
        assert_true(window.ai_live_preview.parentWidget() == window.assistant_query_panel, "live preview should stay in query panel")
        assert_true(window.assistant_context.objectName() == "assistantContext", "assistant calculation context missing")
        assert_true(window._tr("current_calculation") in window.assistant_context.text(), "assistant context label missing")
        assert_true(window.assistant_examples.isVisible(), "assistant examples should guide the empty state")
        assert_true(not window.ai_result.isVisible(), "empty assistant output should not occupy the panel")
        assert_true(len(window.assistant_example_buttons) == 3, "assistant should show three examples")
        assert_true(window.solve_button.icon().isNull(), "calculate action should not use a play icon")
        assert_true(window._tr("hide_ai_panel") in window.ai_toggle_button.text(), "expanded toggle should say hide AI")
        save_and_check_snapshot(window, output_dir / "expanded.png")

        for theme_name, file_name in (
            ("matrix", "expanded-matrix.png"),
            ("light", "expanded-light.png"),
            ("high contrast", "expanded-high-contrast.png"),
        ):
            window.theme_name = theme_name
            window._apply_styles()
            window._render_ai_chat()
            app.processEvents()
            save_and_check_snapshot(window, output_dir / file_name)
        window.theme_name = "graphite"
        window._apply_styles()
        window._render_ai_chat()
        app.processEvents()

        window.expression = "1/0"
        window._evaluate()
        app.processEvents()
        assert_true(window.result_label.text() == "ERROR", "invalid expression should show ERROR")
        assert_true(window.preview_label.property("state") == "error", "invalid expression should mark preview as error")

        window._clear_all()
        app.processEvents()
        assert_true(window.result_label.text() == "0", "clear should reset result")
        assert_true(window.preview_label.property("state") == "neutral", "clear should reset preview state")

        about_html = window._about_html()
        assert_true("'Noto Sans'" in about_html and "sans-serif" in about_html, "about page should use a fallback font stack")
        assert_no_single_rich_text_font_stacks()
    finally:
        window.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Matrix Calculator UI smoke checks.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "matrix-calculator-ui-smoke",
        help="Directory for compact and expanded smoke snapshots.",
    )
    args = parser.parse_args()
    try:
        run_smoke(args.output_dir)
    except Exception as exc:
        print(f"UI smoke failed: {exc}", file=sys.stderr)
        return 1
    print(f"UI smoke OK: snapshots in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
