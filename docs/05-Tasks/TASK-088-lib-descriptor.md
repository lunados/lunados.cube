# TASK-088 — Lib-Deskriptor und 13 Cube-Zuordnungen

Ausgeführt am 2026-11-06. Führender Status in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md); [Ergebnis und Quellenpins](../10-Evidence/MILE-020/TASK-088-RESULT.md).

Story: [US-039](../04-US/US-039-owned-module-descriptors.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,25–0,5 PT (Schätzung)

## Ziel und Arbeit

Im Lib-Repo aus dem gepinnten INDEX.json und seinen Eintragsquellen einen Deskriptor ableiten. Alle 13 method_id, revision, entry path und sha256 übernehmen und gegen Bytes prüfen. Die drei konkreten Cube-Profil-/Ansichtsbezüge mit ihren Cube-Quellen belegen. Für die anderen zehn D-2 je Eintrag begründen. Nutzerentscheidung D-2: drei `cube-profile`, zehn `standalone`; P1.8-Referenzfälle mit `library_ref` liegen für alle 13 vor und zählen allein nicht als Profilnutzung.

## Abnahme und Nachweis

13/13 eindeutige Zuordnungen mit Begründung, Quelle und Entscheidungsverweis; keine zusätzliche oder verlorene Funktion. Ein reproduzierbarer Abgleich entdeckt veränderten INDEX, falschen Entry-Hash und ausgelassene Einträge. candidate-authored/candidate-extracted werden nicht ungeprüft in implemented verwandelt. Cube-Zuordnung ist ein eigenes Merkmal, kein Ersatz für Fähigkeitsstatus.

Nachweis: [TASK-088-RESULT.md](../10-Evidence/MILE-020/TASK-088-RESULT.md) mit Quellenpins und Verweisen auf owner-lokale Artefakte.

## Abhängigkeiten und Grenze

Voraussetzungen erfüllt: TASK-087; D-2 vor finaler Zuordnung entschieden.

Keine neuen Cube-Profile, Evaluatoren oder Runner. D-2 klassifiziert den Bestand; sie implementiert keine bisher ungenutzte Funktion.
