"""VP-09 panels (D-9, AQ-5): split along rows, then columns; coverage of (row, column, entry) units; text index."""
from __future__ import annotations
import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import (PROFILE, P091, BUDGET, NOT_EVALUATED, MUTED, Printer, add, line, text, excerpt, sha_bytes, sha_json, encode, load_json,
                     need, no_active_content, VP09Error)
from .axes import AxesPrinter, binding_coverage, binding_warnings
from .source import profile_of

PANEL_INPUT = 'aiaeao.cube.vp09-panel-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp09-panel-report/1'
CHECK_FORMAT = 'aiaeao.cube.vp09-panel-check/1'
MAX_PANELS = 99


def render_input(inp):
    need(isinstance(inp, dict) and inp.get('format') == PANEL_INPUT, 'VP09_PANEL_COVERAGE', 'not a VP-09 panel input', 'coverage')
    p = AxesPrinter()
    pr = p.project(inp['input'], inp['rows'], inp['cols'], inp['granularity'], inp['row_values'], inp['col_values'])
    need([v for v, _, _ in pr['rv']] == inp['row_values'] and [v for v, _, _ in pr['cv']] == inp['col_values'], 'VP09_PANEL_COVERAGE',
         'panel values differ from the input', 'coverage')
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg


def _chunks(vals, cap):
    return [vals[i:i+cap] for i in range(0, len(vals), cap)] or [[]]


def print_panels(doc, rows, cols, granularity='standard'):
    p = AxesPrinter()
    full = p.project(doc, rows, cols, granularity, budget_check=False)
    prof = profile_of(doc)
    fb = prof == P091 and full['fpair']                        # VP-09.1 binding ledger over panels (FL-3)
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
               'row_values': rs, 'col_values': cs}
        rep, svg = render_input(inp)
        raw = encode(inp)
        files[name+'.svg'] = svg
        files[name+'.input.json'] = raw
        warnings += [dict(w, panel=name) for w in rep['warnings']]
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
    files['index.svg'] = _index(full, entries, cov, prof)
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


def _span(vals, what):
    return f"{what} {vals[0]} … {vals[-1]} ({len(vals)})" if vals else f"{what} – (0)"


def _index(full, entries, cov, prof=PROFILE):
    base = Printer()
    h = 240+len(entries)*24+60
    pair = f"{full['rows']} × {full['cols']}"
    root = base._root({'view_id': 'vp09.panel-index', 'title': excerpt('Panels · '+full['model'].src['title'], 72),
                       'subtitle': excerpt(f"VP-09 · cube.axes {pair} · {full['granularity']} · text-only index, no thumbnails", 105)}, h)
    root.set('data-printer-profile', prof)
    root.set('data-vp09-index', 'display-only')
    text(root, 60, 125, 'PANEL INDEX · coverage of declared (row, column, entry) units · not a verdict', 13, MUTED, 'bold')
    y = 160
    for e in entries:
        g = add(root, 'g', **{'data-vp09-panel': e['panel']})
        text(g, 68, y, e['panel'], 12, '#0F172A', 'bold')
        text(g, 170, y, excerpt(_span(e['row_values'], 'rows'), 60), 12, '#334155')
        text(g, 600, y, excerpt(_span(e['col_values'], 'columns'), 40), 12, '#334155')
        text(g, 900, y, e['svg_sha256'][:16]+'…', 10, MUTED)
        y += 24
    line(root, 60, y, 1140, y, '#E2E8F0')
    text(root, 68, y+28, f"Coverage {cov['status']} · {cov['units_covered']}/{cov['units_total']} units", 12, MUTED, 'bold')
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP09_AUDIT', 'index contains active content', 'audit')
    return svg


def check_panels(directory):
    d = Path(directory)
    need(d.is_dir(), 'VP09_PANEL_COVERAGE', 'not a directory: '+str(d), 'coverage')
    rep = load_json(d/'report.json', 'VP09_PANEL_COVERAGE')
    need(isinstance(rep, dict) and rep.get('format') == REPORT_FORMAT, 'VP09_PANEL_COVERAGE', 'report.json is not a VP-09 panel report', 'coverage')
    listed = rep.get('files', {})
    present = sorted(p.name for p in d.iterdir() if p.is_file() and p.name != 'report.json')
    need(present == sorted(listed), 'VP09_PANEL_COVERAGE', 'directory files differ from report file list', 'coverage')
    need(sha_json(rep['input']) == rep['input_sha256'], 'VP09_PANEL_COVERAGE', 'embedded input digest mismatch', 'coverage')
    for e in rep['panel_ledger']:
        inp = load_json(d/(e['panel']+'.input.json'), 'VP09_PANEL_COVERAGE')
        need(inp.get('input') == rep['input'], 'VP09_PANEL_COVERAGE', e['panel']+': panel input differs from the embedded input', 'coverage')
        try:
            prep, svg = render_input(inp)
        except VP09Error as x:
            raise VP09Error('VP09_PANEL_COVERAGE', e['panel']+': input does not re-render: '+str(x), 'coverage') from x
        need(svg == (d/(e['panel']+'.svg')).read_bytes() and sha_bytes(svg) == e['svg_sha256'], 'VP09_PANEL_COVERAGE',
             e['panel']+': SVG differs from deterministic re-render of its input', 'coverage')
        need(prep['units'] == e['units'], 'VP09_PANEL_COVERAGE', e['panel']+': ledger units differ', 'coverage')
        need(prep.get('binding_units') == e.get('binding_units'), 'VP09_PANEL_COVERAGE', e['panel']+': binding units differ (FL-3)', 'coverage')
    for name, digest in listed.items():
        need(sha_bytes((d/name).read_bytes()) == digest, 'VP09_PANEL_COVERAGE', 'file digest mismatch: '+name, 'coverage')
    full = AxesPrinter().project(rep['input'], rep['rows_axis'], rep['cols_axis'], rep['granularity'], budget_check=False)
    total = sorted(f'{r}|{c}|{e}' for (r, c), es in full['cells'].items() for e in es)
    cov = _coverage(total, rep['panel_ledger'])
    need(total == rep['all_units'] and cov == rep['coverage'] and cov['status'] == 'COMPLETE', 'VP09_PANEL_COVERAGE',
         'union of panels does not reproduce the recorded complete coverage', 'coverage')
    prof = profile_of(rep['input'])
    if prof == P091 and full['fpair']:
        bcov = binding_coverage(full['units_b'], [u for e in rep['panel_ledger'] for u in e.get('binding_units', [])])
        need(bcov == rep.get('binding_coverage') and full['units_b'] == rep.get('binding_ledger') and bcov['status'] == 'COMPLETE',
             'VP09_PANEL_COVERAGE', 'union of panels does not reproduce the recorded binding coverage (FL-3)', 'coverage')
    return {'format': CHECK_FORMAT, 'profile': prof, 'status': 'PASS', 'panels': len(rep['panel_ledger']), 'coverage': cov, **NOT_EVALUATED}
