"""VP-09 panels (D-9, AQ-5): split along rows, then columns; coverage of (row, column, entry) units; text index."""
from __future__ import annotations
import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import (PROFILE, P091, P092, V91UP, tag_profile, via07, BUDGET, NOT_EVALUATED, MUTED, Printer, add, line, text, excerpt, sha_bytes, sha_json, encode, load_json, fs_isdir, fs_names, fs_bytes, fs_json,
                     need, no_active_content, VP09Error)
from .axes import AxesPrinter, binding_coverage, binding_warnings, warning_summary, _locale
from .source import profile_of

PANEL_INPUT = 'aiaeao.cube.vp09-panel-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp09-panel-report/1'
CHECK_FORMAT = 'aiaeao.cube.vp09-panel-check/1'
MAX_PANELS = 99


def render_input(inp):
    need(isinstance(inp, dict) and inp.get('format') == PANEL_INPUT, 'VP09_PANEL_COVERAGE', 'not a VP-09 panel input', 'coverage')
    p = AxesPrinter()
    opts = {k: inp[k] for k in ('hide_empty', 'locale') if k in inp}  # VP-09.2 display options travel with the panel input
    pr = p.project(inp['input'], inp['rows'], inp['cols'], inp['granularity'], inp['row_values'], inp['col_values'], **opts)
    need([v for v, _, _ in pr['rv']] == inp['row_values'] and [v for v, _, _ in pr['cv']] == inp['col_values'], 'VP09_PANEL_COVERAGE',
         'panel values differ from the input', 'coverage')
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg


def _chunks(vals, cap):
    return [vals[i:i+cap] for i in range(0, len(vals), cap)] or [[]]


def print_panels(doc, rows, cols, granularity='standard', hide_empty=None, locale=None):
    p = AxesPrinter()
    opts = {k: v for k, v in (('hide_empty', hide_empty), ('locale', locale)) if v is not None}
    full = p.project(doc, rows, cols, granularity, budget_check=False, **opts)
    prof = profile_of(doc)
    fb = prof in V91UP and full['fpair']                        # VP-09.1 binding ledger over panels (FL-3)
    rcap, ccap, _ = BUDGET[granularity]
    rv = [v for v, _, _ in full['rv']]; cv = [v for v, _, _ in full['cv']]
    need(granularity != 'detail' or (len(rv) <= rcap and len(cv) <= ccap), 'VP09_AXES_BUDGET',
         f'{len(rv)} rows / {len(cv)} columns exceed detail ({rcap}/{ccap}); detail never splits (AQ-5)', 'granularity')
    sets = [(r, c) for r in _chunks(rv, rcap) for c in _chunks(cv, ccap)]
    need(len(sets) <= MAX_PANELS, 'VP09_AXES_BUDGET', f'{len(sets)} panels exceed {MAX_PANELS}', 'granularity')
    files, entries, warnings = {}, [], []
    for i, (rs, cs) in enumerate(sets):
        name = f'panel-{i+1:02d}'
        inp = {'format': PANEL_INPUT, 'profile': prof, 'input': copy.deepcopy(doc), 'rows': rows, 'cols': cols, 'granularity': granularity,
               'row_values': rs, 'col_values': cs, **opts}
        rep, svg = render_input(inp)
        raw = encode(inp)
        files[name+'.svg'] = svg
        files[name+'.input.json'] = raw
        warnings += [dict(w, panel=name) for w in rep['warnings'] if w['code'] != 'VP09_ALL_EMPTY']
        e = {'panel': name, 'row_values': rs, 'col_values': cs, 'units': rep['units'], 'svg_sha256': sha_bytes(svg),
             'input_sha256': sha_bytes(raw)}
        if fb:
            e['binding_units'] = rep['binding_units']
        entries.append(e)
    total = sorted(f'{r}|{c}|{e}' for (r, c), es in full['cells'].items() for e in es)
    cov = _coverage(total, entries)
    need(cov['status'] == 'COMPLETE', 'VP09_PANEL_COVERAGE', 'panels do not cover units', 'coverage')
    extra = {}
    if fb:
        bcov = binding_coverage(full['units_b'], [u for e in entries for u in e['binding_units']])
        need(bcov['status'] == 'COMPLETE', 'VP09_PANEL_COVERAGE', 'panels do not account for every binding unit (FL-3)', 'coverage')
        warnings += binding_warnings(full['units_b'])
        extra = {'binding_ledger': full['units_b'], 'binding_coverage': bcov}
    if prof == P092:
        h = full['hidden']
        if full['all_empty']:
            warnings.append({'code': 'VP09_ALL_EMPTY', 'hidden_rows': len(h['hidden_rows']), 'hidden_cols': len(h['hidden_cols'])})
        if h:
            extra.update({k: h[k] for k in ('hide_empty', 'row_values_all', 'col_values_all', 'hidden_rows', 'hidden_cols', 'hidden_counts')})
        if not full['L'].identity:
            extra['locale'] = full['L'].record()
    files['index.svg'] = _index(full, entries, cov, prof)
    if prof == P092:
        extra['warning_summary'] = warning_summary(warnings)
    report = {'format': REPORT_FORMAT, 'profile': prof, **extra, 'reference_version': 'v9.4', 'status': 'PASS', 'view': 'cube.axes',
              'rows_axis': rows, 'cols_axis': cols, 'granularity': granularity, 'input_sha256': sha_json(doc), 'input': doc,
              'panel_count': len(entries), 'panel_ledger': entries, 'coverage': cov, 'all_units': total, 'warnings': warnings,
              'files': {k: sha_bytes(b) for k, b in sorted(files.items())}, 'source_status': 'declared_unverified', **NOT_EVALUATED,
              'notices': ['Panels split along rows, then columns, in declared order (D-9).',
                          'The index is a drawn table of contents; it embeds no panel.']}
    files['report.json'] = encode(report)
    return report, files


def _coverage(total, entries):
    covered = sorted({u for e in entries for u in e['units']})
    missing = sorted(set(total)-set(covered))
    return {'status': 'COMPLETE' if not missing and set(covered) <= set(total) else 'INCOMPLETE', 'units_total': len(total),
            'units_covered': len(covered), 'uncovered_units': missing[:20]}


def _span(vals, what, L=None):
    if L is not None and not L.identity and vals:
        return L.t('axes.index.'+('rows' if what == 'rows' else 'cols'), '', first=vals[0], last=vals[-1], n=len(vals))
    if L is not None and not L.identity:
        return L.t('axes.index.'+('rows' if what == 'rows' else 'cols'), '', first='–', last='–', n=0)
    return f"{what} {vals[0]} … {vals[-1]} ({len(vals)})" if vals else f"{what} – (0)"


def _index(full, entries, cov, prof=PROFILE):
    L = full.get('L') or _locale(None)
    T_ = L.t
    base = Printer()
    h = 240+len(entries)*24+60
    pair = f"{full['rows']} × {full['cols']}"
    root = base._root({'view_id': 'vp09.panel-index', 'title': excerpt(T_('index.title', 'Panels · ')+full['model'].src['title'], 72),
                       'subtitle': excerpt(T_('axes.index.subtitle', '{printer} · cube.axes {pair} · {granularity} · text-only index, no thumbnails',
                                              printer='VP-09', pair=pair, granularity=full['granularity']), 105)}, h)
    root.set('data-printer-profile', prof)
    root.set('data-vp09-index', 'display-only')
    text(root, 60, 125, T_('axes.index.header', 'PANEL INDEX · coverage of declared (row, column, entry) units · not a verdict'), 13, MUTED, 'bold')
    y = 160
    for e in entries:
        g = add(root, 'g', **{'data-vp09-panel': e['panel']})
        text(g, 68, y, e['panel'], 12, '#0F172A', 'bold')
        text(g, 170, y, excerpt(_span(e['row_values'], 'rows', L), 60), 12, '#334155')
        text(g, 600, y, excerpt(_span(e['col_values'], 'columns', L), 40), 12, '#334155')
        text(g, 900, y, e['svg_sha256'][:16]+'…', 10, MUTED)
        y += 24
    line(root, 60, y, 1140, y, '#E2E8F0')
    text(root, 68, y+28, T_('axes.index.coverage', 'Coverage {status} · {covered}/{total} units', status=cov['status'], covered=cov['units_covered'],
                            total=cov['units_total']), 12, MUTED, 'bold')
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP09_AUDIT', 'index contains active content', 'audit')
    return via07(L.post, svg, 'index', 'VP09_AUDIT')


def check_panels(directory):
    """Directory form (CLI); reads files and applies the same checks as check_files (G6 MA-2)."""
    return _check(Path(directory))


def check_files(files):
    """In-memory form (G6 MA-2): `files` maps the names print-panels writes to their bytes."""
    need(isinstance(files, dict), 'VP09_PANEL_COVERAGE', 'files must be a mapping of names to bytes', 'coverage')
    return _check(dict(files))


def _check(d):
    need(fs_isdir(d), 'VP09_PANEL_COVERAGE', 'not a directory: '+str(d), 'coverage')
    rep = fs_json(d, 'report.json', 'VP09_PANEL_COVERAGE')
    need(isinstance(rep, dict) and rep.get('format') == REPORT_FORMAT, 'VP09_PANEL_COVERAGE', 'report.json is not a VP-09 panel report', 'coverage')
    listed = rep.get('files', {})
    present = [n for n in fs_names(d) if n != 'report.json']
    need(present == sorted(listed), 'VP09_PANEL_COVERAGE', 'directory files differ from report file list', 'coverage')
    need(sha_json(rep['input']) == rep['input_sha256'], 'VP09_PANEL_COVERAGE', 'embedded input digest mismatch', 'coverage')
    for e in rep['panel_ledger']:
        inp = fs_json(d, e['panel']+'.input.json', 'VP09_PANEL_COVERAGE')
        need(inp.get('input') == rep['input'], 'VP09_PANEL_COVERAGE', e['panel']+': panel input differs from the embedded input', 'coverage')
        try:
            prep, svg = render_input(inp)
        except VP09Error as x:
            raise VP09Error('VP09_PANEL_COVERAGE', e['panel']+': input does not re-render: '+str(x), 'coverage') from x
        need(svg == fs_bytes(d, e['panel']+'.svg', 'VP09_PANEL_COVERAGE') and sha_bytes(svg) == e['svg_sha256'], 'VP09_PANEL_COVERAGE',
             e['panel']+': SVG differs from deterministic re-render of its input', 'coverage')
        need(prep['units'] == e['units'], 'VP09_PANEL_COVERAGE', e['panel']+': ledger units differ', 'coverage')
        need(prep.get('binding_units') == e.get('binding_units'), 'VP09_PANEL_COVERAGE', e['panel']+': binding units differ (FL-3)', 'coverage')
    for name, digest in listed.items():
        need(sha_bytes(fs_bytes(d, name, 'VP09_PANEL_COVERAGE')) == digest, 'VP09_PANEL_COVERAGE', 'file digest mismatch: '+name, 'coverage')
    opts = {k: v for k, v in (('hide_empty', rep.get('hide_empty')), ('locale', (rep.get('locale') or {}).get('code'))) if v is not None}
    full = AxesPrinter().project(rep['input'], rep['rows_axis'], rep['cols_axis'], rep['granularity'], budget_check=False, **opts)
    total = sorted(f'{r}|{c}|{e}' for (r, c), es in full['cells'].items() for e in es)
    cov = _coverage(total, rep['panel_ledger'])
    need(total == rep['all_units'] and cov == rep['coverage'] and cov['status'] == 'COMPLETE', 'VP09_PANEL_COVERAGE',
         'union of panels does not reproduce the recorded complete coverage', 'coverage')
    prof = profile_of(rep['input'])
    if prof in V91UP and full['fpair']:
        bcov = binding_coverage(full['units_b'], [u for e in rep['panel_ledger'] for u in e.get('binding_units', [])])
        need(bcov == rep.get('binding_coverage') and full['units_b'] == rep.get('binding_ledger') and bcov['status'] == 'COMPLETE',
             'VP09_PANEL_COVERAGE', 'union of panels does not reproduce the recorded binding coverage (FL-3)', 'coverage')
    return {'format': CHECK_FORMAT, 'profile': prof, 'status': 'PASS', 'panels': len(rep['panel_ledger']), 'coverage': cov, **NOT_EVALUATED}


print_panels = tag_profile(print_panels, lambda doc, *a, **k: profile_of(doc) if isinstance(doc, dict) else None)
