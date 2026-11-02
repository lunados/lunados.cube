#!/usr/bin/env python3
"""Pin the VP-10 0.10.0 outputs (SVG and report) before any 0.10.1 code (VP101-01).

  pin_0100_digests.py --write   # once, on the unchanged 0.10.0 code
  pin_0100_digests.py           # check: every pinned output is byte-identical
Covers J-01…J-14 (J-13 is an error and pins its code) and both golden cases.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpcells.source import from_plan  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, encode  # noqa: E402
OUT = HERE/'fixtures/regression_0100_digests.json'


def cases():
    for c in json.loads((HERE/'fixtures/j01_j14_materialized.json').read_text('utf-8'))['cases']:
        yield c['id'], c
    for g in json.loads((HERE/'fixtures/golden_cells.json').read_text('utf-8'))['cases']:
        yield g['id'], {**g, 'rows': 'Y:referent', 'cols': 'Y:referent', 'steps': None}


def digest(c):
    try:
        doc, _ = from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'], steps=c.get('steps'))
        rep, svg = render_cells(doc, c['rows'], c['cols'], hide_empty=c.get('hide_empty'), locale=c.get('locale'))
    except VP09Error as e:
        return {'error': e.code}
    return {'svg_sha256': hashlib.sha256(svg).hexdigest(), 'report_sha256': hashlib.sha256(encode(rep)).hexdigest()}


def main():
    now = {i: digest(c) for i, c in cases()}
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.p2.vp10-regression-digests/1', 'profile': 'P2-VP-CELLS/0.10.0',
                                   'pinned_before': 'any 0.10.1 code (VP101-01)', 'cases': now}, indent=1, sort_keys=True)+'\n', 'utf-8')
        print('pinned', len(now)); return
    pinned = json.loads(OUT.read_text('utf-8'))['cases']
    same = sum(now.get(k) == v for k, v in pinned.items())
    print(f'{same}/{len(pinned)} byte-identical'); sys.exit(0 if same == len(pinned) and set(now) == set(pinned) else 1)


if __name__ == '__main__':
    main()
