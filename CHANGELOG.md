# Changelog

## 1.0.2 - 2026-06-20

- Improved the calculator UI hierarchy for compact and expanded assistant use.
- Added explicit visual states for local calculation, AI status, warnings,
  errors and recovery after clearing.
- Added an offscreen UI smoke test for compact mode, expanded assistant mode,
  error recovery and rich-text font-stack hygiene.
- Updated CI actions and packaging metadata to remove Node.js and build
  warnings.

## 1.0.1 - 2026-04-29

- Prepared a follow-up release so the source package, Discover metadata and
  Flathub packaging can be kept in sync.
- Switched the Flatpak manifest to `io.qt.PySide.BaseApp` in the repository
  copy used for the next release cycle.
- Restored working AppStream screenshot URLs in the upstream metadata.
- Kept the current Flathub submission stable while preparing the next clean
  release.

## 1.0.0 - 2026-04-27

- Added project packaging metadata via `pyproject.toml`.
- Declared PySide6 as an install dependency so the app starts after a standard install.
- Removed persistent OpenAI API key storage from application settings.
- Hardened settings file permissions to owner-read/write only.
- Made the desktop launcher independent of absolute user paths.
- Added security, privacy, architecture and operations documentation.
- Extracted settings persistence and OpenAI network access from the main window
  into dedicated core services.
- Extracted assistant flow decisions into a UI-independent service.
- Expanded the local natural-language assistant for German and English, including
  written numbers, numeric abbreviations, relationship word problems and English
  smalltalk/chat abbreviations.
