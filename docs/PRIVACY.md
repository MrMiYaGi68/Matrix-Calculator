# Privacy Notes

Matrix Calculator performs calculations locally by default.

This note is a project-level privacy baseline. For organizational or public
distribution, complete `docs/DATA_PROTECTION.md` with the actual controller,
legal basis, recipient, retention and data-subject-rights information.

## Local Mode

Local expression parsing and supported natural-language math run on the user's
machine. No network request is required.

## Optional Online AI Mode

When direct API mode is selected and an API key is active, the current user
query can be sent to the OpenAI API after an explicit session approval. Chat
context is disabled by default and is sent only if the user enables it. Users
should not send personal, confidential or special-category data unless they
have checked their applicable privacy and contractual requirements.

The app does not persist API keys. Users can provide a key through
`OPENAI_API_KEY` or for the current session only.

## Exported History

Calculation history is exported only when the user explicitly chooses the
history export action.

## Data Subject Requests

The app has no central account database. Local history can be cleared in the UI.
Exported files, support tickets and backups are outside the app and must be
handled by the controller's operational process.
