"""VP-12 §1.11, D-7: one panel per plan; index, report with panel ledger; check-panels re-renders and compares."""
from __future__ import annotations
import copy
import json
from xml.etree import ElementTree as ET

from .common import (PROFILE, VIEW, PANEL_INPUT, REPORT_FORMAT, CHECK_FORMAT, NS, Printer, add, text, excerpt, encode, sha_bytes,
                     sha_json, no_active_content, MUTED, INK, NOT_EVALUATED, need, fs_isdir, fs_names, fs_bytes, VP07Error)
from .landscape import render_landscape, _printer


def render_input(inp):
    need(isinstance(inp, dict) and inp.get('format') == PANEL_INPUT and inp.get('profile') == PROFILE, 'VP12_PANEL_COVERAGE',
         'not a VP-12 panel input', 'coverage')
    return render_landscape(inp['input'])


def _index(rows, title):
    P = _printer()
    h = 200+28*len(rows)
    root = P._root({'title': excerpt(title, 78), 'subtitle': 'cube.landscape · '+PROFILE, 'view_id': VIEW}, h)
    root.set('data-printer-profile', PROFILE)
    for k, (name, rep) in enumerate(rows):
        g = add(root, 'g', **{'data-vp12-index-entry': name})
        text(g, 42, 130+28*k, name, 14, INK, 'bold')
        text(g, 180, 130+28*k, excerpt(' / '.join(b['step'] for b in rep['bands'])+f" · {rep['counts']['units']} units · "
                                       + rep['crossing_status']['text'], 90), 13, MUTED)
    root2 = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(root2)), 'VP12_AUDIT', 'index has active content', 'audit')
    return root2


def print_panels(doc):
    inp = {'format': PANEL_INPUT, 'profile': PROFILE, 'input': copy.deepcopy(doc)}
    rep, svg = render_input(inp)
    raw = encode(inp)
    name = 'panel-01'
    files = {name+'.svg': svg, name+'.input.json': raw}
    entry = {'panel': name, 'steps': [b['step'] for b in rep['bands']], 'units': rep['units'], 'svg_sha256': sha_bytes(svg),
             'input_sha256': sha_bytes(raw)}
    files['index.svg'] = _index([(name, rep)], f"{doc['source']['plan_id']} · cube.landscape")
    report = {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'view': VIEW, 'plan_id': doc['source']['plan_id'],
              'panel_count': 1, 'panel_ledger': [entry], 'index_sha256': sha_bytes(files['index.svg']),
              'coverage': {'units_total': len(rep['units']), 'units_in_panels': len(entry['units']), 'status': 'COMPLETE'},
              'columns': rep['columns'], 'bands': rep['bands'], 'x_outside': rep['x_outside'], 'crossing_status': rep['crossing_status'],
              'warnings': rep['warnings'], 'source_sha256': rep['source_sha256'], 'content_status': 'declared_unverified', **NOT_EVALUATED}
    files['report.json'] = encode(report)
    return report, files


def check_files(d):
    """d: a directory Path or a {name: bytes} mapping (G6 later)."""
    need(fs_isdir(d), 'VP12_PANEL_COVERAGE', 'not a panel directory', 'coverage')
    names = fs_names(d)
    need('report.json' in names and 'index.svg' in names, 'VP12_PANEL_COVERAGE', 'report.json or index.svg missing', 'coverage')
    rep = json.loads(fs_bytes(d, 'report.json'))
    need(rep.get('format') == REPORT_FORMAT and rep.get('profile') == PROFILE, 'VP12_PANEL_COVERAGE', 'not a VP-12 panel report', 'coverage')
    want = {e['panel']+x for e in rep['panel_ledger'] for x in ('.svg', '.input.json')} | {'report.json', 'index.svg'}
    need(set(names) == want, 'VP12_PANEL_COVERAGE', 'files differ from the panel ledger', 'coverage')
    checked = []
    for e in rep['panel_ledger']:
        raw = fs_bytes(d, e['panel']+'.input.json')
        need(sha_bytes(raw) == e['input_sha256'], 'VP12_PANEL_COVERAGE', e['panel']+': input digest differs', 'coverage')
        r, svg = render_input(json.loads(raw))
        need(svg == fs_bytes(d, e['panel']+'.svg') and sha_bytes(svg) == e['svg_sha256'], 'VP12_PANEL_COVERAGE',
             e['panel']+': re-rendered SVG differs', 'coverage')
        need(r['units'] == e['units'] and r['bands'] == rep['bands'] and r['x_outside'] == rep['x_outside'], 'VP12_PANEL_COVERAGE',
             e['panel']+': ledger differs from the report', 'coverage')
        doc = json.loads(raw)['input']
        checked.append((e['panel'], r))
    idx = _index(checked, f"{doc['source']['plan_id']} · cube.landscape")
    need(idx == fs_bytes(d, 'index.svg') and sha_bytes(idx) == rep['index_sha256'], 'VP12_PANEL_COVERAGE', 'index differs', 'coverage')
    return {'format': CHECK_FORMAT, 'profile': PROFILE, 'status': 'PASS', 'panels': len(checked),
            'units': sum(len(r['units']) for _, r in checked), 'coverage': 'COMPLETE', **NOT_EVALUATED}


def check_panels(path):
    from pathlib import Path
    return check_files(Path(path))
