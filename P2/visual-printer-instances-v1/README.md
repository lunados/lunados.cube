# VP-11 — Instance view (`cube.instances`)

Status: specified, vectors and oracle fixed (TASK-054); **no printer code yet**. Specification: [VP11_ACCEPTANCE_SPEC.md](VP11_ACCEPTANCE_SPEC.md) (MILE-009).

A declared trace for a `binding-context/9` drawn per instance: taken and not taken paths at exclusive gateways, join inputs with their status, and verdicts read from lunados.lib `analyze.trace-conformance/v1` records. The view never checks the trace itself.

| File | Content |
|---|---|
| `fixtures/i01_i34_materialized.json` | I-01…I-34: context, trace set, records; P1.13 result of every trace statement |
| `oracles/independent_i01_i34.json` | expected frames, blocks, rows, verdict lines, model lines, warnings, errors, marks |
| `fixtures/regression_vp10_0110_digests.json` | VP-10 0.11.0 outputs pinned before the G6 change |
| `scripts/materialize_i01_i34.py`, `scripts/write_oracle_i01_i34.py`, `scripts/pin_vp10_0110_digests.py` | how they were made |

All data synthetic.
