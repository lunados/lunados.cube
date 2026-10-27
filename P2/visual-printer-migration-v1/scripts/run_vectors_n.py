#!/usr/bin/env python3
"""Run N-01..N-14 (VP-07.4) against vpmigration through its Python API.

Exit 0 only if every case matches the independent oracle (oracles/independent_n01_n14.json).
Panels are looked up by (step, key values), never by number.
"""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/n01_n14_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_n01_n14.json').read_text('utf-8'))['cases']}
G, T = f'{{{NS}}}g', f'{{{NS}}}text'


def fp(inp, profile='keep'):
    kw = {k: inp[k] for k in ('tracks', 'layers') if k in inp}
    prof = inp.get('profile') if profile == 'keep' else profile
    return from_plan(inp['context'], inp['plan_id'], profile=prof, **kw)


def panels(src, t, tmp, tamper=None):
    rep, files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))
    d = publish_dir(files, Path(tmp)/'panels')
    if tamper == 'edit_methods_line':
        f = next(d/n for n in sorted(files) if n.endswith('.input.json') and b'"methods_line"' in files[n])
        x = json.loads(f.read_text('utf-8'))
        x['methods_line']['transitions'][0]['methods'] = ['migrate.rebuild/v1']
        f.write_text(json.dumps(x, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    check_panels(d)
    return rep, files


def run(c, tmp):
    inp = c['input']
    if c['op'] == 'panels':
        rep, files = panels(inp['source'], inp, tmp)
        return {'warnings': rep['warnings'], 'report': rep, 'files': files}
    src, mapping = fp(inp)
    rep, files = panels(src, inp['then'], tmp, inp.get('tamper'))
    return {'source': src, 'report': rep, 'files': files, 'warnings': list(mapping.get('warnings', []))+rep['warnings']}


def method_of(src, cid):
    c = next(x for x in src['cells'] if x['id'] == cid)
    return c['method']['method_id'] if 'method' in c else 'none'


def panel(out, step, key, outer=None):
    for e in out['report']['panel_ledger']:
        if e.get('step') == step and e['key_values'] == [key] and e.get('outer_value') == outer:
            return e, ET.fromstring(out['files'][e['panel']+'.svg'])
    return None, None


def line_of(root):
    g = next((x for x in root.iter(G) if x.get('data-vp07-methods-line') is not None), None)
    if g is None:
        return None, None, None
    return g, g.get('data-vp07-methods-line').split(), [t.text or '' for t in g.iter(T)]


def check(c, out, tmp):
    x, ok = c['expect'], True
    src, rep = out.get('source') or out['report']['source'], out['report']
    led = rep['panel_ledger']
    if 'group_order' in x:
        seq = []
        for e in led:
            if e['key_values'] not in seq:
                seq.append(e['key_values'])
        ok = ok and seq == x['group_order']
    if x.get('groups_pure'):
        ok = ok and all(len({method_of(src, cid) for cid in e['shown_cell_ids']}) == 1 for e in led)
    if 'group_cells' in x:
        got = {}
        for e in led:
            for cid in e['shown_cell_ids']:
                got.setdefault(method_of(src, cid), set()).add(cid)
        ok = ok and {k: sorted(v) for k, v in got.items()} == x['group_cells']
    if x.get('coverage_complete'):
        ok = ok and rep['coverage']['status'] == 'COMPLETE'
    if 'min_panels_of' in x:
        ok = ok and sum(e['key_values'] == [x['min_panels_of']['key']] for e in led) >= x['min_panels_of']['n']
    if 'subtitle_contains' in x:
        w = x['subtitle_contains']
        roots = [ET.fromstring(out['files'][e['panel']+'.svg']) for e in led if e['key_values'] == [w['key']]]
        ok = ok and bool(roots) and all(any(w['text'] in (t.text or '') for t in r.iter(T)) for r in roots)
    if 'outer_complete' in x:
        st = {o['outer_value']: o['status'] for o in rep.get('outer_ledger', [])}
        ok = ok and all(st.get(v) == 'COMPLETE' for v in x['outer_complete'])
    for k in ('line', 'line_2'):
        if k in x:
            w = x[k]
            _, root = panel(out, w['step'], w['key'])
            g, codes, texts = line_of(root) if root is not None else (None, None, None)
            whole = ' '.join(texts or [])
            ok = ok and g is not None and codes == w['codes'] and all(s in whole for s in w.get('contains', [])) \
                and not any(s in whole for s in w.get('excludes', []))
    if 'no_line_steps' in x:
        for e in led:
            if e.get('step') in x['no_line_steps']:
                ok = ok and line_of(ET.fromstring(out['files'][e['panel']+'.svg']))[0] is None
    if 'line_overflow' in x:
        w = x['line_overflow']
        e, root = panel(out, w['step'], w['key'], w.get('outer'))
        g, codes, texts = line_of(root)
        title = g.find(f'{{{NS}}}title').text
        ok = ok and len(codes) == w['codes_total'] and len(texts) <= w['max_text_lines'] and 'more' in texts[-1] \
            and all(f'{cd} ' in title for cd in codes) and len(e['panel_report']['methods']['transitions']) == w['codes_total']
    if 'edge_method' in x:
        w = x['edge_method']
        _, root = panel(out, w['step'], w['key'])
        ref = next(cc['declaration_ref'] for cc in src['cells'] if cc['id'] == w['cell'])
        g = next((y for y in root.iter(G) if y.get('data-edge-id') and y.get('data-declaration-ref') == ref), None)
        ok = ok and g is not None and g.get('data-vp07-method') == w['method']
        if x.get('edge_geometry_as_073'):
            s73, _ = fp(c['input'], profile=None)
            _, f73 = panels(s73, c['input']['then'], tmp+'/g73')
            r73 = next(ET.fromstring(f73[e['panel']+'.svg']) for e in print_panels(s73, *[c['input']['then'][k] for k in ('view', 'partition', 'granularity', 'lens')])[0]['panel_ledger']
                       if e.get('step') == w['step'] and e['key_values'] == [w['key']])
            g73 = next(y for y in r73.iter(G) if y.get('data-edge-id') and y.get('data-declaration-ref') == ref)
            geo = lambda gg: [(ch.tag, sorted(ch.attrib.items()), ch.text) for ch in gg if ch.tag != f'{{{NS}}}title']  # noqa: E731
            ok = ok and geo(g) == geo(g73)
    if 'both_lines' in x:
        _, root = panel(out, x['both_lines']['step'], x['both_lines']['key'])
        ok = ok and any(y.get('data-vp07-layers') for y in root.iter(G)) and line_of(root)[0] is not None
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
            except VP07Error as e:
                out, status, codes, msg = None, 'FAIL', [e.code], str(e)
            ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) \
                and not any(k in codes for k in c['forbidden_codes'])
            if ok and status == 'PASS':
                ok = check(c, out, tmp)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg[:110])
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
