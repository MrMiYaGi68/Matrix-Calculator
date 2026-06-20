# Data Protection Checklist

Matrix Calculator is designed as a local-first desktop application. This file
documents the project controls that support GDPR-aligned use. It is not a legal
opinion and must be completed by the responsible controller before an
organizational rollout.

## Processing Overview

| Area | Default behavior | Personal-data risk | Control |
| --- | --- | --- | --- |
| Local calculator input | Processed on the user's device | Low, unless the user types personal data | No network request in local mode |
| AI chat history | Kept in memory for the running app session | Medium if personal data is typed | Clear-history action, no automatic export |
| Direct OpenAI API mode | Optional and user initiated | Medium to high depending on input | API key required, explicit session transfer approval |
| API key | Environment variable or current session only | Secret leakage risk | Not persisted in `settings.json`; legacy keys removed |
| History export | User-selected text export | Depends on history content | Explicit export action only |

## Controller Checklist

Before distributing this app in an organization, the controller must fill in:

- Controller identity and contact details.
- Data protection officer contact, if applicable.
- Purpose and legal basis for optional online AI processing.
- Categories of data users are allowed to enter.
- Recipient categories, including OpenAI API when direct API mode is enabled.
- Retention policy for exported history, local logs and support tickets.
- Process for access, deletion, rectification, portability and objection
  requests.
- Complaint path to the competent supervisory authority.
- Whether an OpenAI Data Processing Addendum / AVV / DPA is required and in
  place.
- Third-country transfer assessment and safeguards, if applicable.
- Whether a DPIA is required for the intended rollout scenario.

## Technical And Organizational Measures

- Data minimization: local mode is the default and performs no network request.
- Privacy by default: chat context for API prompts is disabled by default.
- User control: direct API transfer asks for explicit approval once per app
  session.
- Secret handling: API keys are not written to `settings.json`; file
  permissions are hardened to `0600`.
- Release hygiene: release archives are built by `tools/build_release_zip.py`
  and exclude bytecode/cache artifacts.
- Testing: CI runs unit tests, compile checks, desktop validation and release
  hygiene checks.

## Open Items For Legal/Operations

- Replace this checklist with the organization's actual privacy notice before
  external distribution.
- Document support-ticket retention and deletion procedures.
- Define incident handling, breach-notification ownership and escalation times.
- Decide whether the embedded ChatGPT web view is allowed in the target
  environment or should be disabled by policy.

## Reference Points

- GDPR Article 13: information duties at data collection.
- GDPR Article 28: processor contract / DPA requirements.
- GDPR Article 32: security of processing and regular evaluation of measures.
- OpenAI API / enterprise privacy documentation for data use, training and
  business controls.
