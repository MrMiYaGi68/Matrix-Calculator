# ADR 0001: Local-First API Key Handling

## Status

Accepted

## Context

The calculator is a desktop client with optional OpenAI API access. Persisting
API keys in a plaintext settings file creates avoidable risk.

## Decision

The app does not store API keys in `settings.json`. Users can set
`OPENAI_API_KEY` in their environment or enter a key for the current app session
only.

## Consequences

- Local mode remains unaffected.
- Direct API mode may require users to configure their environment.
- Existing settings files containing `openai_api_key` are migrated by removing
  that field on load.

