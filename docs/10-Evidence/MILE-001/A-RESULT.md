# Charge A — abgeschlossen

Datum: 2026-11-01 · TASK-001 und TASK-002 erfüllt.

[Ausgangsstand](A-CAPABILITY-BASELINE.md) · [Vorher](a-before.json) · [Nachher](a-after.json)

Die lokale Selbstauskunft ergänzt Kontext /1 bis /7 und Entry-Profile. Quellenpräsenz und tatsächliche Runtime-Ladeprüfung sind ausdrücklich getrennt. Das neue Format `aiaeao.cube.local-validation-discovery/1` und sein Schema ergänzen nur den lokalen Discovery-Pfad. Die Toolbeschreibung nennt den expliziten Dispatch und seine Grenzen.

## Durchgeführte Prüfungen

Arbeitsverzeichnis `P3/adapters/mcp-local`, Interpreter `.venv/bin/python -B`:

| Aufruf | Ergebnis |
|---|---|
| `-m unittest discover -s tests -p 'test_*surface.py' -v` | 56 Tests, OK |
| `-m unittest discover -s tests -p test_validation_discovery.py -v` | 5 Tests, OK; einschließlich Missing-Module- und Schema-Negativkontrolle |
| `-m unittest discover -s tests -p test_g6_plan_views.py -v` | 19 Tests, OK; 36,817 s |
| SDK 2.0.0, frische stdio-Verbindung nach Änderung | 10 Tools; Discovery entspricht lokalem Code; Erfolg |

Die Prüfanzahl beträgt 80. Die kanonischen Hashes von Legacy- und G4-Ausgabe sind vor/nach Änderung identisch; siehe Rohprotokolle. Kein Golden angepasst. Keine semantische Validatoränderung, kein G5-Deployment, kein Vollständigkeitsbeweis aller Kontextkombinationen.
