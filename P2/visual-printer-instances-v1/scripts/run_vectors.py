#!/usr/bin/env python3
"""Run I-01…I-34 (VP-11) through vpinstances and compare with the independent oracle (oracles/independent_i01_i34.json).

Compared per case: error code, or frames, block headers, row texts, verdict lines, model lines, warning codes and the
number of violation marks; every row and verdict text must stand in the SVG (as <title> of its group).
"""
import copy, json, sys
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpinstances.trace import from_trace  # noqa: E402
from vpinstances.view import render_instances  # noqa: E402
from vpinstances.common import VP09Error, NS, PROFILE  # noqa: E402

VEC = json.loads((HERE/'fixtures/i01_i34_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_i01_i34.json').read_text('utf-8'))['cases']}
q = lambda t: f'{{{NS}}}{t}'  # noqa: E731


def run(c):
    doc = from_trace(copy.deepcopy(c['context']), copy.deepcopy(c['trace']), copy.deepcopy(c['records']))
    return render_instances(doc, None if c['locale'] == 'en' else c['locale'])


def check(c):
    e = ORACLE[c['id']]
    try:
        rep, svg = run(c)
    except VP09Error as x:
        return e['status'] == 'error' and e['code'] == x.code, f'error {x.code}'
    if e['status'] == 'error':
        return False, 'no error, expected '+e['code']
    why = []
    frames = [f['instance'] or '-' for f in rep['frames']]
    if frames != e['frames']:
        why.append(f'frames {frames}')
    blocks = {f['instance'] or '-': [b['header'] for b in f['blocks']] for f in rep['frames']}
    if blocks != e['blocks']:
        why.append(f'blocks {blocks}')
    rows = {f"{f['instance'] or '-'}|{b['gateway']}": [r['text'] for r in b['rows']] for f in rep['frames'] for b in f['blocks']}
    for k in sorted(set(rows) | set(e['rows'])):
        if rows.get(k) != e['rows'].get(k):
            why.append(f'rows {k}: {rows.get(k)}')
    verdicts = {f"{f['instance'] or '-'}|{b['gateway']}": [v['text'] for v in b['verdicts']] for f in rep['frames'] for b in f['blocks']}
    for k in sorted(set(verdicts) | set(e['verdicts'])):
        if verdicts.get(k) != e['verdicts'].get(k):
            why.append(f'verdicts {k}: {verdicts.get(k)}')
    if rep['model'] != e['model']:
        why.append(f"model {rep['model']}")
    if sorted({w['code'] for w in rep['warnings']}) != e['warnings']:
        why.append(f"warnings {[w['code'] for w in rep['warnings']]}")
    if rep['violation_marks'] != e['violation_marks']:
        why.append(f"marks {rep['violation_marks']}")
    root = ET.fromstring(svg)
    titles = {t.text for g in root.iter(q('g')) if g.get('data-vp11-row') or g.get('data-vp11-verdict') for t in g.findall(q('title'))}
    lost = [s for v in list(rows.values())+list(verdicts.values()) for s in v if s not in titles]
    if lost:
        why.append(f'not in SVG {lost[:2]}')
    if rep['profile'] != PROFILE or root.get('data-printer-profile') != PROFILE:
        why.append('profile')
    return not why, '; '.join(why) or 'as oracle'


def main():
    n = 0
    for c in VEC:
        ok, why = check(c)
        n += ok
        print('PASS' if ok else 'FAIL', c['id'], why if not ok else '')
    print(f'{n}/{len(VEC)} match')
    sys.exit(0 if n == len(VEC) == len(ORACLE) else 1)


if __name__ == '__main__':
    main()
