# Architecture

Matrix Calculator is a local Linux desktop application.

## Current Layers

- `calculator.py`: PySide6 window, UI state and app entry point.
- `core/assistant_service.py`: UI-independent assistant decision flow for local answers, clarification and fallback routing.
- `core/expression_parser.py`: local mathematical expression parser.
- `core/natural_query/`: local natural-language math handlers.
- `core/formatting.py`: shared numeric and expression formatting.
- `core/settings.py`: settings persistence, legacy secret migration and file-permission hardening.
- `core/openai_client.py`: OpenAI model lookup and request execution.
- `core/openai_support.py`: OpenAI request helpers and API error descriptions.
- `core/i18n.py`: translations and UI text.
- `ui/`: reusable UI configuration and dialogs.

## Known Architecture Debt

`calculator.py` still owns the main UI and some helper formatting methods.
Settings persistence, OpenAI network access and assistant flow decisions have
been extracted into service classes. The next refactor should move natural-query
preview generation and query-help suggestions into smaller core modules.

## Dependency Direction

Core modules should stay free of PySide6 imports. UI code may depend on core
modules, but parser and natural-query tests must remain runnable without a
display server.
