# Charge B — abgeschlossen

Datum: 2026-11-01 · TASK-003, TASK-004 und TASK-006 erfüllt.

[Vollständiger Bericht](b-report.json) · [Fall-/Berichtsvertrag und Wiederholung](../../09-Research/analysis-readiness/README.md)

Drei vor dem Lauf fixierte, exakt aus dem historischen Protokoll extrahierte Fälle wurden zweimal ausgeführt. Jede Wiederholung öffnete eine frische lokale stdio-MCP-Verbindung. Der Bericht enthält Quellhashes von 836 Dateien, HEAD, Python/SDK-Version, vollständige Eingaben und SDK-Rohantworten. Fachstatus/Diagnosen sind in beiden Läufen gleich; die Quelldateien blieben während der Prüfung unverändert.

| Fall | Fachstatus | Erwartung |
|---|---|---|
| P1-method-arity-negative | FAIL, P1_METHOD_SIGNATURE | erfüllt |
| P1-mode-display | PASS | erfüllt |
| P1-mode-unbound | UNRESOLVED, P1_QUALIFIER_PROFILE_MISSING | erfüllt |

Zwei echte Aufrufe mit leerem Kontext lieferten TOOL_ERROR/P1_MCP_CONFIG_INVALID ohne Fachstatus. Ein kontrollierter Start eines nicht vorhandenen Programms erzeugte FileNotFoundError/UNAVAILABLE, ebenfalls ohne Fachstatus. Es wurde keine fachliche Antwort simuliert. Unbeobachtete Gesamturteile zu Ausdruck, Bindung, Darstellung und Nutzen bleiben NOT_ASSESSED.

## Verifikation

- `P3/adapters/mcp-local/.venv/bin/python -B -m unittest discover -s scripts/research/tests -v`: 8 Tests, OK.
- `P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --output /private/tmp/mile001-b-run`: Exit 0, 3 Fälle × 2 Verbindungen, Ergebnis PASS für die definierten Proben.

Grenze: minimale deklarative Validatorfälle, keine fachliche Gesamtprüfung der fünf Ansätze, kein Renderer- oder Nutzertest. Die Runtime wird im vorhandenen lokalen Adapter geprüft, nicht im öffentlichen Reader oder auf G5.
