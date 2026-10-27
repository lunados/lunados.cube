#!/usr/bin/env python3
"""Run B-01..B-20 (VP-09.1) against vpaxes through its Python API. Exit 0 only if every case matches the oracle."""
import hashlib, json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels  # noqa: E402
from vpaxes.common import publish_dir, NS, encode  # noqa: E402

DOC = json.loads((HERE/'fixtures/b01_b20_materialized.json').read_text('utf-8'))
VEC = DOC['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_b01_b20.json').read_text('utf-8'))['cases']}
G = f'{{{NS}}}g'


def run(c, tmp):
    inp = c['input']
    kw = {'subjects': inp['subjects']} if 'subjects' in inp else {}
    doc, _ = from_plan(inp['context'], inp['plan_id'], profile=inp['profile'], **kw)
    if c['op'] == 'render':
        rep, svg = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'])
        out = {'warnings': rep['warnings'], 'report': rep, 'svgs': [svg]}
        if c['expect'].get('equals_default_090'):
            d0, _ = from_plan(inp['context'], inp['plan_id'], **kw)
            r0, s0 = render_axes(d0, inp['rows'], inp['cols'], inp['granularity'])
            out['same_090'] = encode(d0) == encode(doc) and s0 == svg and encode(r0) == encode(rep)
        return out
    rep, files = print_panels(doc, inp['rows'], inp['cols'], inp['granularity'])
    d = publish_dir(files, Path(tmp)/'panels')
    if inp.get('tamper') == 'drop_binding_unit':
        f = d/'report.json'
        x = json.loads(f.read_text('utf-8'))
        next(e for e in x['panel_ledger'] if e['binding_units'])['binding_units'].pop()
        f.write_text(json.dumps(x, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    check_panels(d)
    return {'warnings': rep['warnings'], 'report': rep, 'files': files,
            'svgs': [b for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]}


def cellgroups(svg):
    return {g.get('data-vp09-cell'): g for g in ET.fromstring(svg).iter(G) if g.get('data-vp09-cell')}


def check(c, out):
    x, ok = c['expect'], True
    rep = out['report']
    if x.get('rendered'):
        ok = ok and rep.get('render_status') == 'PASS'
    if 'row_order' in x:
        ok = ok and rep['row_values'] == x['row_order']
    for want in x.get('cell_contains', []):
        key = f"{want['row']}|{want['col']}"
        g = cellgroups(out['svgs'][0]).get(key)
        ok = ok and want['entry'] in rep['cells'].get(key, []) and g is not None and want['entry'] in g.find(f'{{{NS}}}title').text
    if 'owner_absent' in x:
        o = x['owner_absent']
        ok = ok and not any(e.split(' · ')[0] == o for es in rep['cells'].values() for e in es)
        ok = ok and not any(u['owner'] == o for u in rep['binding_ledger'])
    for want in x.get('off_axis_includes', []):
        ok = ok and any(u['state'] == 'off_axis' and all(u.get(k) == v for k, v in want.items()) for u in rep['binding_ledger'])
        ok = ok and any(w['code'] == 'VP09_ARGUMENT_OFF_AXIS' and w['owner'] == want['owner'] and w['role'] == want['role']
                        for w in out['warnings'])
    if x.get('no_cells'):
        ok = ok and rep['cells'] == {} and rep['row_values'] == [] and not cellgroups(out['svgs'][0])
    if 'cells_of_entry' in x:
        e = x['cells_of_entry']['entry']
        got = sorted(k.split('|') for k, es in rep['cells'].items() if e in es)
        ok = ok and got == sorted(x['cells_of_entry']['cells'])
    if 'step_rule' in x:
        w = x['step_rule']
        ok = ok and any(u['owner'] == w['owner'] and u.get('step_rule') == w['rule'] and u.get('step') == w['step']
                        for u in rep['binding_ledger'])
    for want in x.get('dropped_includes', []):
        ok = ok and any(u['state'] == 'out_of_slice' and u['owner'] == want['owner'] and u['role'] == want['role']
                        for u in rep['binding_ledger'])
    if x.get('binding_coverage_complete'):
        ok = ok and rep['binding_coverage']['status'] == 'COMPLETE'
    if 'binding_coverage' in x:
        ok = ok and rep['binding_coverage'] == x['binding_coverage']
    if x.get('coverage_complete'):
        ok = ok and rep['coverage']['status'] == 'COMPLETE' and rep['panel_count'] >= x.get('panels_min', 1)
    if 'columns_total' in x:
        ok = ok and len({v for e in rep['panel_ledger'] for v in e['col_values']}) == x['columns_total']
    if 'equals_default_090' in x:
        ok = ok and out['same_090'] is x['equals_default_090']
    if 'units' in x:
        ok = ok and len(rep['units']) == x['units']
    if 'all_in_col' in x:
        a = x['all_in_col']
        mine = {k: es for k, es in rep['cells'].items() if k.split('|')[0] == a['row']}
        ok = ok and list(mine) == [f"{a['row']}|{a['col']}"] and len(mine[f"{a['row']}|{a['col']}"]) == a['n']
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    src = DOC['gm_pos_source']
    assert hashlib.sha256((REPO/src['path']).read_bytes()).hexdigest() == src['sha256'], 'P1.11 golden changed since materialisation (D-8)'
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
            if ok and status == 'FAIL':
                ok = all(s in msg for s in c['expect'].get('message_contains', []))
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg[:110])
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
