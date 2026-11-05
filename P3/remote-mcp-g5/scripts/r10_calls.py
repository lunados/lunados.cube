"""MILE-016 TASK-080: G5 wire calls for core 0.9.3-proof and gateway 0.3.0-proof (VP-12 cube.landscape, VP-09.3 locale).

R10 = every R9 call (unchanged bytes), five VP-12 landscape calls on the synthetic plan of the VP-12 vectors
(L-01, L-02, L-04 through the tools, an undeclared step, a seven-layer map) and two VP-09.3 X × Y calls with the
pinned de locale (de-0093.json, a runtime asset new in R10).
"""
from __future__ import annotations
import json
from pathlib import Path
import r5_calls
import r9_calls

REPO = Path(__file__).resolve().parents[3]
HOST = r9_calls.HOST | {'L10-01', 'L10-02', 'X10-01'}
run_chain = r5_calls.run_chain


def _cases(rel):
    return {c['id']: c for c in json.loads((REPO/rel).read_text('utf-8'))['cases']}


def calls():
    out = [c for c in r9_calls.calls()]
    land = _cases('P2/visual-printer-landscape-v1/fixtures/l01_l14_materialized.json')
    l1, l2 = land['L-01'], land['L-02']
    src = r5_calls.source
    seven = dict(l1['layers'], layer_order=l1['layers']['layer_order']+['edge', 'cloud', 'vendor'])
    out += [
        r5_calls.views_chain('L10-01', src(l1['context'], 'pm-ls', 'vplandscape', layers=l1['layers']),
                             {'view': 'cube.landscape', 'granularity': 'detail'}),
        r5_calls.views_chain('L10-02', src(l1['context'], 'pm-ls', 'vplandscape', layers=l1['layers'], steps='current,mvp,beta'),
                             {'view': 'cube.landscape', 'granularity': 'detail', 'locale': 'de'}),
        r5_calls.views_chain('L10-03', src(l2['context'], 'pm-ls', 'vplandscape', placement_predicates=[]),
                             {'view': 'cube.landscape', 'granularity': 'standard'}),
        r5_calls.chain('L10-04', 'P', [src(l1['context'], 'pm-ls', 'vplandscape', steps='current,gamma')]),
        r5_calls.views_chain('L10-05', src(l1['context'], 'pm-ls', 'vplandscape', layers=seven),
                             {'view': 'cube.landscape', 'granularity': 'detail'}, check=False),
    ]
    xy = _cases('P2/visual-printer-axes-v1/fixtures/x01_x12_materialized.json')['X-01']
    xsrc = src(xy['context'], xy['plan_id'], 'vpaxes', profile='P2-VP-AXES/0.9.3')
    out += [
        r5_calls.views_chain('X10-01', xsrc, {'view': 'cube.axes', 'granularity': 'detail', 'rows': 'X', 'cols': 'Y:kind', 'locale': 'de'}),
        r5_calls.views_chain('X10-02', xsrc, {'view': 'cube.axes', 'granularity': 'detail', 'rows': 'X', 'cols': 'Y:referent',
                                              'hide_empty': 'cols', 'locale': 'de'}),
    ]
    for c in out:
        c['live'] = 'host' if c['id'] in HOST else None
    return out
