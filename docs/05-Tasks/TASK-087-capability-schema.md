# TASK-087 — Deskriptorformat und Offline-Prüfung

Planungsstand: ausgearbeitet; [Ergebnisnachweis](../10-Evidence/MILE-020/TASK-087-RESULT.md) liegt vor. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-038](../04-US/US-038-capability-contract.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,5–0,75 PT (Schätzung)

## Ziel und Arbeit

Das durch D-1 entschiedene eigene dokumentarische Format ausarbeiten; `aiaeao.module-capabilities/1` bleibt bis zur Schemafestlegung Arbeitstitel. Modulkennung, Format-/Modul-/Fähigkeitsversionen, Quellen und SHA-256, Fähigkeiten mit Input/Output, implemented/candidate/unknown und Ausschlüsse definieren. Module v2 bei passenden Quellen nur mit exakter Version und Hash referenzieren. Dokumenthash extern im Verweis führen, sodass kein Selbsthash-Zirkel entsteht. Hash über exakte Datei-Bytes; Serialisierung des neighbors-Blocks festlegen. Das Prüfskript verarbeitet nur ausdrücklich bereitgestellte lokale Artefakte und einen Pin-Manifest; kein Nachladen und kein latest-Fallback.

## Abnahme und Nachweis

Schema, Prüfskript und erwartete Fälle: gültiger vollständiger Deskriptor, falsche Version/Typ/Status, doppelte IDs, fehlende Quelle, manipulierte Bytes, fehlender lokaler Snapshot. Strukturfehler und Hashabweichung sind Fehler; fehlende Bytes sind unavailable/unprüfbar und niemals erfolgreicher Pin-Nachweis. Ein generisches MCP-Tool darf nicht als gültiger unveränderter v2-Deskriptor durchgehen. Prüfbefehle und Soll-Ergebnisse dokumentieren.

Abschlussnachweis: [TASK-087-RESULT](../10-Evidence/MILE-020/TASK-087-RESULT.md) mit Schema- und Prüferpins, positiven und negativen Offline-Fällen sowie Grenzen der Aussage. Reale Owner-Deskriptoren folgen in TASK-088–090.

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-086 und entschiedene D-1.

Keine Autorisierung, dynamische Registrierung oder universelle MCP→v2-Übersetzung. Module v2 bleibt normativ unverändert.
