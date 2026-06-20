# Support Guide

## Common Issues

### App Does Not Start

Check:

- `~/.cache/matrix-calculator.log`
- PySide6 installation
- `DISPLAY`, `WAYLAND_DISPLAY` and desktop session variables

### OpenAI API Does Not Work

Check:

- `OPENAI_API_KEY` is set or a key was entered for the current session.
- The API key belongs to the correct project.
- Billing and model permissions are active.
- The user did not expect a ChatGPT web login to work as an API credential.

### Wrong Calculation Result

Capture:

- Exact input expression or natural-language query.
- Expected result.
- Current app version.
- Whether `Deg` or `Rad` mode was active.

Add a regression test before fixing parser or natural-language behavior.

## Escalation

Security, API-key, privacy and packaging issues should be treated as
release-blocking until triaged.

