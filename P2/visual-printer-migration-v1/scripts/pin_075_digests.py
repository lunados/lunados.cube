#!/usr/bin/env python3
"""VP-07.6 VP076-01: pin SHA-256 digests of every 0.7.5 output before any 0.7.6 code.

Run once on the unchanged 0.7.5 code (`--write`); afterwards `--check` recomputes the same outputs (from-plan with
--profile 0.7.5, as the O vectors declare it, plus the golden plan) and compares byte digests. Covers cube.phases and
cube.flow panels, German locale, hidden ledger, method sets and the subject slice. 0.7.0…0.7.4 keep their own pins.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import from_plan, print_panels, VP07Error  # noqa: E402
from vpmigration.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_075_digests.json'
VEC = json.loads((HERE/'fixtures/o01_o15_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_v075.json').read_text('utf-8'))
FLOW = {'view': 'cube.flow', 'partition': 'subject', 'granularity': 'standard', 'lens': 'cube.lens.execution'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def panels(src, t):
    try:
        files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'),
                             locale=t.get('locale'), hide_ledger=t.get('hide_ledger', False))[1]
        return {n: sha(b) for n, b in sorted(files.items())}
    except VP07Error as e:                       # a failing combination is pinned as such
        return 'FAIL '+e.code


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS' or c['op'] != 'from-plan':
            continue
        inp = c['input']
        src, mapping = from_plan(inp['context'], inp['plan_id'], profile=inp['profile'],
                                 **({'subjects': inp['subjects']} if 'subjects' in inp else {}))
        d = {'source': sha(encode(src)), 'mapping': sha(encode(mapping)), 'then': panels(src, inp['then']),
             'flow': panels(src, inp.get('flow') or FLOW)}
        out[c['id']] = d
    src, mapping = from_plan(GOLD['context'], GOLD['plan_id'], profile=GOLD['profile'])
    out['golden075:source'] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
    out['golden075:phases'] = panels(src, GOLD['expected']['phases'])
    for loc in (None, 'de'):
        out[f'golden075:flow:{loc or "en"}'] = panels(src, FLOW | {'locale': loc})
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': 'P2-VP-MIGRATION/0.7.5',
                                   'pinned_before': 'any VP-07.6 runtime code (VP076-01)', 'digests': cur},
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
