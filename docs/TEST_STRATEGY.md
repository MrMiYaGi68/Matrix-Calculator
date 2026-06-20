# Test Strategy

## Test Layers

- Unit tests: parser, formatting, i18n, button configuration and natural-query
  handlers.
- Service tests: OpenAI helper behavior and settings security.
- GUI smoke tests: construct `MatrixCalculatorWindow` with
  `QT_QPA_PLATFORM=offscreen`.
- Packaging checks: validate `pyproject.toml` and `MatrixCalculator.desktop`.
- Release hygiene: confirm no `__pycache__`, `*.pyc`, local user paths or API
  keys are included in release artifacts.

## Required Local Release Checks

```bash
python3 -m py_compile calculator.py core/*.py ui/*.py
python3 -m unittest discover -s tests -p 'test_*.py'
desktop-file-validate MatrixCalculator.desktop
QT_QPA_PLATFORM=offscreen python3 -c 'from PySide6.QtWidgets import QApplication; from calculator import MatrixCalculatorWindow; app=QApplication([]); w=MatrixCalculatorWindow(); print(w.windowTitle())'
```

## Gaps

- No automated screenshot comparison yet.
- No packaged install test on every target Linux distribution yet.
- No network integration test against the OpenAI API in CI; this is intentional
  to avoid requiring secrets in routine CI.

