#!/usr/bin/env python3
"""Pin the VP-10 0.11.0 outputs (SVG and report) before the VP-11 G6 change (VP11-01).

  pin_vp10_0110_digests.py --write   # once, on the unchanged VP-10 and adapter code (TASK-054)
  pin_vp10_0110_digests.py           # check: every pinned output is byte-identical
Covers the CLI vectors of S-01…S-16 (errors pin their code). The 0.10.0 and 0.10.1 outputs stay pinned in vpcells itself.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
CELLS = HERE.parent/'visual-printer-cells-v1'
sys.path.insert(0, str(CELLS)); sys.dont_write_bytecode = True
from vpcells.statements import from_statements  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, encode  # noqa: E402
OUT = HERE/'fixtures/regression_vp10_0110_digests.json'


def digest(c):
    try:
        doc = from_statements(copy.deepcopy(c['context']), copy.deepcopy(c['statements']), c['predicate'], copy.deepcopy(c['projection']))
        rep, svg = render_cells(doc, locale=c['locale'], axis_order=c['axis_order'])
    except VP09Error as e:
        return {'error': e.code}
    return {'svg_sha256': hashlib.sha256(svg).hexdigest(), 'report_sha256': hashlib.sha256(encode(rep)).hexdigest()}


def main():
    vec = [c for c in json.loads((CELLS/'fixtures/s01_s16_materialized.json').read_text('utf-8'))['cases'] if c['via'] == 'cli']
    now = {c['id']: digest(c) for c in vec}
    if '--write' in sys.argv:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps({'format': 'aiaeao.p2.vp10-regression-digests/1', 'profile': 'P2-VP-CELLS/0.11.0',
                                   'pinned_before': 'the VP-11 G6 change (VP11-01, TASK-054)', 'cases': now}, indent=1, sort_keys=True)+'\n', 'utf-8')
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
