#!/usr/bin/env python3
"""Run O-01..O-15 (VP-07.5) against vpmigration through its Python API.

Exit 0 only if every case matches the independent oracle (oracles/independent_o01_o15.json).
Every PASS run is also re-checked with check_panels on the published directory.
"""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/o01_o15_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_o01_o15.json').read_text('utf-8'))['cases']}
G, T = f'{{{NS}}}g', f'{{{NS}}}text'
LAST = {}


def panels(src, t, tmp, name='panels'):
    rep, files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'),
                              locale=t.get('locale'), hide_ledger=t.get('hide_ledger', False))
    check_panels(publish_dir(files, Path(tmp)/name))
    return rep, files


def run(c, tmp):
    inp = c['input']
    if c['op'] == 'panels':
        rep, files = panels(inp['source'], inp, tmp)
        return {'warnings': rep['warnings'], 'report': rep, 'files': files}
    LAST.clear()
    src, mapping = from_plan(inp['context'], inp['plan_id'], profile=inp['profile'], **({'subjects': inp['subjects']} if 'subjects' in inp else {}))
    LAST['src'] = src
    rep, files = panels(src, inp['then'], tmp)
    out = {'source': src, 'report': rep, 'files': files, 'warnings': list(mapping.get('warnings', []))+rep['warnings']}
    if 'flow' in inp:
        out['flow_report'], out['flow_files'] = panels(src, inp['flow'], tmp, 'flow')
    return out


def svgs(files):
    return [ET.fromstring(b) for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]


def texts(roots):
    return [t.text or '' for r in roots for t in r.iter(T)]


def bar_texts(out, cell):
    return [t.text or '' for r in svgs(out['files']) for g in r.iter(G) if g.get('data-cell-id') == cell for t in g.iter(T)]


def plain(c, out, tmp):
    then = {k: v for k, v in c['input']['then'].items() if k != 'locale'}
    return panels(out['source'], then, tmp, 'plain')


def check(c, out, tmp):
    x, ok = c['expect'], True
    rep = out['report']
    roots = svgs(out['files'])
    tx = texts(roots)
    ok = ok and all(any(s == t for t in tx) or any(s in t for t in tx) for s in x.get('texts_contain', []))
    ok = ok and not any(s in t for s in x.get('texts_exclude', []) for t in tx)
    if 'report_locale' in x:
        ok = ok and rep.get('locale', {}).get('code') == x['report_locale']
    if x.get('ids_unchanged') or x.get('equals_no_locale'):
        prep, pfiles = plain(c, out, tmp)
        if x.get('ids_unchanged'):
            ok = ok and [e['shown_cell_ids'] for e in rep['panel_ledger']] == [e['shown_cell_ids'] for e in prep['panel_ledger']] \
                and [sorted(g.get('data-cell-id') for g in r.iter(G) if g.get('data-cell-id')) for r in roots] == \
                [sorted(g.get('data-cell-id') for g in r.iter(G) if g.get('data-cell-id')) for r in svgs(pfiles)]
        if x.get('equals_no_locale'):
            ok = ok and pfiles == out['files']
    if 'bar_label' in x:
        ok = ok and x['bar_label']['text'] in bar_texts(out, x['bar_label']['cell'])
    if 'bar_label_contains' in x:
        ok = ok and any(x['bar_label_contains']['text'] in t for t in bar_texts(out, x['bar_label_contains']['cell']))
    if x.get('ledger_hidden'):
        ok = ok and rep.get('ledger_hidden') is True and all(r.get('data-vp07-ledger-hidden') == 'true' for r in roots)
    if x.get('embedded_ledger_as_shown'):
        for r, e in zip(roots, rep['panel_ledger']):
            led = json.loads(next(y for y in r.iter() if y.get('id') == 'vp07-phases-ledger').text)
            ok = ok and led['shown_cell_ids'] == e['shown_cell_ids'] and led.get('ledger_hidden') is True
    if 'flow_texts_exclude' in x:
        froots = svgs(out['flow_files'])
        ftx = texts(froots)
        ok = ok and not any(s in t for s in x['flow_texts_exclude'] for t in ftx) and out['flow_report'].get('ledger_hidden') is True \
            and all(r.get('data-vp07-ledger-hidden') == 'true' for r in froots)
    ms = rep.get('method_sets')
    if 'set_order' in x:
        ok = ok and ms is not None and list(ms) == x['set_order']
    if 'set_cells' in x:
        ok = ok and ms is not None and {m: sorted(v['cells']) for m, v in ms.items()} == x['set_cells']
    if 'memberships' in x:
        ok = ok and all(rep.get('memberships', {}).get(k) == v for k, v in x['memberships'].items())
    if x.get('all_sets_complete'):
        ok = ok and ms is not None and all(v['status'] == 'COMPLETE' for v in ms.values())
    if 'min_panels_of_set' in x:
        w = x['min_panels_of_set']
        ok = ok and len(ms[w['set']]['panels']) >= w['n']
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
        msg = ''
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP07Error as e:
                out, status, codes, msg = None, 'FAIL', [e.code], str(e)
                diag = e.diagnostic()
            ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) \
                and not any(k in codes for k in c['forbidden_codes'])
            if ok and status == 'PASS':
                ok = check(c, out, tmp)
            if ok and 'diagnostic_profile' in c['expect']:
                ok = diag.get('profile') == c['expect']['diagnostic_profile']
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg[:110])
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
