# TASK-089 — Toolbox-Bestand und Translator beschreiben

Abgeschlossen am 2026-11-06: Owner-Artefakte geprüft, D-4 durch [TASK-092](../10-Evidence/MILE-020/TASK-092-RESULT.md) geklärt. Führender Status in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md); [Ergebnis](../10-Evidence/MILE-020/TASK-089-RESULT.md).

Story: [US-039](../04-US/US-039-owned-module-descriptors.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,25–0,5 PT (Schätzung)

## Ziel und Arbeit

Den ersten Toolbox-Deskriptor im dokumentarischen Toolbox-Workspace auf aiaeao-toolbox-dns==0.1.0 begrenzen und die tatsächlichen Paketquellen im Relay-Repo pinnen. Den Translator-Deskriptor im lunados.connector-Repo aus dessen Empfehlung und vorhandenen Tabellen ableiten; Entwurf, dokumentarische Tabelle und vorhandene Implementierung unterscheiden. Herkunft der v9.4-Referenzpins aus den Tabellen nachweisen.

## Abnahme und Nachweis

Beide Deskriptoren bestehen Struktur-/Pin-Prüfung. Toolbox nennt genaue Paketversion, Input/Output, Effekte und Ausschlüsse ohne DNS-Ausführung. Translator enthält keine als implemented ausgegebene universelle Transformation. Dokumentarischer Workspace und ausführbares Paket bleiben unterscheidbar; keine angenommene Codeverlagerung.

Nachweis: [TASK-089-RESULT.md](../10-Evidence/MILE-020/TASK-089-RESULT.md) mit Quellenpins, Prüfergebnissen und Verweisen auf owner-lokale Artefakte. Die finale Zuordnung und der aktuelle Connector-Deskriptorhash stehen im [TASK-092-Ergebnis](../10-Evidence/MILE-020/TASK-092-RESULT.md).

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-087; Benennung vor Abschluss durch TASK-092.

Keine neue Toolbox-Fähigkeit, kein DNS/Netzwerk-Aufruf, keine Translator-Implementierung oder Übernahme der noch offenen Platzierungsempfehlung.
