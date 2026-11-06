# TASK-090 — Cube and Relay role descriptors: result

Date: 2026-11-06 · Executor and file writer: Codex · [Task](../../05-Tasks/TASK-090-cube-relay-descriptors.md) · [execution checklist](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

## Local bases and owner artifacts

The Cube descriptor is owner-local at `lunados.cube/module-capabilities/v1/`. It separates P0 reference reading, P1 descriptive validation, P2 projection, P3 local MCP, and P3 G5 source access into five narrowly stated capabilities. P0/P1/P2 remain independent. `implemented` means the named source-code slice exists; it does not certify a current host or remote deployment.

Relay `main` at `6d6f62d234696e85f8618da83d31ac9a2915a918` was 22 commits ahead of `origin/main` and had four unrelated untracked research paths. The required `agentctl git-sync-check --strict` reported `synced: false`. The user explicitly authorized that reviewed local HEAD as the base for an isolated TASK-090 worktree on 2026-11-06. The branch `agent/codex/task-090-mile-020` and worktree `.agent-worktrees/codex-task-090-mile-020/` contain only the new `module-capabilities/` owner artifacts. No Relay main file, existing research path, GitHub ref, commit, merge, push, or deployment was changed by this task.

The Relay worktree has three logical role descriptors in `module-capabilities/v1/{core-server,server-gui,web-app}/descriptor.json`, checked together by `module-capabilities/v1/pins.json`. The existing `aiaeao-connector==0.1.0` package has a separate source-slice descriptor and pin manifest under `module-capabilities/v1/connector-package/`. That package is **not** an eighth logical module or an extra Cube neighbor.

| New owner artifact | SHA-256 of exact bytes |
|---|---|
| Cube `module-capabilities/v1/descriptor.json` | `7232a200da2c4925ad8b5be5f021215a913e3445c06e54a6414986a9595a4ab4` |
| Cube `module-capabilities/v1/pins.json` | `db09c2e7c35d87dfb3caee5f8c6c6912f5e9109e4f103c359ea098064eae3bf2` |
| Relay `core-server/descriptor.json` | `a622465268c692f6b4ab23767de448d6d0542c2ee76dd118b8de5f1a79d9728b` |
| Relay `server-gui/descriptor.json` | `88fd83549b5750d3eb6777f78dcd850cd1113c9c0025ef22af4985604a17927a` |
| Relay `web-app/descriptor.json` | `f7a5f1792d99c889eefe5524c9da00956b53890f00b6d513118181d82c1779f4` |
| Relay logical `pins.json` | `9431f3d1244a69796561378964d4d19938221fa77204956f5c37674d2fe3be17` |
| Relay `connector-package/descriptor.json` | `796c4cb8c8ff7a907435dbcf094b9bb7294d9980785f7e004416abf6d12ce3bd` |
| Relay `connector-package/pins.json` | `f4401f26467a10a6842d136adfbab0c8cf91507cdf7e4df29f64cb706885c80f` |

## Seven-role coverage at this local state

| MILE-071 logical role | Owner descriptor and status boundary |
|---|---|
| Core/Server | Relay `aiaeao.core-server`: bounded Module v1 data-only inspection and canonical record models are source-implemented; neither supplies a universal Admission API nor proves a live canonical host. |
| Server GUI | Relay `aiaeao.server-gui`: selected operator view is `candidate` despite shared App/UI source; no separate service, policy store, or qualified connected host is claimed. |
| Web App / Application Service | Relay `aiaeao.web-app`: one bounded document-summary journey is source-implemented; the server-planner view is `candidate`. App purpose and display do not become Core admission or provider transport authority. |
| Connector | `lunados.connector` owner descriptor from TASK-089/092, with internal `translator/` area. Relay's `aiaeao-connector` package descriptor is a bounded source slice for this role, at its present source location. |
| Toolbox | `lunados.toolbox` owner descriptor from TASK-089, limited to the existing DNS fixture package. |
| Pure Cube | `lunados.cube` owner descriptor above: P0/P1/P2 and separate P3 local/G5 source paths. |
| Functions Library | `lunados.lib` owner descriptor from TASK-088: 13 candidate methods and 3/10 Cube relation split. |

The Relay package descriptor pins Module Contract v2 and its exact two descriptor types, packaged v2 bytes, Companion v1/v2 manifests, package code, three root derivatives, package register, and the adapter registry. `registry.py` is a name inventory, not evidence of a running provider. The v2 `structured-inspection/v1` claim is limited to bounded no-effect control; `artifact-observation/v1` is selected synthetic local fixture replay, not an actual foreign observation. A Receipt does not prove observed start; technical Result/Outcome do not confer project Verification, Completion, or Satisfaction. The existing package location is not moved to the future `lunados.connector` target repository.

## Focused validation and limits

The TASK-087 checker returned `PASS` with no diagnostics for all six current manifests: Cube, Lib, Toolbox, Connector, Relay logical roles, and Relay Connector package. The Cube descriptor binds ten exact source files; the four Relay descriptors bind 29 source pins. The checker validated descriptor/schema shape, exact local bytes, source references, uniqueness, and both exact Module-v2 references. A separate local aggregation of the five **logical-role** manifests produced seven unique module IDs (`aiaeao.core-server`, `aiaeao.server-gui`, `aiaeao.web-app`, `lunados.connector`, `lunados.cube`, `lunados.lib`, `lunados.toolbox`); `aiaeao-connector` was excluded as a package slice. This aggregation was a check, not an implemented neighbor response. `git diff --check` passed in Cube. `agentctl git-status` in the isolated Relay worktree reported branch `agent/codex/task-090-mile-020`, expected dirty state from the new uncommitted `module-capabilities/` directory, and no upstream.

These are offline, source-bound development checks. No Relay/Cube module, adapter, provider, UI, remote gateway, or DNS path was invoked; no full suite, independent QA, installed package check, host qualification, G5 deployment or current remote availability is claimed. Relay integration into main remains separate from this TASK-090 delivery. TASK-093 must decide and pin the actual seven-neighbor list from the owner descriptors, excluding the extra package source-slice descriptor.
