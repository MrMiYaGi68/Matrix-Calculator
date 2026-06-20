# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AppSettings:
    openai_model: str
    assistant_mode: str
    app_language: str
    ai_step_by_step: bool
    ai_use_context: bool
    theme_name: str


class SettingsStore:
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(data, dict):
            return {}
        changed = False
        if "openai_api_key" in data:
            data.pop("openai_api_key", None)
            changed = True
        if changed:
            self.write_raw(data)
        else:
            self._harden_permissions()
        return data

    def write(self, settings: AppSettings) -> None:
        self.write_raw(
            {
                "openai_model": settings.openai_model,
                "assistant_mode": settings.assistant_mode,
                "app_language": settings.app_language,
                "ai_step_by_step": settings.ai_step_by_step,
                "ai_use_context": settings.ai_use_context,
                "theme_name": settings.theme_name,
            }
        )

    def write_raw(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._harden_permissions()

    def session_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    def _harden_permissions(self) -> None:
        if self.path.exists():
            self.path.chmod(0o600)
