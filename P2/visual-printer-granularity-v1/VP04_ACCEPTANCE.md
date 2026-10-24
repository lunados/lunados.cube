# VP-04 · Acceptance and Gate Matrix

| AC | Requirement | Verification |
|---|---|---|
| VP04-AC-01 | VP01, VP02, VP03 snapshot unchanged and regressions pass | `scripts/verify_vp04.py` invokes frozen `verify_vp03.py` |
| VP04-AC-02 | Three exact level identifiers and explicit typed budgets | unit negative cases and request schema |
| VP04-AC-03 | All three Cube views, not Planner aliases | fixture matrix, namespace negative |
| VP04-AC-04 | Source bundles are immutable, checksum locked | direct comparison, tamper tests |
| VP04-AC-05 | No invented edge, parent, claim, measurement or anchor | subset invariant tests |
| VP04-AC-06 | Source order stable; tree ancestry and edge focus preserved | tree and edge remapping tests |
| VP04-AC-07 | Bar maximum preserved; line contiguous; axis rescale flagged | chart tests, report and SVG text |
| VP04-AC-08 | All omissions documented in JSON and SVG metadata | completeness and ledger tests |
| VP04-AC-09 | Five VP03 lenses remain opt-in declarations; no AI inference | lens validation and no-target warning |
| VP04-AC-10 | `detail` cannot truncate, `reject` cannot overflow | negative tests |
| VP04-AC-11 | Byte-identical output, no unsafe SVG injection/tags | 20 SVG/report goldens and XML guard |
| VP04-AC-12 | Standalone CLI and local static preview; no new app/server | CLI subprocess smoke, `granularity_preview.html` |
| VP04-AC-13 | Reports conform to JSON Schema Draft 2020-12 | optional independent `jsonschema` oracle (present in build) |
| VP04-AC-14 | Full ZIP checksums and fresh extraction reproducible | integrity ledger and fresh-release QA |
| VP04-AC-15 | No P1 authority, witness, truth or admission claims | report status assertions; manual review |

**Local limitations:** Different SVG/font engines may render math Unicode anchors differently. Safari/macOS, Claude/Grok interaction and human legibility at extreme densities are **not** automatically proven. Source fixtures are authored, not empirically witnessed. No 3D work. No new Cube-hosted endpoint in VP04.

## Gate / decision

- `2D_GO`: local tests and user visual review pass; proceed with VP05 combinations.
- `2D_REVISE`: charts, hierarchy visibility, labeling or glyphs need corrections within 2D.
- `2D_STOP`: reductions systematically imply undocumented or misleading semantic facts.

Passing automated tests does not decide the human visual review.
