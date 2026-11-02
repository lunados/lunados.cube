# EPIC-005 — Vollständigkeit und Instanzbindung

Status: done · Milestone: [MILE-005](../02-Milestones/MILE-005-completeness-instances.md) · Voraussetzung: [EPIC-001](EPIC-001-grammar-learning.md) (Lernbilanz)

## Ergebnis

„Unbekannt“ wird in Cube nie als „leer“ oder „verletzt“ ausgegeben, und Prozessaussagen sind typisiert an ihre Instanz gebunden — prüfbar und darstellbar.

## Umfang

Ein neues P1-Profil (Vollständigkeitserklärung, Instanzbindung), eine Populationsprüfung (Profil erklärt, LIB zählt; D-6), ein neuer Printer-Stand für vier Zellzustände. Keine Änderung an P0, P1.1–P1.9, P2 oder der Morphologie.

## Akzeptanz

- Die MILE-002-Fälle ARC-02, ARC-03, DSM-03, BPMN-01, BPMN-02, BPMN-03 sind ausführbar und liefern das vorab erwartete neue Ergebnis.
- Unvollständige Erklärung führt nie zu FAIL und nie zu „geprüft leer“.
- Die Darstellung zeigt die vier Zellzustände farbfrei; „geprüft“ nur für den erklärten Umfang.

## Stories

- [US-018 — Vollständigkeit erklären und prüfen](../04-US/US-018-completeness.md)
- [US-019 — Instanzen typisiert binden](../04-US/US-019-instance-binding.md)
- [US-020 — Vier Zellzustände darstellen](../04-US/US-020-cell-states.md)
