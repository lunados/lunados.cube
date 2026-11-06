# Cube module capabilities — MILE-020 / TASK-090

`descriptor.json` describes four independent Cube areas: pinned
P0 v9.4 reference reading, P1 descriptive structural validation, P2
projection/plan views and P3 MCP access, with local and G5 paths kept
separate. The ten declared source files are
bound by `pins.json` to exact local bytes. `implemented` refers only to the
named source-code slice; it does not prove current host or G5 deployment.

The P0/P1/P2 operations remain independent. P1 `PASS` is not truth, Admission
or Authority. P2 does not automatically invoke P1 or translate ACG to VP-03.
P3 discovery now returns the seven documentary references from the packaged
`P3/adapters/mcp-local/aiaeao_mcp_local/neighbors.json`. It does not import,
read or invoke the referenced modules. The block is built offline from the five
owner pin manifests with `build_neighbors.py --relay <TASK-090-worktree> --write`,
then checked without `--write`. The Relay Connector package source slice is not
an eighth neighbor. This descriptor makes no cross-domain overall-status claim;
the G5 source artifact does not certify the current remote endpoint.

Check its structure and pins from the Cube repository root:

```bash
python3 contracts/module-capabilities/v1/check.py --manifest module-capabilities/v1/pins.json
```

The check is offline and invokes no Cube tool, renderer or remote gateway.
