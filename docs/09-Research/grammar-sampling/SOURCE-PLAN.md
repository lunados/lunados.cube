# Quellenplan für MILE-002

Status: planned. Folgende zuvor im Research verwendete Einstiegsquellen sind Arbeitsansätze, noch keine in diesem Milestone neu verifizierten oder vollständig gepinnten Normbaselines.

| Ansatz | Einstieg | Vor Durchführung festzulegen |
|---|---|---|
| C4 / Structurizr | [C4 Kontextsicht](https://c4model.com/diagrams/system-context), [Implied relationships](https://docs.structurizr.com/dsl/implied-relationships) | C4-Abstraktion; konkreter DSL-/Dokumentationsstand und Ableitungsstrategie |
| ArchiMate | [Open Group ArchiMate](https://www.opengroup.org/archimate-forum/archimate-overview), [Community-Einführung](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/) | Zugängliche normative Version und konkrete Relationsregel; Community-Einführung ersetzt keine Normprüfung |
| DSM / MDM | [DSM-Einführung](https://dsmweb.org/introduction-to-dsm/), [Tutorial](https://dsmweb.org/tutorial-overview/) | Verwendete Definitionen für Domäne, Richtung, Zellbedeutung und DMM/MDM-Zuordnung |
| BPMN | [OMG BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2) | Gewählte Baseline 2.0.2 und konkrete XOR-/AND-/Instanz-Regelstellen; kein pauschaler Engine-Konformitätsanspruch |
| DAG | [NetworkX DAG-Algorithmen](https://networkx.org/documentation/stable/reference/algorithms/dag.html) | Mathematische Begriffe und konkrete Algorithmusversion nur bei tatsächlicher Ausführung; stabile Definition und Implementierung trennen |

Für jede verwendete Regel: Quelle, Version oder Abrufdatum, Abschnitt, normative/dokumentarische/selbst gesetzte Geltung, relevante Aussage in eigener Formulierung. Für eigene Artefakte außerdem Hash. Urheberrechtlich geschützte Normen nicht vollständig ins Repository kopieren; bibliografische Fundstelle und eigener begrenzter Fall genügen.

Cube-/LIB-Ausgangsstand mit Datei-/Codehashes binden. Öffentliche Referenz, lokale P3-MCP-Validierung und gegebenenfalls externer LIB-Evaluator bleiben getrennte Nachweisarten. Ist eine notwendige Regelquelle nicht zugänglich, bleibt der konkrete Fall offen statt eine Konformität zu behaupten.
