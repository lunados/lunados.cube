#!/usr/bin/env python3
"""Run H-01..H-16 (VP-09.2) against vpaxes through its Python API. Exit 0 only if every case matches the oracle.

Panel runs are re-checked with check_panels on the published directory.
"""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels  # noqa: E402
from vpaxes.common import publish_dir, NS, SEPS  # noqa: E402

VEC = json.loads((HERE/'fixtures/h01_h16_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_h01_h16.json').read_text('utf-8'))['cases']}
G, T, TI = f'{{{NS}}}g', f'{{{NS}}}text', f'{{{NS}}}title'


def opts(inp, drop=()):
    return {k: inp[k] for k in ('hide_empty', 'locale') if k in inp and k not in drop}


def run(c, tmp):
    inp = c['input']
    kw = {'subjects': inp['subjects']} if 'subjects' in inp else {}
    doc, _ = from_plan(inp['context'], inp['plan_id'], profile=inp['profile'], **kw)
    if c['op'] == 'render':
        rep, svg = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'], **opts(inp))
        out = {'warnings': rep['warnings'], 'report': rep, 'svgs': [svg], 'doc': doc}
        if 'locale' in inp:
            out['plain'] = render_axes(doc, inp['rows'], inp['cols'], inp['granularity'], **opts(inp, ('locale',)))[0]
        return out
    rep, files = print_panels(doc, inp['rows'], inp['cols'], inp['granularity'], **opts(inp))
    check_panels(publish_dir(files, Path(tmp)/'panels'))
    return {'warnings': rep['warnings'], 'report': rep, 'files': files,
            'svgs': [b for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]}


def cellgroups(svg):
    return {g.get('data-vp09-cell'): g for g in ET.fromstring(svg).iter(G) if g.get('data-vp09-cell')}


def cell_lines(g):
    return [t.text or '' for t in g.iter(T)]


def wrapped_ok(lines, entry):
    """The entry is drawn on >= 2 consecutive lines that rebuild it exactly; every break follows a space or a separator."""
    for i in range(len(lines)):
        acc, j = lines[i], i
        while len(acc) < len(entry) and j+1 < len(lines):
            nxt = lines[j+1]
            if entry.startswith(acc+' '+nxt):
                acc, brk = acc+' '+nxt, True
            elif entry.startswith(acc+nxt) and acc and acc[-1] in SEPS:
                acc = acc+nxt
            else:
                break
            j += 1
        if acc == entry and j > i:
            return True
    return False


def check(c, out):
    x, ok = c['expect'], True
    rep = out['report']
    for want in x.get('cell_contains', []):
        key = f"{want['row']}|{want['col']}"
        g = cellgroups(out['svgs'][0]).get(key)
        ok = ok and want['entry'] in rep['cells'].get(key, []) and g is not None and want['entry'] in g.find(TI).text
    for want in x.get('cell_absent', []):
        ok = ok and f"{want['row']}|{want['col']}" not in rep['cells']
    if x.get('no_cells'):
        ok = ok and rep['cells'] == {} and not cellgroups(out['svgs'][0])
    if x.get('binding_coverage_complete'):
        ok = ok and rep['binding_coverage']['status'] == 'COMPLETE'
    if 'col_values' in x:
        ok = ok and rep['col_values'] == x['col_values']
    if 'hidden_cols_include' in x:
        ok = ok and set(x['hidden_cols_include']) <= set(rep.get('hidden_cols', [])) and rep['hidden_counts']['cols'] == len(rep['hidden_cols'])
    if x.get('coverage_complete'):
        ok = ok and rep['coverage']['status'] == 'COMPLETE'
    if 'wrapped_at_separators' in x:
        w = x['wrapped_at_separators']
        g = cellgroups(out['svgs'][0]).get(f"{w['row']}|{w['col']}")
        ok = ok and g is not None and wrapped_ok(cell_lines(g), w['entry']) and not any(s.endswith('…') for s in cell_lines(g))
    if 'shortened_with_title' in x:
        w = x['shortened_with_title']
        g = cellgroups(out['svgs'][0]).get(f"{w['row']}|{w['col']}")
        ok = ok and g is not None and any(s.endswith('…') for s in cell_lines(g)) and w['entry'] in g.find(TI).text \
            and w['entry'] in rep['cells'][f"{w['row']}|{w['col']}"]
    if 'texts_contain' in x:
        tx = [t.text or '' for b in out['svgs'] for t in ET.fromstring(b).iter(T)]
        ok = ok and all(s in tx for s in x['texts_contain'])
    if x.get('row_values_unchanged'):
        ok = ok and rep['row_values'] == out['plain']['row_values'] and rep['col_values'] == out['plain']['col_values'] \
            and rep['cells'] == out['plain']['cells']
    if 'report_locale' in x:
        ok = ok and rep.get('locale', {}).get('code') == x['report_locale']
    if 'summary' in x:
        got = {s['code']: s for s in rep.get('warning_summary', [])}
        w = x['summary']
        ok = ok and w['code'] in got and got[w['code']]['count'] == w['count'] and len(got[w['code']]['items']) == w['count']
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['forbidden_codes'], c['expect']) == \
            (o['expected_status'], o['required_codes'], o['forbidden_codes'], o['expect']), c['id']+': vector differs from oracle'
        msg, diag = '', {}
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP09Error as e:
                out, status, codes, msg, diag = None, 'FAIL', [e.code], str(e), e.diagnostic()
            ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) \
                and not any(k in codes for k in c['forbidden_codes'])
            if ok and status == 'PASS':
                ok = check(c, out)
            if ok and 'diagnostic_profile' in c['expect']:
                ok = diag.get('profile') == c['expect']['diagnostic_profile']
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg[:110])
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
