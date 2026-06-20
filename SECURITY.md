# Security

## API Keys

Matrix Calculator does not store OpenAI API keys in
`~/.config/matrix-calculator/settings.json`.

Preferred options:

- Set `OPENAI_API_KEY` in the shell or desktop environment before starting the app.
- Enter an API key in the app only for the current running session.

Use restricted, project-scoped API keys where possible. Rotate keys if they
were shared, committed, logged or stored in plaintext.

## Local Data

The settings file contains UI and assistant preferences only. It is written
with owner-only permissions (`0600`).

Calculation history is held in memory during the app session unless exported
manually by the user.

## Network Use

The calculator works locally by default. External OpenAI API calls are only made
when API mode is selected and an API key is available.

Do not enter personal, confidential or regulated data into online AI mode unless
the relevant privacy, contractual and organizational requirements are already
covered.

