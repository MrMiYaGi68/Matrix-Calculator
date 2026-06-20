# Change Control

Use this lightweight process for release-impacting changes.

## Required For Each Change

- Short problem statement.
- Affected area: UI, parser, natural language, OpenAI, packaging, security,
  documentation or tests.
- Risk rating: low, medium or high.
- Test evidence.
- Documentation update decision.

## Approval Rules

- Low-risk parser/UI fixes can be merged after tests pass.
- Security, OpenAI, packaging and persistence changes require a second review.
- Any change that handles API keys or user data must update `SECURITY.md` or
  `docs/PRIVACY.md` when behavior changes.

## Release Notes

User-visible behavior, dependency, packaging and security changes must be added
to `CHANGELOG.md`.

## Architecture Decisions

Record larger structural decisions in `docs/adr/` before implementation.

