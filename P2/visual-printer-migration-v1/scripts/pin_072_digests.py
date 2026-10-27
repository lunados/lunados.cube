#!/usr/bin/env python3
"""VP-07.3 VP073-01: pin SHA-256 digests of every 0.7.2 output before any 0.7.3 code.

Run once on the unchanged 0.7.2 code (`--write`); afterwards `--check` recomputes the same
outputs (from-plan with a layer map, as 0.7.2 selects itself) and compares byte digests.
0.7.0 and 0.7.1 stay covered by pin_070_digests.py and pin_071_digests.py.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import from_plan, print_panels  # noqa: E402
from vpmigration.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_072_digests.json'
VEC = json.loads((HERE/'fixtures/l01_l13_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_v072.json').read_text('utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def files_digest(files):
    return {n: sha(b) for n, b in sorted(files.items())}


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS':
            continue
        inp = c['input']
        if c['op'] == 'panels':
            out[c['id']] = files_digest(print_panels(inp['source'], inp['view'], inp['partition'], inp['granularity'], inp.get('lens'))[1])
            continue
        src, mapping = from_plan(inp['context'], inp['plan_id'], tracks=inp.get('tracks'), layers=inp.get('layers'))
        d = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
        t = inp.get('then')
        if t:
            d['panels'] = files_digest(print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))[1])
        out[c['id']] = d
    src, mapping = from_plan(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], layers=GOLD['layers'])
    out['golden072:source'] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
    for view, part, lens in (('cube.phases', 'track,layer', None), ('cube.phases', 'layer', None),
                             ('cube.flow', 'track,subject', 'cube.lens.execution')):
        out[f'golden072:{view}:{part}'] = files_digest(print_panels(src, view, part, 'standard', lens)[1])
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': 'P2-VP-MIGRATION/0.7.2',
                                   'pinned_before': 'any VP-07.3 runtime code (VP073-01)', 'digests': cur},
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
