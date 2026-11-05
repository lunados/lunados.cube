#!/usr/bin/env python3
"""VP-07.7 VP077-01: pin SHA-256 digests of every 0.7.6 output before any 0.7.7 code.

Run once on the unchanged 0.7.6 code (`--write`); afterwards `--check` recomputes the same outputs (the OL-01…OL-12
vectors through the G6 functions plan_source / plan_views, which equal the CLI) and compares byte digests of the
source, the mapping and every panel file. 0.7.0…0.7.5 keep their own pins.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / 'P3/adapters/mcp-local')); sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402
from vpmigration.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_076_digests.json'
VEC = json.loads((HERE/'fixtures/ol01_ol12_materialized.json').read_text('utf-8'))['cases']


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf-8')).hexdigest()


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS':
            continue
        env = g6.plan_source(**c['plan_source'])
        res = g6.plan_views(env['source'], **c['plan_views'])
        out[c['id']] = {'source': sha(encode(env['source'])), 'mapping': sha(encode(env['mapping'])),
                        'panels': [sha(p['svg']) for p in res['panels']], 'report': sha(encode(res['report']))}
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': 'P2-VP-MIGRATION/0.7.6',
                                   'pinned_before': 'any VP-07.7 runtime code (VP077-01)', 'digests': cur},
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
