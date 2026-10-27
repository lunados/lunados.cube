#!/usr/bin/env python3
"""VP-09.1 VP091-01: pin SHA-256 digests of every 0.9.0 output before any 0.9.1 code.

Run once on the unchanged 0.9.0 code (`--write`); afterwards `--check` recomputes the same
outputs with the default profile (0.9.0, D-1) and compares byte digests.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpaxes import from_plan, render_axes, print_panels  # noqa: E402
from vpaxes.common import encode  # noqa: E402

OUT = HERE/'fixtures/regression_090_digests.json'
VEC = json.loads((HERE/'fixtures/a01_a20_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_axes.json').read_text('utf-8'))
GOLD_VIEWS = [('Z:referent', 'T'), ('Y:referent', 'T'), ('F', 'Z:referent'), ('F', 'T'), ('Z:kind', 'T'), ('Y:referent', 'Z:referent')]


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
        doc, mapping = from_plan(inp['context'], inp['plan_id'], layers=inp.get('layers'))
        d = {'input': sha(encode(doc)), 'mapping': sha(encode(mapping))}
        if c['op'] == 'render':
            rep, svg = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'])
            d.update(svg=sha(svg), report=sha(encode(rep)))
        else:
            d['panels'] = files_digest(print_panels(doc, inp['rows'], inp['cols'], inp['granularity'])[1])
        out[c['id']] = d
    doc, mapping = from_plan(GOLD['context'], GOLD['plan_id'])
    out['golden:input'] = {'input': sha(encode(doc)), 'mapping': sha(encode(mapping))}
    for r, c in GOLD_VIEWS:
        out[f'golden:{r}x{c}:standard'] = files_digest(print_panels(doc, r, c, 'standard')[1])
    return out


def main():
    got = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp09-regression-digests/1', 'profile': 'P2-VP-AXES/0.9.0',
                                   'digests': got}, sort_keys=True, indent=1)+'\n', 'utf-8')
        print('pinned', len(got), 'outputs')
        return
    want = json.loads(OUT.read_text('utf-8'))['digests']
    bad = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
    for k in bad:
        print('DIFF', k)
    print(f'{len(want)-len(bad)}/{len(want)} 0.9.0 outputs byte-identical')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
