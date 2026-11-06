# MILE-021 — Explorer an den Vertrag binden

Status: **geplant (Entwurf)** · Stand: 2026-11-06 · Betrifft: lunados.explorer, lunados.cube · Nach [MILE-020](MILE-020-module-capability-descriptors.md) sinnvoll, aber nicht davon abhängig

## Ziel und Entscheidung

Explorer und Cube sollen sich nur noch über gepinnte Verträge berühren, nicht über Ordnerpfade und Interna. Nachweise in beide Richtungen sollen reproduzierbar sein.

**Entscheidung (Nutzer, 2026-11-06):** lunados.explorer wird ein **eigenes Repository**. Der Explorer nutzt den Cube; die Cases enthalten Projektdaten von außen und ändern sich häufiger als die gepinnten Cube-Profile. Der Cube übernimmt die Explorer-Sheets, auf die sich seine Abnahmen stützen, als gepinnte Fixtures, wie er es bei lunados.lib bereits tut.

## Ausgangslage (2026-11-06)

- lunados.explorer ist nicht unter Versionskontrolle.
- `scripts/print_sheet.py` hängt `P1/`, `P2/` und `P3/adapters/mcp-local` des Cube per `sys.path` ein; `scripts/check.py` nutzt standardmäßig `../lunados.cube/AIAEAO_Pure_Cube_P0_v9.4/v9.4/grammar`.
- Cube-Abnahmen stützen sich auf Explorer-Sheets, unter anderem [MILE-013](MILE-013-printer-module-bodies.md) bis [MILE-016](MILE-016-axis-pair-views.md), `VP12_ACCEPTANCE_SPEC.md` (VP12-03) und `P1_15_ACCEPTANCE_SPEC.md` (P1.15-06).
- Die P1.8/P1.9-Goldens (`golden_exp002b`, `golden_exp024` …) stammen aus Experimenten in lunados.space. Ob jedes Golden kopiert und gehasht ist, ist nicht geprüft.

## Arbeitsumfang

1. lunados.explorer als Git-Repository anlegen; Methode (`docs/`, `schema/`, `mappings/`, `agent/`, `scripts/`) und Cases (`cases/`) bleiben getrennt. GitHub-Repository erst nach Freigabe.
2. Der Explorer bindet den Cube über einen **gepinnten Checkout** (D-1): eine Pin-Datei nennt Cube-Commit und Hash; `check.py` und `print_sheet.py` laufen offline gegen genau diesen Stand und prüfen den Pin vor jedem Lauf. Die `sys.path`-Einbindung von P1/P2/P3 ohne Pin entfällt.
3. Der Cube übernimmt die referenzierten Sheets (mindestens F02, F03a, F05) mit Explorer-Commit und SHA-256 als Fixtures und stellt die betroffenen Abnahmen darauf um. Abgeschlossene Nachweise bleiben unverändert; neue Läufe verweisen auf die Fixtures.
4. Herkunft der Space-Goldens prüfen und dokumentieren; fehlende Kopien oder Hashes nachziehen.

## Entscheidung

| ID | Frage | Ergebnis |
|---|---|---|
| D-1 | Wie bindet der Explorer den Cube? | **Entschieden (Nutzer, 2026-11-06): gepinnter Checkout** mit Cube-Commit und Hash. Eine Anbindung über MCP bleibt möglich, ist aber nicht Teil dieser Mile. |

## Abnahme

- [ ] lunados.explorer ist ein Git-Repository mit sauberem Ausgangs-Commit.
- [ ] Kein Explorer-Skript importiert Cube-Interna über Ordnerpfade; `check.py` und `print_sheet.py` laufen gegen den gepinnten Cube-Stand und brechen bei abweichendem Hash ab.
- [ ] Die Cube-Fixtures nennen Explorer-Commit und SHA-256; die betroffenen Abnahmen laufen ohne Nachbarordner.
- [ ] Herkunft aller Space-Goldens ist dokumentiert.

## Nicht in MILE-021

Änderungen an der Explorer-Methode; Aufnahme in die Playbook-Library ([MILE-023](MILE-023-playbook-library.md)); Verschieben der Cases in den Cube.

## Aufwand

Schätzung 1,5–2,5 PT.
