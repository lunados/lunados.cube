#!/usr/bin/env python3
"""Run S-01…S-16 (VP-10 0.11.0, statement sets and aggregation records) through vpcells and compare with the
independent oracle (oracles/independent_s01_s16.json).

`svg_must_not_contain` is read as whole tokens (not inside a longer word): the oracle lists the plan words p0, p1, phase,
plan and migration; as raw substrings p1 would also hit the printer's own attribute prefix `data-vp10-`.
"""
import copy, json, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpcells.statements import from_statements  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, NS  # noqa: E402
from vpcells import api  # noqa: E402

VEC = json.loads((HERE/'fixtures/s01_s16_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_s01_s16.json').read_text('utf-8'))['cases']}
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')
q = lambda t: f'{{{NS}}}{t}'  # noqa: E731


def run(c):
    doc = from_statements(copy.deepcopy(c['context']), copy.deepcopy(c['statements']), c['predicate'], copy.deepcopy(c['projection']))
    return render_cells(doc, locale=c['locale'], axis_order=c['axis_order'])


def parse(svg):
    root = ET.fromstring(svg)
    cells = {g.get('data-vp10-cell'): [t.text for t in g.iter(q('text'))] for g in root.iter(q('g')) if g.get('data-vp10-cell')}
    texts = [t.text for t in root.iter(q('text'))]
    led = json.loads(next(m for m in root.iter(q('metadata')) if m.get('id') == 'vp10-cells-ledger').text)
    return root, cells, texts, led


def check(c, by_id):
    e = c['expected']
    if c['via'] != 'cli':                                    # S-16: G6 source + views + check equals the CLI render
        _, svg = run(by_id[e['svg_equals_cli_of']])
        src = api.source(copy.deepcopy(c['context']), None, c['predicate'], statements=copy.deepcopy(c['statements']),
                         projection=copy.deepcopy(c['projection']))
        res = api.views(json.loads(json.dumps(src['source'])), 'cube.cells')
        chk = api.check(json.loads(json.dumps(res)))
        same = res['panels'][0]['svg'].encode('utf-8') == svg
        return same and chk['status'] == e['check'] and res['profile'] == 'P2-VP-CELLS/0.11.0', f"G6 svg {'==' if same else '!='} CLI, check {chk['status']}"
    try:
        rep, svg = run(c)
    except VP09Error as x:
        return e.get('error') == x.code, f'error {x.code}'
    if 'error' in e:
        return False, 'no error'
    root, cells, texts, led = parse(svg)
    why = []
    states = {k: v['state'] for k, v in rep['cells'].items()}
    if rep['profile'] != e['profile'] or root.get('data-printer-profile') != e['profile']:
        why.append(f"profile {rep['profile']}")
    for k in ('rows', 'cols'):
        if k in e and rep[f'{k[:-1]}_values'] != e[k]:
            why.append(f"{k} {rep[k[:-1]+'_values']}")
    if 'marked' in e:
        got = {k: ', '.join(v.get('entries', [])) for k, v in rep['cells'].items() if v['state'] == 'marked'}
        if got != e['marked']:
            why.append(f'marked {got}')
    if 'checked' in e:
        got = {k: v['scope'] for k, v in rep['cells'].items() if v['state'] == 'checked'}
        if got != e['checked']:
            why.append(f'checked {got}')
    if 'unknown' in e and sorted(k for k, s in states.items() if s == 'unknown') != sorted(e['unknown']):
        why.append(f"unknown {sorted(k for k, s in states.items() if s == 'unknown')}")
    if any(s == 'element' and k.split('|')[0] != k.split('|')[1] for k, s in states.items()):
        why.append('element off the diagonal')
    if sorted(w['code'] for w in rep['warnings']) != sorted(e.get('warnings', sorted(w['code'] for w in rep['warnings']))):
        why.append(f"warnings {[w['code'] for w in rep['warnings']]}")
    if 'feedback_cells' in e and rep.get('feedback_cells') != e['feedback_cells']:
        why.append(f"feedback {rep.get('feedback_cells')}")
    for k, v in e.get('text', {}).items():
        if cells.get(k) != v:
            why.append(f'text {k}: {cells.get(k)}')
    if 'title' in e and (root.find(q('title')).text != e['title'] or e['title'] not in texts):
        why.append('title')
    if 'legend_line' in e and (e['legend_line'] not in texts or rep['loss_line'] != e['legend_line']):
        why.append(f"legend line {rep['loss_line']}")
    if 'loss' in e and (rep['aggregation'] or {}).get('loss') != e['loss']:
        why.append('loss')
    if 'ledger_derived' in e and (led['aggregation'] or {}).get('derived') != e['ledger_derived']:
        why.append(f"ledger derived {(led['aggregation'] or {}).get('derived')}")
    if 'ledger_suppressed' in e and {x['statement_id']: x['suppressed_by'] for x in (led['aggregation'] or {}).get('suppressed', [])} != e['ledger_suppressed']:
        why.append('ledger suppressed')
    raw = svg.decode('utf-8')
    bad = [w for w in e.get('svg_must_not_contain', []) if re.search(r'(?<![A-Za-z0-9])'+re.escape(w.strip())+r'(?![A-Za-z0-9])', raw)]
    if bad:
        why.append(f'plan vocabulary {bad}')
    if not all(rep[k] == 'NOT_EVALUATED' for k in NOPROMO):
        why.append('promotion')
    return not why, '; '.join(why) or f"{rep['state_counts']} warnings {sorted(w['code'] for w in rep['warnings'])}"


def main():
    assert [c['id'] for c in VEC] == sorted(ORACLE) and all(c['expected'] == ORACLE[c['id']]['expected'] for c in VEC)
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
