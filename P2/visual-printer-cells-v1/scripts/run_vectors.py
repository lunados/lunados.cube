#!/usr/bin/env python3
"""Run J-01..J-14 through vpcells (from-plan, print) and compare every cell state with the independent oracle."""
import copy, json, sys
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpcells.source import from_plan  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, NS  # noqa: E402

ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_j01_j14.json').read_text('utf-8'))['cases']}
BASE = json.loads((HERE/'oracles/independent_j01_j14.json').read_text('utf-8'))['base']
VEC = json.loads((HERE/'fixtures/j01_j14_materialized.json').read_text('utf-8'))['cases']
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(c):
    doc, _ = from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'], steps=c['steps'])
    return render_cells(doc, c['rows'], c['cols'], hide_empty=c['hide_empty'], locale=c['locale'])


def expand(e):
    """Oracle shorthand → explicit {cell: state} for the visible off-diagonal cells, plus hidden cells."""
    marked = BASE['marked'] if e['marked'] == 'base' else e['marked']
    hidden = set(e.get('hidden_cells', []))
    checked = e['checked']
    if e['unknown'] == 'all empty':
        unknown = [k for k in BASE['empty'] if k not in hidden]
    elif e['unknown'] == 'rest of empty':
        unknown = [k for k in BASE['empty'] if k not in checked and k not in hidden]
    else:
        unknown = e['unknown']
    want = {k: 'marked' for k in marked}
    want.update({k: 'unknown' for k in unknown})
    want.update({k: 'checked' for k in checked})
    want.update({k: 'hidden' for k in hidden})
    return want


def cell_texts(svg):
    root = ET.fromstring(svg); q = lambda t: f'{{{NS}}}{t}'  # noqa: E731
    out = {}
    for g in root.iter(q('g')):
        k = g.get('data-vp10-cell') or g.get('data-vp09-cell')
        if k:
            out[k] = [t.text for t in g.iter(q('text'))]
    return out


def check(c):
    e = c['expected']
    try:
        rep, svg = run(c)
    except VP09Error as x:
        return e.get('error') == x.code, f'error {x.code}'
    if 'error' in e:
        return False, 'no error'
    got = {k: v['state'] for k, v in rep['cells'].items() if v['state'] != 'element'}
    want = expand(e)
    bad = {k: (got.get(k), w) for k, w in want.items() if got.get(k) != w}
    extra = sorted(set(got) - set(want))
    diag = all(v['state'] in ('element', 'hidden') for k, v in rep['cells'].items() if k.split('|')[0] == k.split('|')[1])
    scopes = {k: rep['cells'][k].get('scope') for k in e['checked']}
    ok = not bad and not extra and diag and scopes == e['checked']
    ok &= sorted(w['code'] for w in rep['warnings']) == sorted(e['warnings'])
    for k in ('hidden_rows', 'hidden_cols'):
        if k in e:
            ok &= rep[k] == e[k]
    if 'declarations_other_predicate' in e:
        ok &= rep['declarations_other_predicate'] == e['declarations_other_predicate']
    texts = cell_texts(svg)
    tbad = {k: (texts.get(k), v) for k, v in e.get('text', {}).items() if texts.get(k) != v}
    ok &= not tbad and all(rep[k] == 'NOT_EVALUATED' for k in NOPROMO)
    return ok, f"states {'ok' if not bad and not extra else (bad, extra)} scopes {scopes} warnings {[w['code'] for w in rep['warnings']]}" + \
        (f' text {tbad}' if tbad else '')


def main():
    assert [c['id'] for c in VEC] == sorted(ORACLE)
    n = 0
    for c in VEC:
        ok, why = check(c)
        n += ok
        print('PASS' if ok else 'FAIL', c['id'], why)
    print(f'{n}/{len(VEC)} match')
    sys.exit(0 if n == len(VEC) else 1)


if __name__ == '__main__':
    main()
