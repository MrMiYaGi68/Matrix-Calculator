# Runbook

## Install For Development

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

On distributions that package PySide6 system-wide, installing the distro
package is also supported.

## Start

```bash
matrix-calculator
```

For a source checkout without installation:

```bash
./start-calculator.sh
```

## Optional OpenAI API

```bash
export OPENAI_API_KEY='...'
matrix-calculator
```

The app does not store the key in `settings.json`.

## Test

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

For CI-equivalent hygiene checks, keep Python bytecode outside the checkout:

```bash
PYTHONPYCACHEPREFIX=/tmp/matrix-calculator-pycache \
QT_QPA_PLATFORM=offscreen \
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Build Release ZIP

```bash
python3 tools/build_release_zip.py --output ../meine-app-clean.zip
```

The release ZIP builder excludes `__pycache__`, `*.pyc`, local cache
directories and existing ZIP files, then validates the archive before
returning success.

## Logs

The starter script writes launch diagnostics to:

```text
~/.cache/matrix-calculator.log
```

## Release Checklist

- Run the full unittest suite.
- Build the ZIP with `tools/build_release_zip.py`; do not package the checkout
  manually.
- Start the app once on the target desktop environment.
- Verify `MatrixCalculator.desktop` through the installed `matrix-calculator`
  command.
- Confirm no `__pycache__` or `*.pyc` files are included in release archives.
- Confirm no API keys are present in settings, logs or archives.
