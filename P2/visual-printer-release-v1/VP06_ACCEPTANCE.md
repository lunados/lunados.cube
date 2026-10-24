# VP-06 – Acceptance Gates

| Gate | Requirement | Check |
| --- | --- | --- |
| G01 | VP-01–VP-05 baseline files unchanged | full-file inventory hashes, original per-stage release gates |
| G02 | 3 cube views × 5 lenses × 3 levels preserved | unchanged VP-05 90-case oracle (54 accepted / 36 correctly rejected) |
| G03 | One agent CLI for prepare/check/print/capabilities | 46 independent tests, subprocess positives and negatives |
| G04 | Source SHA and unverified identity preserved | 4 golden report/SVG pairs, tamper test, independent SHA comparison |
| G05 | Full and honest loss ledger in every result | source partitions, nested VP-05 audit, schema and tests |
| G06 | No silent ontology/relation/measurement/lens synthesis | 191 baseline unit tests + explicit failure scenarios |
| G07 | Stable machine-readable failure behavior | JSON stderr diagnostics on exit 2, no print dir for validation failure |
| G08 | Printer can be used entirely offline | Python 3.10+ stdlib, no browser/server/network |
| G09 | Static Cube integration is opt-in and **not** a callable endpoint | separate add-only overlay, explicit no-HTTP-render contract |
| G10 | Reproducible release ZIP | SHA256 ledger, file inventory locks, fresh extraction and rerun |
| G11 | Cross-platform SVG glyph parity not overstated | font and accessibility limitations documented; local Safari test manual |
| G12 | Deferred features remain out of scope | no auto multi-SVG, no 3D, no runtime authority/Admission |

**Local release gates passing does not imply deployment or external agent validation.** The public static overlay is a publication candidate only.
