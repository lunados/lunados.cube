# CONCEPT-001 — Analysevorbereitung

Status: done · Stand: 2026-11-01

Die Analyse soll durch drei kleine Bausteine unterstützt werden: präzise MCP-Selbstauskunft, ein gemeinsames Format für Vergleichsfälle und wiederholbare Aufrufe bestehender Prüfer mit Ergebnisprotokoll.

Die Vorbereitung beginnt mit vorhandenen PASS-/FAIL-/UNRESOLVED-Beispielen. Sie erzeugt keine neue Morphologie und keine allgemeine Ausführungssemantik. Ein generisches Analyseframework oder neue Adapter zu allen fünf Ansätzen sind dafür nicht erforderlich.

Zunächst genügt ein einfacher lokaler Prüflauf. Reale MCP-Antworten und direkte lokale Validatoraufrufe müssen im Protokoll unterscheidbar sein. Die Discovery-Korrektur wird auf die tatsächlich belegte Abweichung begrenzt.

Das Konzept bündelt die Empfehlung aus dem Gespräch. Details werden im [OpenSpec-Entwurf](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/design.md) fortgeschrieben. Grober Aufwand: 1–2 PT, mit Überschneidung zur bisherigen Analyseplanung.


Umsetzung im begrenzten Umfang abgeschlossen: [MILE-001-Nachweise](../10-Evidence/MILE-001/README.md). Die ursprüngliche Aufwandsschätzung ist keine Laufzeitmessung.
