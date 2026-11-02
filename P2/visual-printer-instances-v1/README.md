# VP-11 — Instance view (`cube.instances`)

Status: implemented locally (TASK-055): I-01…I-34 34/34 as the oracle; VP-10 0.11.0 still byte-identical. Specification: [VP11_ACCEPTANCE_SPEC.md](VP11_ACCEPTANCE_SPEC.md) (MILE-009).

A declared trace for a `binding-context/9` drawn per instance: taken and not taken paths at exclusive gateways, join inputs with their status, and verdicts read from lunados.lib `analyze.trace-conformance/v1` records. The view never checks the trace itself.

| File | Content |
|---|---|
| `fixtures/i01_i34_materialized.json` | I-01…I-34: context, trace set, records; P1.13 result of every trace statement |
| `oracles/independent_i01_i34.json` | expected frames, blocks, rows, verdict lines, model lines, warnings, errors, marks |
| `fixtures/regression_vp10_0110_digests.json` | VP-10 0.11.0 outputs pinned before the G6 change |
| `vpinstances/` | the printer: `trace.py` (inputs, RC-1…RC-3), `view.py` (drawing, ledger, report, audit), `api.py` (G6), `__main__.py` (CLI) |
| `scripts/run_vectors.py`, `tests/test_vp11.py` | vectors against the oracle; tests |
| `scripts/materialize_i01_i34.py`, `scripts/write_oracle_i01_i34.py`, `scripts/pin_vp10_0110_digests.py` | how they were made |

```
python3 -m vpinstances from-trace --context ctx9.json --trace trace.json [--record r.json …] --out in.json
python3 -m vpinstances print-instances --input in.json --out <dir> [--locale de]
python3 -m vpinstances check-instances --input in.json
```

All data synthetic.
