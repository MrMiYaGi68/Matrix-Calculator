# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import html
import re


_LINK_PATTERN = re.compile(r"(https://[^\s<]+)")
_CHATGPT_QUERY_PATTERN = re.compile(r"https://chatgpt\.com/\?q=[^<\s]+")
_TASK_RECOGNIZED_LINES = {"Aufgabe erkannt", "Task recognized"}
_EXPLANATION_LABELS = {"Erklärung", "Vorgehen", "Explanation", "Method"}


def format_rich_text_block(
    text: str,
    *,
    body_bg: str = "#1c222b",
    text_color: str = "#e8edf5",
    link_color: str = "#9dc1ff",
) -> str:
    safe = html.escape(text)
    safe = _LINK_PATTERN.sub(
        lambda match: f'<a href="{match.group(1)}" style="color:{link_color}; text-decoration:none; font-weight:600;">{match.group(1)}</a>',
        safe,
    )
    return (
        f"<html><body style=\"font-family:'DejaVu Sans', 'Noto Sans', sans-serif; font-size:14px; line-height:1.5; color:{text_color}; background:{body_bg};\">"
        + safe.replace("\n", "<br>")
        + "</body></html>"
    )


def format_ai_message_html(role: str, text: str, colors: dict[str, str] | None = None) -> str:
    palette = {
        "link": "#9dc1ff",
        "note_bg": "#24313c",
        "note_fg": "#cfe7ff",
        "section_bg": "#1f252d",
        "section_border": "#313844",
        "section_label": "#90a0b2",
        "section_fg": "#f6f8fb",
        "explanation_bg": "#232a33",
        "explanation_border": "#323a46",
        "explanation_label": "#9fb0c3",
        "explanation_fg": "#edf1f5",
        "plain_fg": "#edf1f5",
    }
    if colors:
        palette.update(colors)
    if role == "system":
        safe = html.escape(text).replace("\n", "<br>")
        return _CHATGPT_QUERY_PATTERN.sub(
            lambda match: f'<a href="{match.group(0)}" style="color:{palette["link"]}; text-decoration:none; font-weight:600;">Frag bitte ChatGPT</a>',
            safe,
        )
    if role != "assistant":
        return html.escape(text).replace("\n", "<br>")

    lines = text.splitlines()
    blocks: list[str] = []
    note = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line in _TASK_RECOGNIZED_LINES:
            note = """
            <div style="
              display:inline-block;
              margin-bottom:10px;
              padding:6px 10px;
              border-radius:999px;
              background:%s;
              color:%s;
              font-size:12px;
              font-weight:600;
            ">Aufgabe erkannt</div>
            """ % (palette["note_bg"], palette["note_fg"])
            i += 1
            continue
        if ":" in line:
            label, value = line.split(":", 1)
            label = html.escape(label.strip())
            value = html.escape(value.strip())
            if label in _EXPLANATION_LABELS:
                blocks.append(
                    f"""
                    <div style="
                      margin-top:10px;
                      padding:12px 14px;
                      border-radius:14px;
                      background:{palette["explanation_bg"]};
                      border:1px solid {palette["explanation_border"]};
                    ">
                      <div style="font-size:12px; text-transform:uppercase; letter-spacing:0.08em; color:{palette["explanation_label"]}; margin-bottom:6px;">{label}</div>
                      <div style="font-size:15px; line-height:1.5; color:{palette["explanation_fg"]};">{value}</div>
                    </div>
                    """
                )
            else:
                blocks.append(
                    f"""
                    <div style="
                      margin-top:8px;
                      padding:12px 14px;
                      border-radius:14px;
                      background:{palette["section_bg"]};
                      border:1px solid {palette["section_border"]};
                    ">
                      <div style="font-size:12px; text-transform:uppercase; letter-spacing:0.08em; color:{palette["section_label"]}; margin-bottom:6px;">{label}</div>
                      <div style="font-size:{'24px' if label == 'Ergebnis' else '16px'}; line-height:1.4; color:{palette["section_fg"]}; font-weight:{'700' if label == 'Ergebnis' else '500'};">{value}</div>
                    </div>
                    """
                )
        else:
            blocks.append(f"<div style='font-size:15px; line-height:1.5; color:{palette['plain_fg']};'>{html.escape(line)}</div>")
        i += 1
    return note + "".join(blocks)


def render_ai_chat_html(
    messages: list[tuple[str, str]],
    labels: dict[str, tuple[str, str, str, str]],
    *,
    body_background: str = "#1c222b",
    rich_text_colors: dict[str, str] | None = None,
) -> str:
    blocks: list[str] = []
    for role, text in messages:
        title, bg, fg, align = labels.get(role, labels["fallback"])
        safe_text = format_ai_message_html(role, text, rich_text_colors)
        blocks.append(
            f"""
            <div style="margin: 8px 0 12px 0; text-align:{align};">
              <div style="
                display:inline-block;
                max-width:86%;
                background:{bg};
                color:{fg};
                border-radius:20px;
                padding:12px 14px;
                box-shadow: 0 10px 24px rgba(0,0,0,0.18);
                text-align:left;
                font-size:16px;
                line-height:1.45;
              ">
                <div style="font-size:12px; opacity:0.74; margin-bottom:8px;">{title}</div>
                <div>{safe_text}</div>
              </div>
            </div>
            """
        )
    return (
        f"""
        <html>
          <body style="background:{body_background}; font-family:'DejaVu Sans', 'Noto Sans', sans-serif; margin:0; padding:10px;">
        """
        + "".join(blocks)
        + """
          </body>
        </html>
        """
    )
