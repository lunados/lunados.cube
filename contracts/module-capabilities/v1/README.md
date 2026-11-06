# Documentary module capabilities v1

Status: TASK-087 format contract, 2026-11-06. This directory defines **only the common description and offline verification format** for MILE-020. Owner descriptors will be produced in TASK-088–090. The synthetic example is not an AIAEAO module or a host capability.

## Files and boundaries

- [`descriptor.schema.json`](descriptor.schema.json) defines `aiaeao.module-capabilities/1`. A module supplies an ID, its own version and owner, source identities with exact SHA-256, capability IDs/versions/statuses, input/output descriptions and exclusions. `implemented`, `candidate` and `unknown` describe a claimed source state, never current host availability. An `implemented` claim must cite a pinned evidence source; the checker can verify bytes and references, **not** whether the evidence is sufficient or the capability runs.
- [`pin-manifest.schema.json`](pin-manifest.schema.json) supplies explicit local file paths for descriptors and every declared source. It is an operator-supplied check input, not a module-owned artifact or public registry. Relative paths resolve against the manifest's directory; absolute local paths are accepted for cross-repository snapshots. URLs, globs, directory searches, network requests and a `latest` fallback are never used.
- [`neighbors.schema.json`](neighbors.schema.json) defines the additive Cube `neighbors` block. Each item carries only module ID/version, descriptor format, an owner-locator string and SHA-256 of the complete descriptor bytes. The locator is descriptive and is not fetched or trusted by discovery. The full descriptor hash lives **outside** the descriptor, avoiding a self-hash cycle. TASK-093 embeds the verified seven-item block as a single Cube-owned package asset.
- [`check.py`](check.py) checks JSON Schemas, duplicate IDs, declared source references and exact bytes. It optionally emits canonical `neighbors` bytes after a full PASS. Its only runtime dependency is `jsonschema` ([requirements](requirements.txt)); absence of that library is not reported as a successful check.

`v2_ref` is optional per capability. It can name only `aiaeao-module-contract/v2`, one of its two fixed capability IDs and version `v1`, and a cited source whose local bytes match the source SHA-256. The checker verifies the supplied v2 manifest's identity and both fixed descriptor-to-payload pairs. It does not modify or generalize Module v2. A generic MCP tool must use the new documentary format without claiming to be a v2 capability. The supplied source location and owner identity remain assertions by the descriptor producer; byte verification alone does not authenticate an owner.

The schema IDs under `aiaeao.local` identify local schemas; they do not assert that a web endpoint serves them. Generic source `version` and `artifact` fields are likewise owner assertions. The checker confirms their presence and bytes, not their meaning. A `candidate` or `unknown` capability may have empty `inputs` or `outputs` when no shape has been established; empty arrays make no claim that a real interface takes or produces nothing.

## Offline use

From the Cube repository root, with `jsonschema>=4.18,<5` available:

```sh
python3 contracts/module-capabilities/v1/check.py --manifest contracts/module-capabilities/v1/examples/pins.json
python3 contracts/module-capabilities/v1/check.py --manifest contracts/module-capabilities/v1/examples/pins.json --neighbors-only
python3 -m unittest discover -s contracts/module-capabilities/v1/tests -v
```

The example manifest lists exactly one synthetic descriptor and one synthetic source. For real owner artifacts, create an explicit local pin manifest with a path, descriptor SHA-256 and one local path for each declared source ID. The checker reads only those files. JSON output is `PASS`, `FAIL` or `UNAVAILABLE`; exit codes are respectively 0, 1 and 2. A missing local file is `UNAVAILABLE`, never a successful pin. A wrong hash, malformed shape, duplicate ID or undeclared reference is `FAIL`. If any failure and unavailability occur together, `FAIL` wins and both diagnostics remain visible. `--neighbors-only` prints bytes only on PASS.

## Canonical neighbors bytes

The checker sorts `items` by `module_id` (ASCII IDs), then serializes the **neighbors block alone** as UTF-8 JSON with sorted object keys, no insignificant whitespace, `ensure_ascii=False` and no NaN. A final newline is added by the CLI for display and is **not** part of the canonical block bytes. G4 and G5 retain different envelope fields; TASK-093 compares this block's canonical bytes while checking each old surface against its own baseline.

The format grants no admission, authority, runtime binding, execution, source truth or host availability. An owner review remains necessary before a descriptor is published as its module's description.
