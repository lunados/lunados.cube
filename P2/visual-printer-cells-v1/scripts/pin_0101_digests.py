#!/usr/bin/env python3
"""Pin the VP-10 0.10.1 outputs (SVG and report) before any 0.11.0 code (VP110-01).

  pin_0101_digests.py --write   # once, on the unchanged 0.10.1 code
  pin_0101_digests.py           # check: every pinned output is byte-identical
Covers O-01…O-09 (O-05 is an error and pins its code). The 0.10.0 outputs stay pinned by pin_0100_digests.py.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpcells.source import from_plan  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, encode  # noqa: E402
OUT = HERE/'fixtures/regression_0101_digests.json'


def digest(c):
    try:
        doc, _ = from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'], steps=c['steps'])
        rep, svg = render_cells(doc, c['rows'], c['cols'], hide_empty=c['hide_empty'], locale=c['locale'], axis_order=c['axis_order'])
    except VP09Error as e:
        return {'error': e.code}
    return {'svg_sha256': hashlib.sha256(svg).hexdigest(), 'report_sha256': hashlib.sha256(encode(rep)).hexdigest()}


def main():
    vec = [c for c in json.loads((HERE/'fixtures/o01_o10_materialized.json').read_text('utf-8'))['cases'] if c['via'] == 'cli']
    now = {c['id']: digest(c) for c in vec}
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.p2.vp10-regression-digests/1', 'profile': 'P2-VP-CELLS/0.10.1',
                                   'pinned_before': 'any 0.11.0 code (VP110-01)', 'cases': now}, indent=1, sort_keys=True)+'\n', 'utf-8')
        print('pinned', len(now)); return
    pinned = json.loads(OUT.read_text('utf-8'))['cases']
    same = sum(1 for k in pinned if now.get(k) == pinned[k])
    for k in sorted(pinned):
        if now.get(k) != pinned[k]:
            print('DIFF', k, now.get(k), pinned[k])
    print(f'{same}/{len(pinned)} byte-identical')
    sys.exit(0 if same == len(pinned) == len(now) else 1)


if __name__ == '__main__':
    main()
