# Roadmap — Lernen aus fünf Grammatikvergleichen

Status: in_progress · Stand: 2026-11-01 · MILE-001 und MILE-002 abgeschlossen

Cube an Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG untersuchen. Ergebnis sind konkrete Erkenntnisse zu Envelopes, LIB, Referenz-/Kardinalitätsprofilen, LENS/MODE/Achsen und visueller Grammatik. Lücken werden benannt, bevor Erweiterungen umgesetzt werden.

| Milestone | Ergebnis | Grober Aufwand | Nutzen | Komplexität |
|---|---|---:|---|---|
| [MILE-001 — Analyse vorbereiten](../02-Milestones/MILE-001-analysis-readiness.md) | **Abgeschlossen:** lokale Selbstauskunft, reproduzierbare Fälle und Variantenvergleich; Nachweise verlinkt | 1–2 PT | Sehr hoch | Niedrig–mittel |
| [MILE-002 — Grammatik abtasten](../02-Milestones/MILE-002-grammar-sampling.md) | **Abgeschlossen:** 15 Fallberichte, Lückenbilanz, Übergaben an MILE-003/004; [Nachweis](../10-Evidence/MILE-002/C-RESULT.md) | 2–3 PT | Sehr hoch | Mittel–hoch |
| MILE-003 — Darstellung prüfen | Relevante Unterschiede in Graph, Matrix und Sequenz; kleine Lesbarkeitsprüfung | 1–2 PT | Hoch | Mittel |
| MILE-004 — Lernbilanz | Priorisierte LIB-/Profil-/Visualisierungsvorschläge; begründete offene Kernfragen | 0,5–1 PT | Sehr hoch | Niedrig–mittel |

Die frühere reine Analyseabschätzung betrug 4–7 PT. Die 1–2 PT Vorbereitung ersetzen teilweise deren Bestandsaufnahme und manuelle Prüfarbeit; eine belastbare neue Gesamtsumme wird erst nach Abgrenzung von MILE-001 gebildet. PT sind menschliche Engineering-/Review-Tage, keine Agentenlaufzeit oder Terminverpflichtung. Die Werte sind Planungsannahmen.

## Nächster Schritt

MILE-001 und MILE-002 sind abgeschlossen. Die [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) übergibt zwölf Darstellungsanforderungen an **MILE-003** (Lesbarkeitstest zuerst für abgeleitete vs. deklarierte Kante, vier Zellzustände, Zeugenzyklus, Instanzgruppierung) und eine vorläufige Maßnahmenliste an MILE-004 (vorn: Vollständigkeit/Population, `impact.propagate`-Revision mit Zyklus-Gate, Relationsherkunft). Keine Morphologieänderung begründet. Die Entwicklung vollständiger Interoperabilität bleibt außerhalb des Auftrags.

## Maßstab

Ausdruck, Vertragsbindung, implementierte Prüfung, Darstellung und Nutzen getrennt bewerten. Eine Ablage als beliebiger Text ist kein Abdeckungsnachweis. Ein fehlendes gleichnamiges Symbol ist noch keine morphologische Lücke.

[Milestones](../02-Milestones/README.md) · [Epic](../03-Epics/EPIC-001-grammar-learning.md) · [Lernvergleich](../09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md) · [XXL-Aufwandreferenz](../09-Research/cube-grammar-2026-11-01/XXL-REFERENZ.md)
