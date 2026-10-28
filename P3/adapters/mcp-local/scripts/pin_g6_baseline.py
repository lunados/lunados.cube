#!/usr/bin/env python3
"""G6 G6-01 / K-03: pin, before any G6 code, the outputs G6 must not change.

- check-panels results (canonical JSON) for panel directories of VP-07 (0.7.1…0.7.4), VP-08 and VP-09 (0.9.0, 0.9.1);
- the legacy card `cube_get_capabilities` and the G4 `discover_surface()` (also the base of the G5 surface).

`--write` once on the unchanged code; afterwards the default run compares.
"""
from __future__ import annotations
import hashlib, json, sys, tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]; ROOT = BASE.parents[2]
sys.dont_write_bytecode = True
for p in ('P2/visual-printer-migration-v1', 'P2/visual-printer-sequence-v1', 'P2/visual-printer-axes-v1'):
    sys.path.insert(0, str(ROOT/p))
sys.path.insert(0, str(BASE))
import vpmigration, vpsequence, vpaxes  # noqa: E402
from vpmigration.common import publish_dir, encode  # noqa: E402
from aiaeao_mcp_local import bridge, surface  # noqa: E402

OUT = BASE/'tests/g6/baseline_digests.json'
MIG, SEQ, AX = ROOT/'P2/visual-printer-migration-v1/fixtures', ROOT/'P2/visual-printer-sequence-v1/fixtures', ROOT/'P2/visual-printer-axes-v1/fixtures'
FLOW = ('cube.flow', 'subject', 'standard', 'cube.lens.execution')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def cases():
    """(name, printer module, report, files) for every pinned panel directory."""
    j = lambda p: json.loads(p.read_text('utf-8'))  # noqa: E731
    g71, g72, g73, g74 = j(MIG/'golden_v071.json'), j(MIG/'golden_v072.json'), j(MIG/'golden_v073.json'), j(MIG/'golden_v074.json')
    s71, _ = vpmigration.from_plan(g71['context'], 'mp-acme', tracks=g71['tracks'])
    yield 'vp07-071-phases-track-subject', vpmigration, *vpmigration.print_panels(s71, 'cube.phases', 'track,subject', 'standard')
    yield 'vp07-071-flow-subject', vpmigration, *vpmigration.print_panels(s71, *FLOW)
    s72, _ = vpmigration.from_plan(g72['context'], 'mp-acme', tracks=g72['tracks'], layers=g72['layers'])
    yield 'vp07-072-phases-layer', vpmigration, *vpmigration.print_panels(s72, 'cube.phases', 'layer', 'standard')
    s73, _ = vpmigration.from_plan(g73['context'], g73['plan_id'])
    yield 'vp07-073-phases-subject', vpmigration, *vpmigration.print_panels(s73, 'cube.phases', 'subject', 'standard')
    s74, _ = vpmigration.from_plan(g74['context'], g74['plan_id'], profile=g74['profile'])
    yield 'vp07-074-phases-method', vpmigration, *vpmigration.print_panels(s74, 'cube.phases', 'method', 'standard')
    yield 'vp07-074-flow-subject', vpmigration, *vpmigration.print_panels(s74, *FLOW)
    gs = j(SEQ/'golden_sequence.json')
    yield 'vp08-golden-trigger', vpsequence, *vpsequence.print_panels(gs['sequence_source'], 'trigger', 'standard')
    yield 'vp08-golden-use-case', vpsequence, *vpsequence.print_panels(gs['sequence_source'], 'use_case', 'standard')
    ga = j(AX/'golden_axes.json')
    d90, _ = vpaxes.from_plan(ga['context'], ga['plan_id'])
    yield 'vp09-090-z-t', vpaxes, *vpaxes.print_panels(d90, 'Z:referent', 'T', 'standard')
    d91, _ = vpaxes.from_plan(ga['context'], ga['plan_id'], profile='P2-VP-AXES/0.9.1')
    yield 'vp09-091-f-z', vpaxes, *vpaxes.print_panels(d91, 'F', 'Z:referent', 'standard')


def collect():
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, mod, rep, files in cases():
            d = publish_dir(files, Path(tmp)/name)
            out['check:'+name] = sha(encode(mod.check_panels(d)))
            out['files:'+name] = sha(encode({k: sha(v) for k, v in sorted(files.items())}))
    out['legacy:cube_get_capabilities'] = sha(encode(bridge.get_capabilities()))
    out['g4:discover_surface'] = sha(encode(surface.discover_surface()))
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.g6-baseline-digests/1', 'pinned_before': 'any G6 runtime code (G6-01, K-03)',
                                   'digests': cur}, sort_keys=True, indent=1)+'\n', 'utf-8')
        print('pinned', len(cur), 'outputs'); return
    want = json.loads(OUT.read_text('utf-8'))['digests']
    bad = [k for k in want if want[k] != cur.get(k)]
    for k in bad:
        print('DIFF', k)
    print(f'{len(want)-len(bad)}/{len(want)} G6 baseline outputs byte-identical')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
