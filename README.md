# Matrix Calculator

Ein wissenschaftlicher Taschenrechner in Python für Linux mit moderner `PySide6`-Oberfläche.

## Funktionen

- Grundrechenarten, Klammern und Potenzen
- Moderne `PySide6`-UI mit großem Display, Seitenpanel und klarer Farbcodierung
- Neues Splitter-/Karten-Layout für bessere Lesbarkeit auch ohne Vollbild
- Startet standardmäßig im `Basic`-Layout, mit umschaltbarem `Scientific`-Modus
- Trigonometrie mit `Deg`/`Rad`
- `2nd`-Umschaltung für inverse und alternative Funktionen
- `ln`, `log`, `e^x`, `10^x`, `sqrt`, `cbrt`, `1/x`, `abs`, Fakultät und Prozent
- Hyperbolische Funktionen `sinh`, `cosh`, `tanh`
- Komplexe Zahlen mit `i`, `real`, `imag`, `conj`, `arg`
- Restdivision mit `mod` und Primfaktorzerlegung mit `pf` oder `factor`
- Speicherfunktionen `mc`, `mr`, `m+`, `m-`, `ms`
- Verlaufspanel mit wiederverwendbaren letzten Rechnungen
- Live-Vorschau des Ergebnisses während der Eingabe
- Natürliche Rechenfragen wie `Was sind 20% von 450?`
- Die lokale KI versteht Rechenfragen zuverlässig auf Deutsch und Englisch.
- KI-Bereich mit Chat-Verlauf für Rechenfragen
- Lokaler Mathemodus vor API-Fallback für schnelle, direkte Aufgaben
- Modellwahl und Schritt-für-Schritt-Erklärungen für OpenAI-Antworten
- Optionaler Chat-Kontext für mehrteilige OpenAI-Unterhaltungen
- Exportierbarer Rechenverlauf als Textdatei
- Online-KI ist nur eine optionale Erweiterung, der Standard bleibt lokal und ohne Anmeldung nutzbar
- Smartere Eingabe mit impliziter Multiplikation und automatischem Schließen offener Klammern bei `=`
- Prozenttaste mit typischer Taschenrechner-Logik, z. B. `200 + 10 %` => `200 + 20`
- Optionale OpenAI-Anbindung für frei formulierte Rechenfragen per API-Key
- Tastatursteuerung für Zahlen, Operatoren, `Enter`, `Backspace`, `Delete`, `Escape`

## Start

Installierbare Entwicklungsumgebung:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
matrix-calculator
```

Für die optionale direkte OpenAI-API-Anbindung:

```bash
python3 -m pip install -e '.[ai]'
```

Falls `PySide6` auf Tumbleweed noch fehlt:

```bash
sudo zypper install python313-pyside6
```

Danach:

```bash
python3 calculator.py
```

Oder direkt ausführbar:

```bash
./start-calculator.sh
./calculator.py
```

## Tests

Parser-Regressionen lassen sich ohne zusätzliche Abhängigkeiten direkt so prüfen:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Desktop-Launcher:

- [MatrixCalculator.desktop](MatrixCalculator.desktop) erwartet den installierten Befehl `matrix-calculator`.

## Projektstruktur

- `calculator.py`: Startpunkt und Qt-Hauptfenster.
- `core/formatting.py`: Gemeinsame Zahlen- und Ausdrucksformatierung.
- `core/expression_parser.py`: Mathematischer Ausdrucksparser ohne GUI-Abhängigkeiten.
- `core/openai_support.py`: OpenAI-Hilfslogik, Modellwahl, Header, Hilfetext und API-Fehlermeldungen.
- `core/natural_query/`: Lokale natürliche Rechenfragen, Textlogik und einfache Arithmetik-Fallbacks.
- `ui/dialogs.py`: Wiederverwendbare Dialogfenster.
- `ui/button_config.py`: Tastenlayout, Tastaturhinweise und Einfügewerte.
- `tests/`: Regressionstests für Parser, OpenAI-Hilfslogik, UI-Konfiguration und bekannte Bugs.
- `docs/`: Architektur-, Datenschutz- und Betriebsnotizen.
- `pyproject.toml`: Reproduzierbare Projektmetadaten und optionale Abhängigkeiten.

## Hinweise

- Die App nutzt `PySide6`.
- Für die OpenAI-Funktion wird ein OpenAI API-Key verwendet. Ein normaler ChatGPT-Login allein reicht dafür nicht.
- Den API-Key findest du in deinem OpenAI-Konto unter `https://platform.openai.com/api-keys`.
- Der Key ist nötig, weil die App nur damit offizielle API-Anfragen an OpenAI senden darf. Ohne Key bleibt der Rechner im lokalen Modus oder verweist auf ChatGPT im Browser.
- API-Keys werden nicht dauerhaft in `~/.config/matrix-calculator/settings.json` gespeichert. Setze für dauerhafte Nutzung `OPENAI_API_KEY` in deiner Umgebung oder gib den Key nur für die laufende Sitzung ein.
- OpenAI-Einstellungen wie Modell, Antwortmodus, Sprache und Theme werden lokal in `~/.config/matrix-calculator/settings.json` gespeichert.
- Ohne grafische Session gibt die App eine klare Fehlermeldung aus, statt mit Traceback abzubrechen.
- Siehe [SECURITY.md](SECURITY.md), [docs/PRIVACY.md](docs/PRIVACY.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) und [docs/RUNBOOK.md](docs/RUNBOOK.md).
- This project is licensed under the GNU GPL v3 or later (`GPL-3.0-or-later`).
