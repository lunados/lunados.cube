# MILE-016 — Nachweis

Stand: 2026-11-05 · lokal (G4/G6), lunados.explorer und G5 (R10, Core `0.9.3-proof`, Gateway `0.3.0-proof`, live 58/58) · **vom Nutzer abgenommen am 2026-11-05**

## Reihenfolge

| Schritt | Commit |
|---|---|
| Entwürfe VP-09.3 und VP-12 | 0799944 |
| VP-09.3: Entscheidungen, Vektoren X-01…X-12 und unabhängiges Oracle vor dem Code | 2267a18 |
| VP-09.3 Laufzeit (`P2-VP-AXES/0.9.3`: X × Y, Status der Kreuzung, Locale `de-0093`) | 6f40ead |
| VP-12: Spezifikation, Vektoren L-01…L-14 und Oracle vor dem Code; §1.6 präzisiert, Erwartungen unverändert | 0514d14, 568873f |
| VP-12 Laufzeit (`P2-VP-LANDSCAPE/0.12.0`, `vplandscape`) und Layout für 5–6 Spalten | fa685e2, b336bdd |
| Explorer-Abnahme vermerkt | 5c9a6a7 |
| G6 und G5 R10: Erwartungen vor der Bereitstellung, dann live | 7730d4e, 87324a7 |

Gemergt über PR #48, #49 (VP-09.3, VP-12), #51 (Doku) und #53 (R10).

## Ergebnis je Backlog-Punkt

| ID | Ergebnis | Prüfung |
|---|---|---|
| B9 X × Y | Paar X × Y in `cube.axes`: Zellen aus deklarierten P1.6-Slots je X-Dimension, fehlende Pflicht-Slots als „fehlt“, Ledger der X-Einheiten | X-01…X-12 12/12 gegen das Oracle; 0.9.0…0.9.2 byte-identisch |
| B6 Landschaft | `cube.landscape`: Schichtspalten (VP-07.2-Layer-Map oder Ankerfamilien), Bänder je Schritt, „eingeführt“/„abgelöst ab …“ mit `declared_by`, Kanten nach Herkunft, Platzierungsprädikate kräftig, X-Endpunkte außerhalb, Budget mit Ablehnung | L-01…L-14 gegen das Oracle, 19 Tests; keine Datei anderer P2-Pakete geändert |
| B10 Status der Kreuzung | Statuszeile in X × Y (`X × Y · kanonisch · Morphologie §3.3`) und in der Landschaft (`Y × Z über T · abgeleitet · Morphologie 01.3`), de/en | in X-/L-Vektoren enthalten |

## Abnahme mit lunados.explorer

`print_sheet.py` druckt je Blatt zusätzlich die Landschaft des ganzen Plans (`Fnn-full`, Spalten aus `mappings/landscape-layers.json`) und X × Y:referent für Blätter mit X-Instanz; das Cockpit hat die Sichten „Landschaft“ und „Achsen X × Y“.

| Ergebnis | Wert |
|---|---|
| Landschaft | 11/11 Blätter, `check-panels` PASS; F02 und F05 (Current, BETA) gesichtet |
| X × Y | F05 (vollständig), F03a (fehlender Principal sichtbar), F01 und F04a (leer, X-Endpunkt ungebunden); übrige Blätter ohne X-Instanz |
| Bisherige Sichten | Ablauf und Phasen unverändert PASS; `check.py` 0 Befunde |

## Remote (G6, G5 R10)

- G6: `cube_plan_source` mit Printer `vplandscape`, `cube_plan_views` mit Sicht `cube.landscape`, `cube_plan_check`; P3 `mcp-local` 256 Tests OK.
- G5: Core `0.9.3-proof` stagt `vplandscape` und die Locale-Ordner von `vpaxes` und `vplandscape`; Gateway `0.3.0-proof` (Version `296e448c-…`). Erwartungen vor der Bereitstellung fixiert (57 Aufrufe, R9 50/50 unverändert); live **58/58** ([R10](../../../P3/remote-mcp-g5/G5_R10_ACCEPTANCE.md)).

## Nicht Teil, verschoben

VG-Anker der Schichtspalte (neu B13) und Backlog B11, B12, B4, B7, B8 → [MILE-018](../../02-Milestones/MILE-018-axis-pairs-follow-up.md). Der TOML-Builder (D-3) ist präzisiert und liegt als Referenz in lunados.connector (MILE-004).

## Grenzen

- G5 live: ein einzelner Lauf, keine Wiederholung, kein Monitoring ([KNOWN_LIMITS](../../../P3/remote-mcp-g5/KNOWN_LIMITS.md)); die Core-Versions-ID wurde nicht übermittelt.
- Lokale Prüfungen liefen im Container-Klon und auf dem Gerät; eine Bestätigung im venv des Nutzers steht aus.
