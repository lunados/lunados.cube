# MILE-001 — Cube für den Grammatikvergleich vorbereiten

Status: done · Stand: 2026-11-01 · Umfang: Analysehilfen vor dem eigentlichen Fünfervergleich

## Ergebnis

Cube weist seine lokal verfügbaren Fähigkeiten präzise aus. Vorhandene Vergleichsfälle können mit fixierter Erwartung wiederholt und Ausgangsstand/Variante getrennt beurteilt werden. Das verbessert den Erkenntnisgewinn der anschließenden Analyse.

Alle drei Chargen sind umgesetzt und geprüft. [Abschluss und Grenzen](../10-Evidence/MILE-001/C-RESULT.md). [Nachweis A](../10-Evidence/MILE-001/A-RESULT.md). „Miles“ bezeichnet hier drei lokale Zwischenziele innerhalb dieses Milestones, keine zusätzlichen übergeordneten Roadmap-Milestones.

## Miles und Abschlusskriterien

| Mile | Ergebnis | Abschlussnachweis | Arbeit |
|---|---|---|---|
| **MILE-001-A — Fähigkeiten sichtbar** | Lokale Discovery entspricht vorhandenen Operationen und Kontext-/Profilversionen | Quellengebundene Capability-Matrix, echte lokale Discovery-Probe, geschützte Legacy-/G4-Ausgaben unverändert | EPIC-002; TASK-001–002 |
| **MILE-001-B — Fälle wiederholbar** | PASS, FAIL und UNRESOLVED laufen im selben nachvollziehbaren Verfahren | Fixierte Fixtures, zwei Wiederholungen, Rohantworten und getrennte Dimensionen; Ausfall-/Konfigurationskontrollen | EPIC-003; TASK-003–004, TASK-006 |
| **MILE-001-C — Vergleich und Übergabe** | Eine minimale Profilvariante lässt sich gegen den unveränderten Ausgangsfall vergleichen | Beide Eingaben/Ergebnisse, frische lokale Verbindung, vollständige Abdeckungsmatrix und Arbeitsanleitung | EPIC-003; TASK-005, TASK-007–008 |

MILE-001-A/B/C sind abgeschlossen. Die folgende Reihenfolge beschreibt die durchgeführte Arbeit. B kann nach der Fallauswahl beginnen, während A bearbeitet wird. C benötigt den gemeinsamen Stand von A und B.

## Epics und Stories

- [EPIC-002 — Verlässliche lokale Selbstauskunft](../03-Epics/EPIC-002-local-capability-discovery.md): US-002, TASK-001–002.
- [EPIC-003 — Reproduzierbare Vergleichsprüfung](../03-Epics/EPIC-003-reproducible-comparison.md): US-003, US-001 und US-004, TASK-003–008.

Der bisherige [EPIC-001](../03-Epics/EPIC-001-grammar-learning.md) enthält den späteren eigentlichen Lernvergleich (MILE-002–004) und verwendet diese Vorbereitung als Voraussetzung. Die bestehende US-001 bleibt erhalten und gehört jetzt zu EPIC-003.

## Aufwand, Nutzen und Grenzen

**8–16 Engineering-/Review-Stunden = grob 1–2 PT à 8 h.** EPIC-002: 2–4 h; EPIC-003: 6–12 h. Die Schätzung setzt vorhandene lokale Python-/MCP-Laufzeit, wiederverwendbare Fixtures und additive Discovery-Metadaten voraus. Fehlende Abhängigkeiten oder ein notwendiger Vertragsbruch erfordern eine neue Schätzung; daraus entsteht keine automatische Erweiterung des Umfangs.

Erwarteter Nutzen: sehr hoch, weil alle Folgefälle dieselbe nachvollziehbare Grundlage erhalten. Komplexität: niedrig–mittel; wichtigste Unsicherheit ist die Kompatibilität der Discovery-Ergänzung.

Keine neue Morphologie, kein neuer Envelope-Typ, keine neue LIB-Methode und keine fünf Fremdtool-Adapter in diesem Milestone. Ausführungs-, Wahrheits- und Autoritätsaussagen bleiben getrennt. Public-Read-only ist eine Quelle und kein Validierungsnachweis.

## Nachverfolgung

Führender Aufgabenstatus: [OpenSpec tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md). Anforderungen und Zuordnung: [TRACEABILITY.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/TRACEABILITY.md). Der aktuelle Ausführungsstand steht in der führenden Checkliste; Nachweise sind beim jeweiligen Abschluss verlinkt.
