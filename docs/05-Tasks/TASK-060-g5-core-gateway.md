# TASK-060 — Kern und Gateway

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-B · Aufwand: 1,25–2 PT

## Ziel und Arbeit

G5-Kern `0.8.0-proof`: P1.13 und die Plan-Printer stufen (`assemble_core.py`, Laufzeit-Assets), Dispatch für `/9` und die drei Plan-Tools; Gateway: drei Tools mit Schemas; Discovery. Offline-Prüfung: Remote = lokal für alle Vektoren, Laufzeitmessung nach D-6, Asset- und Prüfsummenprüfung, Parität G4/G5.

## Ergebnis und Akzeptanz

- Offline alles grün; Messung dokumentiert; bei Überschreitung Umfang nach D-6 begrenzt.

## Abhängigkeiten und Grenze

[TASK-059](TASK-059-g5-r5-expectations.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.

## Ergebnis (2026-11-02)

- Zusammenbau: P1.13 und die Plan-Printer VP-07–VP-11 unverändert gestuft (150 Dateien); Selbstprüfung mit KF-01–KF-09 und einer Kette je Sicht. Kern `P3-MCP-REMOTE/0.8.0-proof`: drei Plan-Operationen (Plan-Schicht erst bei Bedarf geladen), Discovery mit `p113_control_flow` und `P2.plan_views` (`remote_available: true`). Gateway `0.2.0-proof`: drei Tools mit Schemas wie lokal, Antwortgrenze 2 MiB + 64 KiB.
- [Offline-Parität](../../P3/remote-mcp-g5/evidence/G5_R5_OFFLINE_PARITY.json): 88/88 wie erwartet (Discovery, 16 `/9`, 71 Plan-Ketten), keine Lesezugriffe außerhalb der Laufzeit, Rechenzeit höchstens 0,89 s (CPython). Sechs Sprachdateien als neue Laufzeit-Assets in den Text-Regeln.
- Bisherige Gates grün: `assemble_core`, Asset-Prüfung (49), G5-Vertrag (21 Tests), Gateway-Tests, `verify_release`, Prüfsummen (33 Dateien), Parität G4/G5 22/22, 10/10, 15/15, 21/21.
- Präzisierungen W-1–W-6 in §9 der [Spezifikation](../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md), u. a. kompakte Kodierung zwischen Kern und Gateway (W-1).
- Für die Bereitstellung: [`r5_remote_acceptance.py`](../../P3/remote-mcp-g5/scripts/r5_remote_acceptance.py) (offline mit Ersatz-Client 88/88 geprüft), `sdk_remote_smoke.py` mit zehn Tools, Nachtrag §9 in [`DEPLOYMENT.md`](../../P3/remote-mcp-g5/DEPLOYMENT.md).
