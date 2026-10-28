#!/usr/bin/env python3
"""VP-09.2 VP092-01: pin SHA-256 digests of every 0.9.1 output before any 0.9.2 code.

Covers B-01…B-20 (from-plan with profile 0.9.1, single renders and panels; FAIL vectors pinned by code and
message) and the golden plan in all 0.9.1 pairs. `--write` once on the unchanged code; the default run compares.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpaxes import from_plan, render_axes, print_panels, VP09Error  # noqa: E402
from vpaxes.common import encode  # noqa: E402

P091 = 'P2-VP-AXES/0.9.1'
OUT = HERE/'fixtures/regression_091_digests.json'
VEC = json.loads((HERE/'fixtures/b01_b20_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_axes.json').read_text('utf-8'))
PAIRS = [('Z:referent', 'T'), ('Y:referent', 'T'), ('Y:referent', 'Z:referent'), ('F', 'Z:referent'), ('F', 'Y:referent'), ('F', 'T'), ('Z:kind', 'T')]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def guard(fn):
    try:
        return fn()
    except VP09Error as e:
        return 'FAIL '+e.code+' '+sha(json.dumps(e.diagnostic(), sort_keys=True).encode())


def collect():
    out = {}
    for c in VEC:
        inp = c['input']
        kw = {'subjects': inp['subjects']} if 'subjects' in inp else {}

        def one():
            doc, mapping = from_plan(inp['context'], inp['plan_id'], profile=inp['profile'], **kw)
            d = {'input': sha(encode(doc)), 'mapping': sha(encode(mapping))}
            if c['op'] == 'render':
                rep, svg = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'])
                d.update(svg=sha(svg), report=sha(encode(rep)))
            else:
                d['panels'] = {n: sha(b) for n, b in sorted(print_panels(doc, inp['rows'], inp['cols'], inp['granularity'])[1].items())}
            return d
        out[c['id']] = guard(one)
    doc, _ = from_plan(GOLD['context'], GOLD['plan_id'], profile=P091)
    for r, c in PAIRS:
        out[f'golden091:{r}x{c}'] = guard(lambda: {n: sha(b) for n, b in sorted(print_panels(doc, r, c, 'standard')[1].items())})
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp09-regression-digests/1', 'profile': P091,
                                   'pinned_before': 'any VP-09.2 runtime code (VP092-01)', 'digests': cur}, sort_keys=True, indent=1)+'\n', 'utf-8')
        print('pinned', len(cur), 'outputs'); return
    want = json.loads(OUT.read_text('utf-8'))['digests']
    bad = [k for k in want if want[k] != cur.get(k)]
    for k in bad:
        print('DIFF', k)
    print(f'{len(want)-len(bad)}/{len(want)} 0.9.1 outputs byte-identical')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
