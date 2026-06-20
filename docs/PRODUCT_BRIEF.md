# Product Brief

## Purpose

Matrix Calculator is a Linux desktop calculator for users who need local
scientific calculations, calculator-style percentage behavior and optional
natural-language math assistance.

## Target Users

- Individual Linux desktop users.
- Learners and technically minded users who want a local-first calculator.
- Maintainers who need a small, testable desktop utility.

## Release 1 Scope

Must have:

- Local expression parsing and scientific calculator buttons.
- Basic and scientific layout modes.
- Local natural-language math for common arithmetic, percent, geometry,
  finance and unit-style questions already covered by tests.
- In-memory history with explicit export.
- Optional OpenAI API mode that is disabled unless an API key is provided.

Out of scope for Release 1:

- Multi-user server operation.
- Centralized account management.
- Cloud sync.
- Automatic collection of usage analytics.
- Persisting API keys in application settings.

## Quality Goals

- Local mode works without network access.
- Parser and natural-query behavior are covered by regression tests.
- Release artifacts do not contain Python bytecode caches or local user paths.
- Optional online mode has explicit user control and no persistent API-key
  storage.

## Acceptance Criteria

- Full unittest suite passes.
- `desktop-file-validate MatrixCalculator.desktop` passes.
- App starts in an offscreen Qt smoke test.
- README, security notes and runbook are updated for each release-impacting
  change.

