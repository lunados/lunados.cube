# TASK-094 — Mile-Abnahme und Übergabe an Verbraucher

Planungsstand: ausgearbeitet; [Abnahme und Übergabe](../10-Evidence/MILE-020/TASK-094-RESULT.md) für den benannten Quell-/G5-Stand durchgeführt. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-041](../04-US/US-041-neighbor-discovery.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,25–0,5 PT (Schätzung)

## Ziel und Arbeit

Die sechs MILE-020-Kriterien anhand TRACEABILITY.md mit gepinnten Artefakten und reproduzierbaren Prüfberichten abnehmen. Owner-Deskriptoren, Schema, Quellenhashes, 13 Lib-Zuordnungen, ADR, Namensverwendung und neighbors-Parität vollständig prüfen. Release-/Bereitstellungsstand von G5 ausdrücklich benennen; wenn die Mile reale G5-Ausgabe beansprucht, müssen deren neighbors gegen dieselben Bytes geprüft sein. Fehlende Host-/Remote-Beobachtung bleibt nicht geprüft, keine Offline-Ergebnisse als Live-Nachweis ausgeben.

## Abnahme und Nachweis

Ein Bericht pro Kriterium nennt Eingaben/Pins, Befehl oder dokumentarischen Review, Ist/Soll, Grenzen und PASS/FAIL/UNRESOLVED/NOT TESTED. Alle sechs Kriterien müssen für Abschluss erfüllt sein; offene Entscheidungen oder fehlender G5-Nachweis verhindern die entsprechende Abnahme. Übergabe an MILE-022/023 enthält nur Referenzen, Versionen, Status-/Hashregeln und offene Grenzen. Aufgaben erst mit verlinkter Evidenz abhaken.

Nachweis: [TASK-094-RESULT](../10-Evidence/MILE-020/TASK-094-RESULT.md) mit Kriterienmatrix, Quellenpins, Live-G5-Beobachtung und Übergabe.

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-086–093; D-1/D-2/D-4 entschieden.

Keine Builder-/Playbook-Implementierung, keine Explorer-Bindung aus MILE-021, keine Ausführung deklarierter Fähigkeiten. Deployment, sofern nötig, ist separat auszuweisen und nicht als erledigt vorauszusetzen.
