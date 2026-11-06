# MILE-020 — Abnahmespur

Die IDs AC-1–6 bezeichnen die sechs Abnahmezeilen der Mile in ihrer Reihenfolge; keine zusätzlichen Produktanforderungen.

| Mile-Kriterium | Story | Tasks | Prüfgegenstand |
|---|---|---|---|
| AC-1 Format, Schema, Prüfskript; D-1 | US-038 | TASK-086/087 | Entscheidung; Schema-Pin; positive/negative Offline-Fälle, Versions- und Hashfehler |
| AC-2 Deskriptor je Modul mit Version/Hash | US-039 | TASK-088/089/090 | Owner-/Rollenmatrix, alle Datei- und Quellenpins, getrennte Statusbelege |
| AC-3 neighbors lokal/G5 bytegleich, Bestand unverändert | US-041 | TASK-093/094 | Serialisierte neighbors-Bytes; per-Oberfläche Vorher/Nachher; keine Nachbarzugriffe; realer G5-Stand oder offene Abnahme |
| AC-4 13 Lib-Zuordnungen | US-039 | TASK-088 | INDEX-Pin, 13/13-Abgleich, D-2 pro Eintrag; vorhandene drei library_ref-Belege |
| AC-5 D-3-ADR | US-040 | TASK-091 | ADR mit Hash-/Pfadtabelle und dokumentierter MILE-071-Folge |
| AC-6 eindeutige Connector-Namen | US-040 | TASK-092 | D-4, Deskriptor-/Space-Review ohne technische Umbenennung |

[TASK-094](../../../../docs/10-Evidence/MILE-020/TASK-094-RESULT.md) dokumentiert alle sechs Kriterien als PASS für den benannten Stand. [CLOSURE](../../../../docs/10-Evidence/MILE-020/CLOSURE.md) dokumentiert den formalen Abschluss und die Grenze zur späteren Relay-Integration.
