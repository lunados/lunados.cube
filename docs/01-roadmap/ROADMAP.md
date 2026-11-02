# Roadmap — Lernen aus fünf Grammatikvergleichen

Status: in_progress · Stand: 2026-11-02 · MILE-001 bis MILE-007 abgeschlossen; MILE-008 geplant

Cube an Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG untersuchen. Ergebnis sind konkrete Erkenntnisse zu Envelopes, LIB, Referenz-/Kardinalitätsprofilen, LENS/MODE/Achsen und visueller Grammatik. Lücken werden benannt, bevor Erweiterungen umgesetzt werden.

| Milestone | Ergebnis | Grober Aufwand | Nutzen | Komplexität |
|---|---|---:|---|---|
| [MILE-001 — Analyse vorbereiten](../02-Milestones/MILE-001-analysis-readiness.md) | **Abgeschlossen:** lokale Selbstauskunft, reproduzierbare Fälle und Variantenvergleich; Nachweise verlinkt | 1–2 PT | Sehr hoch | Niedrig–mittel |
| [MILE-002 — Grammatik abtasten](../02-Milestones/MILE-002-grammar-sampling.md) | **Abgeschlossen und abgenommen:** 15 Fallberichte, Lückenbilanz, Übergaben an MILE-003/004; [Nachweis](../10-Evidence/MILE-002/C-RESULT.md) | 2–3 PT | Sehr hoch | Mittel–hoch |
| [MILE-003 — Darstellung prüfen](../02-Milestones/MILE-003-visual-check.md) | **Abgeschlossen und abgenommen:** Inventur V-01–V-12, Printer-Paare und Mockups, Agenten-Vorprüfung mit blinder Zweitprüfung (kein Menschentest, D-1), Kandidatenregeln an MILE-004; [Nachweis](../10-Evidence/MILE-003/C-RESULT.md) | 1–2 PT | Hoch | Mittel |
| [MILE-004 — Lernbilanz](../02-Milestones/MILE-004-learning-balance.md) | **Abgeschlossen:** Proben zu Envelope und LENS/MODE/Achsen (keine Erweiterung begründet), Lernbilanz für Architektursichten und Prozessspuren, Plan MILE-005; [Nachweis](../10-Evidence/MILE-004/C-RESULT.md) | 1–1,5 PT | Sehr hoch | Niedrig–mittel |
| [MILE-005 — Vollständigkeit und Instanzbindung](../02-Milestones/MILE-005-completeness-instances.md) | **Abgeschlossen:** P1.12 (Abdeckung, Instanzbindung), lunados.lib `analyze.population/v1`, VP-10 Zellzustände, G4/G6, Wiederholung 7/7; [Nachweis](../10-Evidence/MILE-005/C-RESULT.md) | 5–7 PT | Sehr hoch | Mittel–hoch |
| [MILE-006 — Remote prüfen und Matrix ordnen](../02-Milestones/MILE-006-remote-and-order.md) | **Abgeschlossen:** `/8` im G5-Remote mit Host-Abnahme, VP-10 0.10.1 mit Achsenreihenfolge, kurze Sichtprüfung; [Nachweis](../10-Evidence/MILE-006/C-RESULT.md) | 1,75–2,25 PT | Hoch | Niedrig–mittel |
| [MILE-007 — Aussagenmengen ohne Plan](../02-Milestones/MILE-007-statement-sets.md) | **Abgeschlossen:** Aussagenmengen ohne Plan als Matrix (VP-10 0.11.0), lunados.lib `project.aggregate-relations/v1` mit Quellenspur und Verlustbericht, Sichtprüfung; [Nachweis](../10-Evidence/MILE-007/C-RESULT.md) | 2–3 PT | Hoch | Mittel |
| [MILE-008 — Kontrollfluss und Spurkonformität](../02-Milestones/MILE-008-control-flow.md) | Geplant (G-07): Kontrollfluss-Profil P1.13, LIB-Spurprüfung je Instanz, Wiederholung BPMN-01/02 | 4–5,5 PT | Hoch bei Prozess-Anwendungsfall | Mittel–hoch |

Die frühere reine Analyseabschätzung betrug 4–7 PT. Die 1–2 PT Vorbereitung ersetzen teilweise deren Bestandsaufnahme und manuelle Prüfarbeit; eine belastbare neue Gesamtsumme wird erst nach Abgrenzung von MILE-001 gebildet. PT sind menschliche Engineering-/Review-Tage, keine Agentenlaufzeit oder Terminverpflichtung. Die Werte sind Planungsannahmen.

## Nächster Schritt

MILE-001 bis MILE-007 sind abgeschlossen; die sieben Leitfragen sind in der [Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md) beantwortet oder präzise offen. Weder Envelope noch Morphologie brauchen eine Erweiterung. MILE-005 hat Vollständigkeit und Instanzbindung umgesetzt, MILE-006 `/8` remote verfügbar gemacht und die Matrix geordnet. [MILE-007](../02-Milestones/MILE-007-statement-sets.md) hat Aussagenmengen ohne Migrationsplan darstellbar gemacht und Beziehungen mit Quellenspur und Verlustbericht verdichtet (PO-7, G-03). **[MILE-008](../02-Milestones/MILE-008-control-flow.md)** ist geplant: Kontrollfluss und Spurkonformität (G-07). Danach folgt VR-12 (Instanzsicht).

## Maßstab

Ausdruck, Vertragsbindung, implementierte Prüfung, Darstellung und Nutzen getrennt bewerten. Eine Ablage als beliebiger Text ist kein Abdeckungsnachweis. Ein fehlendes gleichnamiges Symbol ist noch keine morphologische Lücke.

[Milestones](../02-Milestones/README.md) · [Epic](../03-Epics/EPIC-001-grammar-learning.md) · [Lernvergleich](../09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md) · [XXL-Aufwandreferenz](../09-Research/cube-grammar-2026-11-01/XXL-REFERENZ.md)
