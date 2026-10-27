#!/usr/bin/env python3
"""Run A-01..A-20 (VP-09) against vpaxes through its Python API. Exit 0 only if every case matches the oracle."""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels  # noqa: E402
from vpaxes.common import publish_dir, no_active_content, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/a01_a20_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_a01_a20.json').read_text('utf-8'))['cases']}
G = f'{{{NS}}}g'


def run(c, tmp):
    inp = c['input']
    doc, _ = from_plan(inp['context'], inp['plan_id'], layers=inp.get('layers'))
    if c['op'] == 'render':
        rep, svg = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'])
        return {'warnings': rep['warnings'], 'report': rep, 'svgs': [svg]}
    rep, files = print_panels(doc, inp['rows'], inp['cols'], inp['granularity'])
    d = publish_dir(files, Path(tmp)/'panels')
    if inp.get('tamper') == 'drop_entry':
        f = d/'panel-01.input.json'
        x = json.loads(f.read_text('utf-8'))
        x['input']['source']['cells'].pop()
        f.write_text(json.dumps(x, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    check_panels(d)
    return {'warnings': rep['warnings'], 'report': rep, 'files': files,
            'svgs': [b for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]}


def cellgroups(svg):
    return {g.get('data-vp09-cell'): g for g in ET.fromstring(svg).iter(G) if g.get('data-vp09-cell')}


def check(c, out):
    x, ok = c['expect'], True
    rep = out['report']
    svg = out['svgs'][0]
    if x.get('rendered'):
        ok = ok and bool(rep['cells']) and rep['render_status'] == 'PASS'
    if 'row_order' in x:
        ok = ok and rep['row_values'] == x['row_order']
    if 'kind_members' in x:
        kind = x['kind_members']['kind']
        kinds = [g.get('data-vp09-kind') or g.get('data-vp09-row') for g in ET.fromstring(svg).iter(G)
                 if g.get('data-vp09-kind') or g.get('data-vp09-row')]
        i = kinds.index(kind)
        members = []
        for k in kinds[i+1:]:
            if k in ('Core', 'Connector', 'Toolbox', 'Tool', 'Adapter', 'Integration', 'Runtime', 'Provider', 'ThirdPartyDependency'):
                break
            members.append(k)
        ok = ok and members == x['kind_members']['order']
    if 'cells_of_entry' in x:
        e = x['cells_of_entry']['entry']
        got = sorted(k.split('|') for k, es in rep['cells'].items() if e in es)
        ok = ok and got == sorted(x['cells_of_entry']['cells'])
    for want in x.get('cell_contains', []):
        key = f"{want['row']}|{want['col']}"
        g = cellgroups(svg).get(key)
        ok = ok and want['entry'] in rep['cells'].get(key, []) and g is not None and want['entry'] in g.find(f'{{{NS}}}title').text
    if 'entry_once' in x:
        ok = ok and sum(es.count(x['entry_once']) for es in rep['cells'].values()) == 1
    if 'blank_cell' in x:
        key = f"{x['blank_cell']['row']}|{x['blank_cell']['col']}"
        ok = ok and key not in rep['cells'] and key not in cellgroups(svg)
        ok = ok and x['blank_cell']['row'] in rep['row_values'] and x['blank_cell']['col'] in rep['col_values']
    if x.get('equal_cells') or x.get('uniform_fill'):
        rects = [r for g in cellgroups(svg).values() for r in g.iter(f'{{{NS}}}rect')]
        ok = ok and len(rects) > 1 and len({(r.get('width'), r.get('height')) for r in rects}) == 1 and len({r.get('fill') for r in rects}) == 1
    if x.get('equal_columns'):
        cols = [g for g in ET.fromstring(svg).iter(G) if g.get('data-vp09-col')]
        xs = sorted(float(t.get('x')) for g in cols for t in list(g.iter(f'{{{NS}}}text'))[:1])
        gaps = {round(b-a, 2) for a, b in zip(xs, xs[1:])}
        ok = ok and len(cols) >= 3 and len(gaps) == 1
    if x.get('no_active_content'):
        ok = ok and all(no_active_content(ET.fromstring(s)) for s in out['svgs'])
    if 'ledger_count' in x:
        want = x['ledger_count']
        key = f"{want['row']}|{want['col']}"
        led = json.loads(next(e for e in ET.fromstring(svg).iter() if e.get('id') == 'vp09-axes-ledger').text)
        ok = ok and len(led['cells'][key]) == want['n'] and cellgroups(svg)[key].get('data-vp09-count') == str(want['n'])
    if x.get('coverage_complete'):
        ok = ok and rep['coverage']['status'] == 'COMPLETE' and rep['panel_count'] >= x.get('panels_min', 1)
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['forbidden_codes'], c['expect']) == \
            (o['expected_status'], o['required_codes'], o['forbidden_codes'], o['expect']), c['id']+': vector differs from oracle'
        msg = ''
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP09Error as e:
                out, status, codes, msg = None, 'FAIL', [e.code], str(e)
            ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) \
                and not any(k in codes for k in c['forbidden_codes'])
            if ok and status == 'PASS':
                ok = check(c, out)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg)
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
