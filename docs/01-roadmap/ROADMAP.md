# Roadmap — Lernen aus fünf Grammatikvergleichen

Status: in_progress · Stand: 2026-11-01 · MILE-001 abgeschlossen

Cube an Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG untersuchen. Ergebnis sind konkrete Erkenntnisse zu Envelopes, LIB, Referenz-/Kardinalitätsprofilen, LENS/MODE/Achsen und visueller Grammatik. Lücken werden benannt, bevor Erweiterungen umgesetzt werden.

| Milestone | Ergebnis | Grober Aufwand | Nutzen | Komplexität |
|---|---|---:|---|---|
| [MILE-001 — Analyse vorbereiten](../02-Milestones/MILE-001-analysis-readiness.md) | **Abgeschlossen:** lokale Selbstauskunft, reproduzierbare Fälle und Variantenvergleich; Nachweise verlinkt | 1–2 PT | Sehr hoch | Niedrig–mittel |
| [MILE-002 — Grammatik abtasten](../02-Milestones/MILE-002-grammar-sampling.md) | Je Ansatz zwei Normalfälle und ein Gegenfall; Versions- und Vertragsbindung | 2–3 PT | Sehr hoch | Mittel–hoch |
| MILE-003 — Darstellung prüfen | Relevante Unterschiede in Graph, Matrix und Sequenz; kleine Lesbarkeitsprüfung | 1–2 PT | Hoch | Mittel |
| MILE-004 — Lernbilanz | Priorisierte LIB-/Profil-/Visualisierungsvorschläge; begründete offene Kernfragen | 0,5–1 PT | Sehr hoch | Niedrig–mittel |

Die frühere reine Analyseabschätzung betrug 4–7 PT. Die 1–2 PT Vorbereitung ersetzen teilweise deren Bestandsaufnahme und manuelle Prüfarbeit; eine belastbare neue Gesamtsumme wird erst nach Abgrenzung von MILE-001 gebildet. PT sind menschliche Engineering-/Review-Tage, keine Agentenlaufzeit oder Terminverpflichtung. Die Werte sind Planungsannahmen.

## Nächster Schritt

[MILE-001](../02-Milestones/MILE-001-analysis-readiness.md) ist abgeschlossen. Der [Bereitschaftsnachweis](../10-Evidence/MILE-001/C-RESULT.md) enthält Wiederholungsanleitung und Grenzen. MILE-002 ist jetzt in drei Chargen mit US-005–011 und TASK-009–017 ausgearbeitet. [TASK-009 — Quellenbasis](../05-Tasks/TASK-009-source-baselines.md) ist erledigt ([Quellenregister](../09-Research/grammar-sampling/SOURCE-REGISTER.md)). [TASK-010](../05-Tasks/TASK-010-authored-case-provenance.md) ist erledigt ([Nachweis](../10-Evidence/MILE-002/TASK-010-RESULT.md)); damit ist MILE-002-A abgeschlossen. Von den fünf Dreierpaketen sind C4 ([TASK-011](../05-Tasks/TASK-011-c4-three-cases.md)) ArchiMate ([TASK-012](../05-Tasks/TASK-012-archimate-three-cases.md)) DSM/MDM ([TASK-013](../05-Tasks/TASK-013-dsm-mdm-three-cases.md)) und DAG ([TASK-015](../05-Tasks/TASK-015-dag-three-cases.md)) erledigt; offen ist BPMN ([TASK-014](../05-Tasks/TASK-014-bpmn-three-cases.md)), das auf den Spezifikationstext wartet. Die Entwicklung vollständiger Interoperabilität bleibt außerhalb des Auftrags.

## Maßstab

Ausdruck, Vertragsbindung, implementierte Prüfung, Darstellung und Nutzen getrennt bewerten. Eine Ablage als beliebiger Text ist kein Abdeckungsnachweis. Ein fehlendes gleichnamiges Symbol ist noch keine morphologische Lücke.

[Milestones](../02-Milestones/README.md) · [Epic](../03-Epics/EPIC-001-grammar-learning.md) · [Lernvergleich](../09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md) · [XXL-Aufwandreferenz](../09-Research/cube-grammar-2026-11-01/XXL-REFERENZ.md)
