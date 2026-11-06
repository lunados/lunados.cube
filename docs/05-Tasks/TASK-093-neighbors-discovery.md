# TASK-093 — Gepinnte neighbors additiv in G4 und G5 aufnehmen

Planungsstand: ausgearbeitet; [Umsetzung und Nachweis](../10-Evidence/MILE-020/TASK-093-RESULT.md) im lokalen Arbeitsstand. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-041](../04-US/US-041-neighbor-discovery.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,25–0,5 PT (Schätzung)

## Ziel und Arbeit

Die abgenommenen Deskriptorbytes beim jeweiligen Owner belassen. Im Cube nur einen gemeinsamen, gepinnten Referenzbestand mit ID, Quelle, Version und SHA-256 führen und als neighbors ausgeben. Discovery-Schema additiv erweitern. Gemeinsamen neighbors-Inhalt in lokale und G5-Discovery übernehmen; vorhandene Oberflächenunterschiede bleiben bestehen.

## Abnahme und Nachweis

Vorher-/Nachher-Vergleich je Oberfläche: nach Entfernen von neighbors sind alle bisherigen Felder unverändert. Die gemäß TASK-087 serialisierten neighbors-Bytes sind zwischen lokal und G5 gleich und stimmen mit dem Referenzbestand überein. Aufruf gelingt ohne Nachbar-Checkout und ohne Netzwerkzugang; keine Imports, Reads oder Aufrufe der referenzierten Module zur Discovery-Zeit. Remote-Artefakt und tatsächlich ausgelieferter Stand werden im Bericht getrennt.

Nachweis: [TASK-093-RESULT](../10-Evidence/MILE-020/TASK-093-RESULT.md) mit Quellenpins, Paritätsvergleich und Verweisen auf owner-lokale Artefakte.

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-087–090, TASK-092; TASK-091 für vollständige Grenzdokumentation.

Keine automatische Bindung, kein Fetch, kein Ausführen und keine neue Host-/Deployment-Autorisierung aus Deskriptoren. Die gesamte Discovery-Antwort wird wegen bestehender Transportunterschiede nicht künstlich gleichgesetzt.
