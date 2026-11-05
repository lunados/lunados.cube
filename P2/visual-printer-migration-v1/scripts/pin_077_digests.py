#!/usr/bin/env python3
"""VP-07.8 VP078-01: pin SHA-256 digests of every 0.7.7 output before any 0.7.8 code.

Run once on the unchanged 0.7.7 code (`--write`); afterwards `--check` recomputes the same outputs (the synthetic
VP-07.7 plan of tests/test_vp077.py through the G6 functions: cube.flow with origin lines, cube.phases, statement
path) and compares byte digests of the source, the mapping and every panel. 0.7.0…0.7.6 keep their own pins.
"""
import hashlib, importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / 'P3/adapters/mcp-local')); sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402
from vpmigration.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_077_digests.json'
P077 = 'P2-VP-MIGRATION/0.7.7'


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf-8')).hexdigest()


def cases():
    spec = importlib.util.spec_from_file_location('vp077_cases', HERE/'tests/test_vp077.py')
    t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
    ctx = t.context()
    st = {'format': 'aiaeao.cube.statement-set/2', 'set_id': 'set-077', 'context_id': ctx['context_id'], 'referents': ['s:core', 's:grant'],
          'statements': [{'statement_id': 'st-1', 'subject': 's:core', 'predicate_id': 'uses', 'object': 's:grant', 'origin': 'declared'}]}
    return {
        'flow': ((ctx, 'pm-077', 'vpmigration'), {'profile': P077, 'origin_lines': True}, ('cube.flow', 'detail'), {'partition': 'subject'}),
        'phases': ((ctx, 'pm-077', 'vpmigration'), {'profile': P077}, ('cube.phases', 'detail'), {'partition': 'subject'}),
        'statements': ((ctx, None, 'vpmigration'), {'profile': P077, 'origin_lines': True, 'statements': st}, ('cube.flow', 'standard'), {'partition': 'subject'}),
    }


def collect():
    out = {}
    for name, (a, k, va, vk) in cases().items():
        env = g6.plan_source(*a, **k)
        res = g6.plan_views(env['source'], *va, **vk)
        out[name] = {'source': sha(encode(env['source'])), 'mapping': sha(encode(env['mapping'])),
                     'panels': [sha(p['svg']) for p in res['panels']], 'report': sha(encode(res['report']))}
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': P077,
                                   'pinned_before': 'any VP-07.8 runtime code (VP078-01)', 'digests': cur},
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
