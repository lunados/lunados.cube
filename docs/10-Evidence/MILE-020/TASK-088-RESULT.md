# TASK-088 — Lib-Deskriptor und 13 Cube-Zuordnungen: Ergebnis

Stand: 2026-11-06 · Ausführung: Codex in `lunados.lib` und `lunados.cube` · [Task](../../05-Tasks/TASK-088-lib-descriptor.md) · [führender Status](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

## D-2 und gelieferte Artefakte

Der Nutzer hat D-2 entschieden: **drei `cube-profile`, zehn `standalone`**. `cube-profile` bedeutet konkrete Nutzung in einem Cube-Profil oder einer Cube-Ansicht. Ein P1.8-Referenzfall mit `library_ref` ist für **alle 13** Methoden vorhanden und allein kein solcher Nutzungsbeleg. `standalone` beschreibt einen Lib-Kandidaten mit eigenem Evaluator; es behauptet keine Host-Ausführung.

Im Owner-Repo `lunados.lib` liegen `module-capabilities/v1/descriptor.json`, `cube-relations.json`, `pins.json`, `README.md` und `scripts/build_module_capabilities.py`. Der Builder liest den exakten `INDEX.json`, alle 13 gepinnten `entry.json` und deren P1.8-Referenzfälle, verlangt 13 eindeutige bekannte IDs und gleiche Methodennamen, Revisionen, Quellstatus und Entry-Hashes. Jede D-2-Zuordnung hat im Sidecar eine einzelne Begründung. Die drei konkreten Cube-Bezüge besitzen zusätzlich Quellenpfade und SHA-256-Pins. Der Deskriptor verwendet `aiaeao.module-capabilities/1` aus TASK-087; sein Status bleibt für alle 13 `candidate`. Die präziseren INDEX-Quellstatus bleiben getrennt im Sidecar.

| Lib-Quelle und Owner-Artefakt | SHA-256 der Datei-Bytes |
|---|---|
| `INDEX.json` | `aa2cfc92bd1aeb98ae72840fe5d225b7af6932824c57adc9635d6e82b9bbcdb6` |
| `module-capabilities/v1/descriptor.json` | `cf6bc1da44ecc9d5a9d2c8c3cef1eac5c663f42d501a1e2d5751ba9a9e022f4b` |
| `module-capabilities/v1/cube-relations.json` | `2f40237634a69bc5880879df0778c2a76596c1b1fa39085c34e89dac0b125b42` |
| `module-capabilities/v1/pins.json` | `6a13e439af6f21ac18c334c44f48a6f3bdb7b172ede9093929e2cf27671c0331` |
| `scripts/build_module_capabilities.py` | `bd9e50375d31f74ad6df2026e14d268e56cad8b95c5f1dc5ce099490791350a3` |

Lib-Ausgangscommit: `284f69d67c216cc1a500e7c86d648c74805c9df3`. Die neuen Artefakte sind lokale Arbeitsänderungen, kein neuer Commit.

| `cube-profile`-Methode | Konkrete gepinnte Cube-Quelle | SHA-256 |
|---|---|---|
| `analyze.population/v1` | `P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md` | `90ba1742a973f820c7b101b35a33599855571b005da5e3647ea0299ba6e58404` |
| `project.aggregate-relations/v1` | `P2/visual-printer-cells-v1/vpcells/statements.py` | `d0a115035a7fd77609d198e7ef8c551a36cc40232004d5faa3f5ac197fdd26fd` |
| `project.aggregate-relations/v1` | `P2/visual-printer-migration-v1/vpmigration/origin.py` | `701cd2486f663b0942f78123f0636931efacb051d69c0c58a942ffd310a0352b` |
| `analyze.trace-conformance/v1` | `P2/visual-printer-instances-v1/vpinstances/trace.py` | `d9de1b99848574d4879c472f2de8d72aa5799698de265eb461aa96fbb5f2d41a` |

Die zehn `standalone`-Methoden sind `decision.compare`, `dialectics.compare`, `experimentation.plan`, `validation.assess`, `feedback.propose`, `measure.scale-check`, `claim.compose`, `impact.propagate`, `verify.reuse` und `counterworld.diff` (je `/v1`). Ihre Einzelbegründungen, Entry- und P1.8-Pins stehen in `cube-relations.json`.

## Ausgeführte Prüfung

| Befehl im Lib-Repo | Beobachtet |
|---|---|
| `python3 scripts/build_module_capabilities.py --check --cube ../lunados.cube` | `PASS`: 13/13 Einträge, drei `cube-profile`, zehn `standalone`; generierte Bytes und vier konkrete Cube-Quellenpins stimmen. Falsche Entry-Hashes, ausgelassene/zusätzliche IDs, geänderte INDEX-/Referenzfall-Bytes oder Drift der generierten Artefakte führen zum Fehlschlag. |
| `python3 ../lunados.cube/contracts/module-capabilities/v1/check.py --manifest module-capabilities/v1/pins.json` | `PASS`, keine Diagnosen; Schema, Deskriptor- und alle 15 deklarierten Quellenpins stimmen. |
| `python3 scripts/verify.py --cube ../lunados.cube` | `PASS lunados.lib: 13 entries, 159/159 checks`; darin 13/13 Cube-P1.8-Referenzfälle. |
| `git diff --check` im Lib-Repo | Bestanden. |

Der Builder läuft offline und führt keinen Lib-Evaluator aus. Die bestehende `verify.py` prüft die Lib-Evaluatoren und Referenzfälle gesondert. Ein Deskriptor oder `cube-profile` beweist weder eine produktive Integration noch aktuelle Host-Verfügbarkeit, Admission, Authority oder eine Ausführung durch den Cube. Die weiteren Owner-Deskriptoren, `neighbors` und die MILE-020-Gesamtabnahme bleiben offen.
