# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
import re


AUTO_OPENAI_MODEL_FALLBACK = "gpt-5-mini"
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def normalize_openai_model(model: object) -> str:
    aliases = {
        "gpt-5.4-mini": AUTO_OPENAI_MODEL_FALLBACK,
        "gpt-5.4": "gpt-5.1",
        "gpt-5.2": "gpt-5.2",
        "gpt-5.1": "gpt-5.1",
        "gpt-5": "gpt-5",
        "gpt-5-mini": "gpt-5-mini",
    }
    text = model.strip() if isinstance(model, str) else ""
    normalized = aliases.get(text, "")
    return normalized or AUTO_OPENAI_MODEL_FALLBACK


def choose_auto_openai_model(available_models: list[str]) -> str:
    preferred_exact = [model for model in available_models if re.fullmatch(r"gpt-5(?:\.\d+)?", model)]
    if preferred_exact:

        def version_key(model: str) -> tuple[int, ...]:
            suffix = model.removeprefix("gpt-5")
            if not suffix:
                return (0,)
            parts = suffix.removeprefix(".").split(".")
            return tuple(int(part) for part in parts if part.isdigit())

        return sorted(preferred_exact, key=version_key, reverse=True)[0]
    for candidate in ["gpt-5-mini", "gpt-5.1-chat-latest", "gpt-5-chat-latest"]:
        if candidate in available_models:
            return candidate
    return AUTO_OPENAI_MODEL_FALLBACK


def openai_api_help_text() -> str:
    return (
        "Warum braucht die App einen API-Key?\n"
        "Diese App spricht die OpenAI-API direkt an, damit sie ChatGPT-ähnliche Online-Antworten "
        "innerhalb des Rechners abrufen kann. Dafür muss OpenAI erkennen, welches Projekt die Anfrage "
        "stellt, welches Modell verwendet wird und über welches Projekt Guthaben, Limits und Abrechnung laufen. "
        "Ein normaler ChatGPT-Login oder ein ChatGPT-Abo allein reicht dafür nicht.\n\n"
        "Schritt für Schritt:\n"
        "1. Öffne https://platform.openai.com/ und melde dich mit deinem OpenAI-Konto an.\n"
        "2. Öffne danach direkt https://platform.openai.com/api-keys .\n"
        "3. Wähle oben das richtige Projekt aus, falls du mehrere Projekte hast.\n"
        "4. Erstelle einen neuen Secret Key.\n"
        "5. Kopiere den Key sofort. Er wird später nicht mehr vollständig angezeigt.\n"
        "6. Setze den Key bevorzugt als Umgebungsvariable OPENAI_API_KEY oder gib ihn nur für die aktuelle App-Sitzung ein.\n"
        "7. Klicke danach auf \"Teste die API!\", damit du sofort siehst, ob Schlüssel, Projekt und Billing funktionieren.\n\n"
        "Wichtig:\n"
        "- API-Keys sind geheim. Teile sie nicht mit anderen.\n"
        "- Die App speichert API-Keys nicht dauerhaft in settings.json.\n"
        "- API-Nutzung und ChatGPT-App/Website sind getrennte Produkte.\n"
        "- Wenn der Test 429 oder \"insufficient_quota\" meldet, ist der Key meist erkannt, aber dem Projekt fehlen Guthaben oder Limits.\n"
        "- API-Key Hilfe: https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key?LanguageId=1\n"
        "- Billing / Credits: https://platform.openai.com/settings/organization/billing/credit-grants\n"
        "- Usage Dashboard: https://platform.openai.com/usage\n"
        "- Limits Hilfe: https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits"
    )


def build_openai_request_headers(api_key: str) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    organization = os.getenv("OPENAI_ORGANIZATION", "").strip()
    project = os.getenv("OPENAI_PROJECT", "").strip()
    if organization:
        headers["OpenAI-Organization"] = organization
    if project:
        headers["OpenAI-Project"] = project
    return headers


def extract_openai_output_text(data: dict) -> str:
    output_text = data.get("output_text")
    if output_text:
        return output_text.strip()
    output = data.get("output", [])
    texts: list[str] = []
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                texts.append(text)
    return "\n".join(texts).strip()


def describe_openai_api_error(status_code: int | None, payload: dict | None = None) -> str:
    payload = payload or {}
    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    code = str(error.get("code") or "").strip()
    message = str(error.get("message") or "").strip()

    if status_code == 401:
        return (
            "OpenAI hat den API-Key nicht akzeptiert. Bitte prüfe den Schlüssel oder erstelle einen neuen unter "
            "https://platform.openai.com/api-keys ."
        )
    if status_code == 403:
        return (
            "Der API-Key darf dieses Projekt oder dieses Modell nicht verwenden. "
            "Bitte prüfe Projektwahl, Berechtigungen und IP-/Projektregeln im OpenAI-Dashboard."
        )
    if status_code == 429 and code == "insufficient_quota":
        return (
            "OpenAI hat den API-Key grundsätzlich erkannt, aber für dieses API-Projekt ist aktuell kein "
            "verfügbares Guthaben oder Monatsbudget vorhanden. Bitte prüfe Billing und Limits unter "
            "https://platform.openai.com/settings/organization/billing und "
            "https://platform.openai.com/settings/organization/limits ."
        )
    if status_code == 429:
        return (
            "OpenAI lehnt die Anfrage gerade wegen eines Limits ab. Bitte warte kurz oder reduziere die "
            "Anfragerate. Mehr dazu: https://platform.openai.com/docs/guides/rate-limits/what-are-some-steps-i-can-take-to-mitigate-this"
        )
    if status_code == 400:
        return (
            "Die OpenAI-Anfrage wurde vom Server als ungültig abgewiesen. "
            f"Details: {message or 'Bitte Modellname und Anfrageformat prüfen.'}"
        )
    if status_code and status_code >= 500:
        return "OpenAI meldet gerade einen Serverfehler. Bitte versuche es in kurzer Zeit erneut."
    if message:
        suffix = f" (OpenAI-Fehler {status_code}: {code})" if status_code else ""
        return message + suffix
    return f"Unbekannter OpenAI-Fehler{f' ({status_code})' if status_code else ''}."
