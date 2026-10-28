#!/usr/bin/env python3
"""VP-07.5 VP075-01: pin SHA-256 digests of every 0.7.4 output before any 0.7.5 code.

Run once on the unchanged 0.7.3 code (`--write`); afterwards `--check` recomputes the same
outputs (from-plan with --profile 0.7.4, as the N vectors declare it) and compares byte digests.
Covers cube.phases and cube.flow panels, single and nested partitions, layers, labels and slices.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import from_plan, print_panels, VP07Error  # noqa: E402
from vpmigration.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_074_digests.json'
VEC = json.loads((HERE/'fixtures/n01_n14_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_v074.json').read_text('utf-8'))
FLOW = ('cube.flow', 'subject', 'standard', 'cube.lens.execution')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def files_digest(files):
    return {n: sha(b) for n, b in sorted(files.items())}


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS' or c['op'] != 'from-plan':
            continue
        inp = c['input']
        kw = {k: inp[k] for k in ('tracks', 'layers', 'labels', 'subjects', 'profile') if k in inp}
        src, mapping = from_plan(inp['context'], inp['plan_id'], **kw)
        d = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
        t = inp.get('then')
        if t:
            d['phases'] = files_digest(print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))[1])
        try:
            d['flow'] = files_digest(print_panels(src, *FLOW)[1])
        except VP07Error as e:                       # e.g. N-11 (many boxes on one subject): the failure itself is pinned
            d['flow'] = 'FAIL '+e.code
        out[c['id']] = d
    src, mapping = from_plan(GOLD['context'], GOLD['plan_id'], profile=GOLD['profile'])
    out['golden074:source'] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
    for view, part, lens in (('cube.phases', 'subject', None), ('cube.phases', 'method', None), ('cube.flow', 'subject', 'cube.lens.execution')):
        out[f'golden074:{view}:{part}'] = files_digest(print_panels(src, view, part, 'standard', lens)[1])
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': 'P2-VP-MIGRATION/0.7.4',
                                   'pinned_before': 'any VP-07.5 runtime code (VP075-01)', 'digests': cur},
                                  sort_keys=True, indent=1)+'\n', 'utf-8')
        print('pinned', len(cur), 'scenarios'); return
    pinned = json.loads(OUT.read_text('utf-8'))['digests']
    bad = [k for k in pinned if pinned[k] != cur.get(k)]
    for k in bad:
        print('DIFF', k)
    print(f'{len(pinned)-len(bad)}/{len(pinned)} scenarios byte-identical')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
