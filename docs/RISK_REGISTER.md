# Risk Register

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | API key is stored or leaked in plaintext | High | Medium | Development | Do not persist keys; prefer `OPENAI_API_KEY`; test settings output | Mitigated |
| R-002 | Release archive includes local paths or bytecode caches | Medium | Medium | Release | Validate desktop file; remove `__pycache__`; CI release hygiene check | Mitigated |
| R-003 | PySide6 dependency breaks clean installs | High | Medium | Release | PySide6 is declared as an install dependency; CI includes Qt smoke tests | Mitigated |
| R-004 | `calculator.py` remains broad | Medium | Medium | Architecture | Continue extracting preview/help formatting and UI-independent helpers | Partially mitigated |
| R-005 | Online AI receives personal or confidential data | High | Medium | Product | Local-first default; privacy notes; direct API requires session transfer approval; chat context disabled by default | Mitigated technically; legal review required |
| R-008 | Organizational rollout lacks completed GDPR controller notice, DPA/AVV decision or transfer assessment | High | Medium | Product/Legal | Complete `docs/DATA_PROTECTION.md` before rollout | Open |
| R-006 | UI changes regress keyboard or parser behavior | Medium | Medium | QA | Unit tests plus Qt smoke test before release | Mitigated |
| R-007 | Costs from external API are uncontrolled | Medium | Low | Product | No automatic API use without key; document budget/limits responsibility | Open |

Review this register before each release and whenever online-AI behavior,
storage, packaging or installation behavior changes.
