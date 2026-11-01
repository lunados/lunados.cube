# MILE-002 — Fälle im Fallvertrag v2

Format `aiaeao.cube.research-case/2` für neu erstellte synthetische Fälle. Historische v1-Fälle unter [analysis-readiness/cases](../../analysis-readiness/cases/) bleiben unverändert und werden weiterhin gegen ihre Archivprobe geprüft.

| Fall | Art | Erwartung | Status |
|---|---|---|---|
| [A-PILOT-01-relation-declared](A-PILOT-01-relation-declared.json) | Pilot für TASK-010, kein Matrixfall | PASS, keine Diagnosen | PASS wie erwartet ([Nachweis](../../../10-Evidence/MILE-002/TASK-010-RESULT.md)); für TASK-011 auf das erweiterte Register neu gepinnt, Argumente unverändert |
| C4-01-* (3), C4-02-* (3), C4-03-* (3) | TASK-011, je Matrixfall Normalfall + zwei Kontrollen | siehe Fallberichte | alle erwartungsgemäß ([Bericht](../../../10-Evidence/MILE-002/task011-c4-report.json)) |
| ARC-01-* (2), ARC-02-* (2), ARC-03-* (3) | TASK-012; ARC-02-count-rule und ARC-03-absence-claim `not_executable` | siehe Fallberichte | ausführbare erwartungsgemäß, zwei `NOT_EXECUTED` ([Bericht](../../../10-Evidence/MILE-002/task012-archimate-report.json)) |
| DSM-01-* (3), DSM-02-* (3), DSM-03-* (3) | TASK-013; DSM-03-empty-known und DSM-03-hidden `not_executable` | siehe Fallberichte | ausführbare erwartungsgemäß, zwei `NOT_EXECUTED` ([Bericht](../../../10-Evidence/MILE-002/task013-dsm-report.json)) |

## Pflichtfelder v2

- `origin.kind = authored_synthetic`; `probe_id`/`extraction` sind verboten, damit keine historische Herkunft vorgetäuscht wird.
- `origin.authored_at`, `reference_version`, `profile_revision` (unveränderter Ausgangsstand oder benanntes Versuchsprofil).
- `origin.source_register` mit Pfad und SHA-256 des [Quellenregisters](../SOURCE-REGISTER.md); bei jeder Registeränderung wird der Fall neu gepinnt.
- `origin.rule_refs`: Regel-IDs aus dem Register (`R-…`) oder Cube-Fundstellen `cube:<Pfad>#<Abschnitt>` mit existierender Datei.
- `origin.matrix_case`: Fall-ID aus der [Fallmatrix](../CASE-MATRIX.md) oder `null` für Piloten; optional `origin.model` mit Pfad und Hash eines Fremdmodells.
- `expected.fixed_before_execution = true` und eine nicht leere `expected.rationale`.
- `invocation_kind`:
  - `local_mcp_stdio`: gleiche Eingabe-, Bindungs- und Erwartungsprüfungen wie v1 (`cube_validate`).
  - `not_executable`: `non_execution.reason`, keine Operation, keine Argumente, kein erwarteter Fachstatus. Der Runner protokolliert `NOT_EXECUTED` und ruft nichts auf.

Ein Bericht mit mindestens einem v2-Fall hat das Format `aiaeao.cube.research-run/2` und enthält `case_kinds`. Reine v1-Läufe bleiben bei `research-run/1`.

## Ausführen

Vom Repository-Root, mit der Adapter-venv:

```sh
P3/adapters/mcp-local/.venv/bin/python -B -m unittest discover -s scripts/research/tests -v
P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --cases docs/09-Research/grammar-sampling/cases --output /private/tmp/mile002-a-pilot-1
P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --output /private/tmp/mile002-a-v1-replay-1
```

Ein Agent in der Linux-VM nutzt statt der Mac-venv `.agent-env/venv/bin/python` (siehe [Agent-Testumgebung](../../../../scripts/dev/README.md)).

Der zweite Befehl führt den Piloten über eine neue lokale stdio-Verbindung aus; der dritte wiederholt die v1-Fälle unverändert. Ausgabeordner dürfen noch nicht existieren. `report.json` beider Läufe gehört nach `docs/10-Evidence/MILE-002/`.
