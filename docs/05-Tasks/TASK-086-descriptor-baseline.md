# TASK-086 — Quellen, Modulabdeckung und D-1 vorbereiten

Planungsstand: ausgearbeitet. Quellenbaseline und D-1-Entscheidung sind im [Ergebnisnachweis](../10-Evidence/MILE-020/TASK-086-RESULT.md) dokumentiert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-038](../04-US/US-038-capability-contract.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,25–0,5 PT (Schätzung)

## Ziel und Arbeit

Eine Baseline aus den in design.md genannten Quellen erstellen: Repo, Commit, relativer Pfad, SHA-256 der gelesenen Bytes, Versionsfeld, Owner und Aussagegrenze. Sieben logische MILE-071-Rollen einschließlich Server GUI von Repositories und Paketen unterscheiden; Translator separat führen. Cube-Flächen lokal/G5 einzeln sichern. Für D-1 die drei Optionen anhand mindestens eines Cube-Tools, einer Lib-Methode und der beiden v2-Fähigkeitstypen vergleichen. Entscheidung durch Nutzer und betroffene Vertragsowner dokumentieren; bis dahin keine Variante als beschlossen behandeln.

## Abnahme und Nachweis

Eine vollständige Abdeckungsmatrix und der genaue v2-Schemapin liegen vor. Die Matrix nennt für jede Rolle die spätere Deskriptorquelle, auch wenn nur candidate/unknown belegbar ist. D-1 enthält gewählte Option, Kompatibilität und Auswirkungen; bleibt die Entscheidung offen, wird TASK-087 blockiert, die Bestandsaufnahme ist dennoch nutzbar.

Abschlussnachweis: [TASK-086-RESULT](../10-Evidence/MILE-020/TASK-086-RESULT.md) mit Quellenpins, Rollenmatrix, lokalem und G5-Discovery-Ausgangsstand sowie D-1-Vergleich und Nutzerentscheidung.

## Abhängigkeiten und Grenze

Voraussetzungen: keine; vorhandene Quellen lesend prüfen.

Nur Dokumentation und Entscheidungsgrundlage; kein Adapteraufruf, kein Import von registry.py, keine Änderung normativer v2-Schemas.
