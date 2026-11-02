#!/usr/bin/env python3
"""Run O-01..O-10 (VP-10.1, declared axis order) through vpcells and compare with the independent oracle."""
import copy, json, sys
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
from vpcells.source import from_plan  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, NS, sha_bytes  # noqa: E402
from vpcells import api  # noqa: E402

ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_o01_o10.json').read_text('utf-8'))['cases']}
VEC = json.loads((HERE/'fixtures/o01_o10_materialized.json').read_text('utf-8'))['cases']
PINS = json.loads((HERE/'fixtures/regression_0100_digests.json').read_text('utf-8'))
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')
q = lambda t: f'{{{NS}}}{t}'  # noqa: E731


def run(c):
    doc, _ = from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'], steps=c['steps'])
    return render_cells(doc, c['rows'], c['cols'], hide_empty=c['hide_empty'], locale=c['locale'], axis_order=c['axis_order'])


def texts(svg):
    root = ET.fromstring(svg)
    cells, heads = {}, {}
    for g in root.iter(q('g')):
        k = g.get('data-vp10-cell') or g.get('data-vp09-cell')
        if k:
            cells[k] = [t.text for t in g.iter(q('text'))]
        for a in ('data-vp09-row', 'data-vp09-col'):
            if g.get(a):
                heads.setdefault(g.get(a), []).extend(t.text for t in g.iter(q('text')))
    return root, cells, heads


def pin_of(jid):
    cases = PINS['cases'] if 'cases' in PINS else PINS
    return cases[jid]


def check(c, by_id):
    e = c['expected']
    if c['via'] != 'cli':                                    # O-10: G6 views + check must equal the CLI render of O-01
        o1 = by_id[e['svg_equals_cli_of']]
        _, svg = run(o1)
        src = api.source(copy.deepcopy(c['context']), c['plan_id'], c['predicate'])
        res = api.views(src['source'], 'cube.cells', axis_order=c['axis_order'])
        chk = api.check(json.loads(json.dumps(res)))
        ok = res['panels'][0]['svg'].encode('utf-8') == svg and chk['status'] == e['check'] and res['profile'] == 'P2-VP-CELLS/0.10.1'
        return ok, f"G6 svg {'==' if res['panels'][0]['svg'].encode() == svg else '!='} CLI {e['svg_equals_cli_of']}, check {chk['status']}"
    try:
        rep, svg = run(c)
    except VP09Error as x:
        return e.get('error') == x.code, f'error {x.code}'
    if 'error' in e:
        return False, 'no error'
    if 'byte_identical_to_pin' in e:
        pin = pin_of(e['byte_identical_to_pin'])
        ok = sha_bytes(svg) == pin['svg_sha256'] and rep['profile'] == e['profile'] and 'axis_order' not in rep
        return ok, f"0.10.0 svg {'==' if sha_bytes(svg) == pin['svg_sha256'] else '!='} pin {e['byte_identical_to_pin']}"
    root, cells, heads = texts(svg)
    why = []
    for k, got in (('profile', rep['profile']), ('rows', rep['row_values']), ('cols', rep['col_values']),
                   ('unordered_values', rep['unordered_values']), ('feedback_cells', rep['feedback_cells']),
                   ('warnings', sorted(w['code'] for w in rep['warnings'])), ('hidden_cols', rep['hidden_cols'])):
        want = sorted(e[k]) if k == 'warnings' else e.get(k, [] if k == 'hidden_cols' else None)
        if got != want:
            why.append(f'{k}: {got} != {want}')
    if root.get('data-printer-profile') != e['profile']:
        why.append('svg profile')
    fb = sorted(g.get('data-vp10-cell') or g.get('data-vp09-cell') for g in root.iter(q('g')) if g.get('data-vp10-feedback') == 'true')
    if fb != e['feedback_cells']:
        why.append(f'svg feedback marks {fb}')
    for k, v in e.get('text', {}).items():
        if cells.get(k) != v:
            why.append(f'text {k}: {cells.get(k)} != {v}')
    for k, v in e.get('header_contains', {}).items():
        if v not in heads.get(k, []):
            why.append(f'header {k}: {heads.get(k)}')
    if not all(rep[k] == 'NOT_EVALUATED' for k in NOPROMO):
        why.append('promotion')
    return not why, '; '.join(why) or f"rows {rep['row_values']} feedback {rep['feedback_cells']} warnings {[w['code'] for w in rep['warnings']]}"


def main():
    assert [c['id'] for c in VEC] == sorted(ORACLE)
    by_id = {c['id']: c for c in VEC}
    n = 0
    for c in VEC:
        ok, why = check(c, by_id)
        n += ok
        print('PASS' if ok else 'FAIL', c['id'], why)
    print(f'{n}/{len(VEC)} match')
    sys.exit(0 if n == len(VEC) else 1)


if __name__ == '__main__':
    main()
