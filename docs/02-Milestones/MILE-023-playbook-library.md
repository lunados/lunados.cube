# MILE-023 — Playbook-Library

Status: **geplant (Entwurf)** · Stand: 2026-11-06 · Abhängig von [MILE-020](MILE-020-module-capability-descriptors.md) und [MILE-021](MILE-021-explorer-contract-binding.md); Verbindung zu [MILE-022](MILE-022-workflow-builder.md) · Betrifft: lunados.playbooks (neu), lunados.explorer, agent-relay-poc-v3

## Ziel und Entscheidung

Eine Bibliothek wiederverwendbarer Vorgehen: was getan werden soll, in welcher Reihenfolge, mit welchen Modulen und wie man das Ergebnis prüft. Ein Playbook schreibt vor; der Explorer beschreibt, was in einem System ist. Deshalb wird die Explorer-Methode **ein** Playbook in der Library, nicht die Library selbst.

Name **Playbook** statt Runbook: „Runbook“ ist im Relay-Repo belegt (`human-epic-runbook/v1` und `/v2`, `RUNBOOK_EPIC.md`). Runbooks werden ein Eintragstyp der Library.

Zusammenspiel: Playbook (was) → Workflow Builder (wie, als Pipeline mit Modulzuordnung) → Cube (Form) → Relay (Zulassung, Ausführung).

## Abgrenzung

- Die Cases des Explorers (zum Beispiel `la_luna_v3`, Relay-Metriken) sind Projektdaten und bleiben im Explorer-Repository.
- Starter Kits: Nur ihr Inhalt (Vorlagen Hello World und News Reporter) gehört in die Library. `agentctl starter-kit-create` mit Freigabe und Prüfung des Zielordners bleibt im Relay-Repo, weil der Befehl Dateien anlegt.

## Arbeitsumfang

1. **Eigenes Repository** (D-1, Arbeitsname `lunados.playbooks`) und **Eintragsformat** (D-2): je Playbook Zweck, Auslöser, Schritte, beteiligte Module (über MILE-020-Deskriptoren), Verweis auf die erzeugbare TOML-Dateiart, Prüfung des Ergebnisses.
2. **Erste Einträge:** „Migration erfassen“ (Explorer-Methode, Verweis auf gepinnten Explorer-Stand), „Starter Kit Hello World“, „Starter Kit News Reporter“.
3. **Starter-Kit-Vorlagen:** zunächst per Hash auf `starter_kit.py` und die Vorlagen im Relay-Repo verweisen; eine Verlagerung der Vorlagendateien erst nach Entscheidung (D-3).
4. **Runbooks** als Eintragstyp mit Verweis auf `human-epic-runbook/v1` bzw. `/v2`.
5. Jedes Playbook nennt die TOML-Dateiart, die der Workflow Builder daraus erzeugt.

## Entscheidungen

| ID | Frage | Optionen |
|---|---|---|
| D-1 | Ablage der Library | **Entschieden (Nutzer, 2026-11-06): eigenes Repository**, Arbeitsname `lunados.playbooks`. Eigener Eintragsvertrag, unabhängig vom Lib-Vertrag mit Evaluator, Oracle und Cases. |
| D-2 | Eintragsformat | Markdown mit Frontmatter · JSON mit erzeugter Ansicht (wie Explorer-Sheets) |
| D-3 | Starter-Kit-Vorlagen | im Relay-Repo lassen und verweisen · in die Library verlagern, Relay pinnt sie |

## Abnahme

- [ ] Repository angelegt; Eintragsformat entschieden, mit Schema und Prüfskript.
- [ ] Drei erste Playbooks liegen vor und verweisen gepinnt auf ihre Quellen.
- [ ] Mindestens ein Playbook führt über den Workflow Builder zu einer Pipeline, die Cube-Prüfung und Relay-Preflight besteht (sobald MILE-022 so weit ist).
- [ ] Keine Projektdaten aus Explorer-Cases in der Library.

## Nicht in MILE-023

Ausführung von Playbooks; Änderung des Starter-Kit-Erzeugungsbefehls; Verschieben der Explorer-Cases.

## Aufwand

Schätzung 2–3 PT.
