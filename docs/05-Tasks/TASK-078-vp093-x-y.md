# TASK-078 — VP-09.3: X × Y aus deklarierten Instanzen, Status der Kreuzung

Mile: [MILE-016](../02-Milestones/MILE-016-axis-pair-views.md) (B9, B10) · Aufwand: 0,5–0,75 PT · Status: erledigt (lokal, G4/G6), 2026-11-05

Spezifikation: [VP09_3_ACCEPTANCE_SPEC.md](../../P2/visual-printer-axes-v1/VP09_3_ACCEPTANCE_SPEC.md). Reihenfolge: Entscheidungen D-1…D-6, Vektoren X-01…X-12 und Oracle vor dem Code, 0.9.0…0.9.2 vorher pinnen, dann Laufzeit, G6, Explorer-Abnahme.

## Ergebnis

- X-01…X-12 12/12 gegen das vorab committete Oracle; 0.9.0…0.9.2 unverändert (Goldens, Regressionsdigests), `VP09_SHA256SUMS.txt` nachgeführt.
- P2: axes, cells, migration, instances, sequence grün; P3 `mcp-local` grün; G6 meldet `vpaxes` 0.9.3 mit `X × Y`.
- lunados.explorer: F05 X × Y vollständig (5 Einheiten, Kette aus Principal, Anfrage und Befugnis); F03a zeigt den fehlenden Principal von A4 als `fehlt` und die Kette von A29 bis zur Revision.
- Explorer-Pipeline (2026-11-05): `print_sheet.py` druckt X × Y:referent für jedes Blatt mit X-Instanz (F01, F03a, F04a, F05; F01/F04a leer, da X-Endpunkt ungebunden), `check-panels` PASS; Cockpit-Sicht „Achsen X × Y“.
- Nicht Teil: weitere Ausgänge einer Admission (Gateway, P1.13) erscheinen nicht über Slots und zählen als `x_ignored`; G5 als eigener Schritt.
