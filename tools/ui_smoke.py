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
        save_and_check_snapshot(window, output_dir / "compact.png")

        window._set_ai_panel_visible(True, resize_window=False)
        window.resize(1400, 920)
        app.processEvents()

        assert_true(window.ai_panel_visible, "assistant panel should open")
        assert_true(window.right_panel.isVisible(), "right panel should be visible when expanded")
        assert_true(window.assistant_query_panel.objectName() == "assistantQueryPanel", "assistant query panel missing")
        assert_true(window.ai_live_preview.parentWidget() == window.assistant_query_panel, "live preview should stay in query panel")
        assert_true(window.solve_button.icon().isNull(), "calculate action should not use a play icon")
        assert_true(window._tr("hide_ai_panel") in window.ai_toggle_button.text(), "expanded toggle should say hide AI")
        save_and_check_snapshot(window, output_dir / "expanded.png")

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
