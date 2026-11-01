# Arbeitsweise

## Zweck und Quellen

Aktuelles Ziel ist Erkenntnisgewinn aus fünf Grammatikvergleichen. Vollständige Interoperabilität ist kein aktuelles Lieferziel. Die Ordnerstruktur wurde auf Nutzerwunsch eingerichtet; technische Erweiterungen sind in ihren jeweiligen Entwürfen beschrieben, nicht bereits umgesetzt.

P0-Morphologie, versionierte P1/P2-Verträge und die P3-Implementierung bleiben an ihren bestehenden Orten. Research ändert diese Verträge nicht. Öffentliche Cube-Dokumentation ist read-only; lokale MCP-Prüfungen belegen nur die konkrete Operation am protokollierten Stand. Validierung, Berechnung, Darstellung und fachliche Gültigkeit werden getrennt ausgewiesen.

## Zuordnung zu OpenSpec

| Arbeitsdokument | Verbindung |
|---|---|
| Roadmap / Milestone / Epic | Ziele und Priorisierung; Links zu einem oder mehreren Changes |
| User Story | Nutzerbedarf und Akzeptanz; Link auf passende Requirement-/Scenario-Abschnitte |
| Task | Eintrag in der maßgeblichen `tasks.md`; eigener Detailtext nur bei Bedarf |
| BUG | Reproduktion, Erwartung und Beobachtung; falls erforderlich Link zum korrigierenden Change |
| ADR / Concept | Begründung und Alternativen; vom `design.md` verlinkt |
| Research / Evidence | Quellen, Hypothesen und Nachweise; keine automatische normative Wirkung |

Unter `openspec/specs/` werden nachvollziehbar konsolidierte Verhaltensspezifikationen gepflegt. Vorschläge stehen in `openspec/changes/<name>/`. Die beiden begrenzten Analysehilfen aus MILE-001 sind dort konsolidiert. Die übrigen bestehenden Cube-Verträge sind noch nicht migriert; der Bereich ersetzt diese Verträge nicht.

Ein Change verbindet Problem (`proposal.md`), vorgeschlagene Anforderungen/Szenarien (`specs/.../spec.md`), Lösung (`design.md`) und Arbeiten (`tasks.md`). Nach der Umsetzung werden Verhalten und Nachweise abgeglichen, die Spezifikation konsolidiert und der Change archiviert. Kleine reine Dokumentationskorrekturen benötigen keine vollständige Epic-/Story-/Task-Kette.

## Status und Identitäten

- Arbeitsstatus: `draft`, `planned`, `in_progress`, `done`, `blocked`, `superseded`. `done` braucht Ergebnis und passenden Nachweis; es bedeutet keine Produktionsfreigabe.
- ADR: `proposed`, `accepted`, `superseded`. Eine Vorlage ist keine akzeptierte Entscheidung.
- Dokument-IDs sind lokal und fortlaufend je Typ: `MILE-001`, `EPIC-001`, `US-001`, `TASK-001`, `BUG-001`, `ADR-001`, `CONCEPT-001`, `RES-001`, `EVD-001`. Archivierte IDs werden nicht wiederverwendet. Vor Vergabe den jeweiligen Ordner prüfen.
- Reihenfolge und Priorität stehen in der Roadmap; Nummern enthalten keine Prioritätsaussage.
- „Miles“ innerhalb eines Milestones sind lokale Zwischenziele, etwa `MILE-001-A/B/C`. Sie werden im Milestone beschrieben und erhalten keine konkurrierenden Roadmap-IDs.
- Bei Tasks eines Changes ist dessen `tasks.md` die führende Statusliste. Verweislisten in `docs/05-Tasks` führen keine zweite Checkboxliste.
- Neue Einträge nennen mindestens Status, Zweck, Scope, verwandte Dokumente und Abschlusskriterium. Unsichere Schätzungen und ungeprüfte Annahmen werden markiert.

## Referenzen und Einrichtungsstand

Orientierung an der am 2026-11-01 gelesenen offiziellen Dokumentation: [Getting Started](https://github.com/Fission-AI/OpenSpec/blob/main/docs/getting-started.md), [Concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md), [Config](https://openspec.dev/docs/configuration/config-yaml).

Es wurden Dateien für das Schema `spec-driven` angelegt. Die OpenSpec-CLI war im aktuellen PATH nicht vorhanden. Daher wurden weder `openspec init` noch `openspec validate` ausgeführt; Chat-Kommandos oder CLI-Integration sind nicht als installiert zu verstehen. Die Vorbereitung kann anhand der Markdown-Dateien unmittelbar weitergeführt werden.
