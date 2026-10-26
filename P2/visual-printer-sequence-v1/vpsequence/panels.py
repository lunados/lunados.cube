"""VP-08 panel export (ST-2…ST-4): one panel per trigger window, coverage of (trigger, message) units, text index."""
from __future__ import annotations
import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import (PROFILE, LEVELS, OVERFLOWS, NOT_EVALUATED, Printer, add, line, text, excerpt, sha_bytes, sha_json, encode,
                     load_json, need, no_active_content, MUTED, VP08Error)
from .source import validate_source
from .sequence import SequencePrinter, _msgs

PARTITIONS = ('trigger', 'use_case')
INPUT_FORMAT = 'aiaeao.cube.vp08-panel-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp08-panel-report/1'
CHECK_FORMAT = 'aiaeao.cube.vp08-panel-check/1'
MAX_PANELS = 99


def _order(src, partition):
    trigs = src['triggers']
    if partition == 'trigger':
        return [t['id'] for t in trigs]
    groups, order = {}, []
    for t in trigs:
        g = t.get('use_case', t['id'])
        if g not in groups:
            order.append(g); groups[g] = []
        groups[g].append(t['id'])
    return [tid for g in order for tid in groups[g]]


def _mini(src, trigger_id):
    """Panel input source: all participants, the one trigger; renders exactly like the full source."""
    s = {k: copy.deepcopy(v) for k, v in src.items() if k != 'triggers'}
    s['triggers'] = [copy.deepcopy(next(t for t in src['triggers'] if t['id'] == trigger_id))]
    return s


def render_input(inp):
    need(isinstance(inp, dict) and inp.get('format') == INPUT_FORMAT, 'VP08_PANEL_COVERAGE', 'not a VP-08 panel input', 'coverage')
    p = SequencePrinter()
    pr = p.project(inp['source'], inp['trigger_id'], inp['granularity'], inp['overflow'])
    k = inp['window']-1
    need(0 <= k < len(pr['windows']), 'VP08_PANEL_COVERAGE', 'panel window out of range', 'coverage')
    svg, lay = p.render_window(pr, k)
    rep = p.report(inp['source'], pr, [p.render_window(pr, j) for j in range(len(pr['windows']))])
    return rep, svg, [f"{inp['trigger_id']}@{m['id']}" for it in lay['items'] for m in _msgs(it)]


def _all_units(src):
    return sorted(f"{t['id']}@{m['id']}" for t in src['triggers'] for it in t['sequence'] for m in _msgs(it))


def build_panels(src, partition='trigger', granularity='standard', overflow='summarize'):
    validate_source(src)
    need(partition in PARTITIONS, 'VP08_PANEL_COVERAGE', 'partition must be trigger|use_case, got '+repr(partition), 'partition')
    need(granularity in LEVELS, 'VP08_SEQUENCE_BUDGET', 'granularity must be overview|standard|detail', 'granularity')
    need(overflow in OVERFLOWS, 'VP08_SEQUENCE_BUDGET', 'overflow must be summarize or reject', 'granularity')
    inputs = []
    for tid in _order(src, partition):
        mini = _mini(src, tid)
        pr = SequencePrinter().project(mini, tid, granularity, overflow)
        for k in range(len(pr['windows'])):
            inputs.append({'format': INPUT_FORMAT, 'profile': PROFILE, 'partition': partition, 'trigger_id': tid,
                           'use_case': pr['trigger'].get('use_case'), 'window': k+1, 'windows': len(pr['windows']),
                           'granularity': granularity, 'overflow': overflow, 'source': mini})
    need(len(inputs) <= MAX_PANELS, 'VP08_SEQUENCE_BUDGET', f'{len(inputs)} panels exceed {MAX_PANELS}', 'partition')
    return inputs


def _coverage(src, entries):
    total = _all_units(src)
    covered = sorted({u for e in entries for u in e['units']})
    missing = sorted(set(total)-set(covered))
    return {'status': 'COMPLETE' if not missing else 'INCOMPLETE', 'units_total': len(total), 'units_covered': len(covered),
            'uncovered_units': missing, 'is_minimum_proven': False}


def _index_svg(src, partition, granularity, entries, coverage):
    base = Printer()
    trig = {t['id']: t for t in src['triggers']}
    order = list(dict.fromkeys(e['trigger_id'] for e in entries))
    h = 240+len(order)*30+len(entries)*22+60
    root = base._root({'view_id': 'vp08.trigger-index', 'title': excerpt('Triggers · '+src['title'], 72),
                       'subtitle': excerpt(f'VP-08 · cube.sequence · partition {partition} · {granularity} · text-only index, no thumbnails', 105)}, h)
    root.set('data-printer-profile', PROFILE)
    root.set('data-vp08-index', 'display-only')
    text(root, 60, 125, 'TRIGGER INDEX · declared entry points and their panels · not a verdict', 13, MUTED, 'bold')
    y = 156
    for tid in order:
        t = trig[tid]
        es = [e for e in entries if e['trigger_id'] == tid]
        g = add(root, 'g', **{'data-vp08-index-trigger': tid})
        add(g, 'title').text = f"{t['label']} ({t['kind']}) · {t['declaration_ref']}"
        text(g, 62, y, excerpt(f"{t['label']} ({t['kind']})", 40), 13, '#0F172A', 'bold')
        text(g, 400, y, excerpt(t.get('use_case', '–'), 30), 12, '#334155')
        text(g, 640, y, f"{sum(len(e['message_ids']) for e in es)} messages · {len(es)} panel{'s' if len(es) > 1 else ''}", 12, '#334155')
        y += 24
        for e in es:
            pg = add(g, 'g', **{'data-vp08-panel': e['panel']})
            text(pg, 82, y, e['panel'], 11, '#334155', 'bold')
            text(pg, 170, y, f"window {e['window']}/{e['windows']} · messages {e['numbers'][0]}–{e['numbers'][-1]}", 11, '#334155')
            text(pg, 900, y, e['svg_sha256'][:16]+'…', 10, MUTED)
            y += 22
        y += 8
    line(root, 60, y, 1140, y, '#E2E8F0')
    text(root, 68, y+28, f"Coverage {coverage['status']} · {coverage['units_covered']}/{coverage['units_total']} (trigger, message) units", 12, MUTED, 'bold')
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP08_AUDIT', 'index contains active content', 'audit')
    return svg


def print_panels(src, partition='trigger', granularity='standard', overflow='summarize'):
    inputs = build_panels(src, partition, granularity, overflow)
    files, entries, warnings = {}, [], []
    for i, inp in enumerate(inputs):
        name = f'panel-{i+1:02d}'
        rep, svg, units = render_input(inp)
        raw = encode(inp)
        files[name+'.svg'] = svg
        files[name+'.input.json'] = raw
        win = rep['windows'][inp['window']-1]
        if inp['window'] == 1:
            warnings += [dict(w, trigger_id=inp['trigger_id'], panel=name) for w in rep['warnings']]
        entries.append({'panel': name, 'trigger_id': inp['trigger_id'], 'use_case': inp['use_case'], 'window': inp['window'],
                        'windows': inp['windows'], 'message_ids': win['message_ids'],
                        'numbers': [rep['numbering'][m] for m in win['message_ids']], 'units': sorted(units),
                        'svg_sha256': sha_bytes(svg), 'input_sha256': sha_bytes(raw)})
    cov = _coverage(src, entries)
    need(cov['status'] == 'COMPLETE', 'VP08_PANEL_COVERAGE', 'panels do not cover units: '+', '.join(cov['uncovered_units'][:10]), 'coverage')
    files['index.svg'] = _index_svg(src, partition, granularity, entries, cov)
    report = {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'status': 'PASS', 'view': 'cube.sequence',
              'partition': partition, 'granularity': granularity, 'overflow': overflow, 'source_sha256': sha_json(src), 'source': src,
              'panel_count': len(entries), 'trigger_count': len({e['trigger_id'] for e in entries}), 'panel_ledger': entries,
              'coverage': cov, 'warnings': warnings, 'files': {k: sha_bytes(b) for k, b in sorted(files.items())},
              'source_status': 'declared_unverified', **NOT_EVALUATED,
              'notices': ['One panel per trigger window; continued windows repeat the participant header.',
                          'Partition is deterministic (declared order), not a proven minimal partition.',
                          'The index is a drawn table of contents; it embeds no panel.']}
    files['report.json'] = encode(report)
    return report, files


def check_panels(directory):
    """Re-verify a finished panel directory (VP-07 PE-6 rule); any mismatch → VP08_PANEL_COVERAGE."""
    d = Path(directory)
    need(d.is_dir(), 'VP08_PANEL_COVERAGE', 'not a directory: '+str(d), 'coverage')
    rep = load_json(d/'report.json', 'VP08_PANEL_COVERAGE')
    need(isinstance(rep, dict) and rep.get('format') == REPORT_FORMAT, 'VP08_PANEL_COVERAGE', 'report.json is not a VP-08 panel report', 'coverage')
    listed = rep.get('files', {})
    present = sorted(p.name for p in d.iterdir() if p.is_file() and p.name != 'report.json')
    need(present == sorted(listed), 'VP08_PANEL_COVERAGE', 'directory files differ from report file list', 'coverage')
    src = rep['source']
    need(sha_json(src) == rep['source_sha256'], 'VP08_PANEL_COVERAGE', 'embedded source digest mismatch', 'coverage')
    try:
        validate_source(src)
    except VP08Error as e:
        raise VP08Error('VP08_PANEL_COVERAGE', 'embedded source invalid: '+str(e), 'coverage') from e
    entries = rep['panel_ledger']
    need(len(entries) == rep['panel_count'] == len([n for n in listed if n.startswith('panel-') and n.endswith('.svg')]),
         'VP08_PANEL_COVERAGE', 'panel count mismatch', 'coverage')
    for e in entries:
        inp = load_json(d/(e['panel']+'.input.json'), 'VP08_PANEL_COVERAGE')
        try:
            _, svg, units = render_input(inp)
        except VP08Error as x:
            raise VP08Error('VP08_PANEL_COVERAGE', e['panel']+': input does not re-render: '+str(x), 'coverage') from x
        need(inp['source']['triggers'] == [t for t in src['triggers'] if t['id'] == inp['trigger_id']], 'VP08_PANEL_COVERAGE',
             e['panel']+': panel input differs from the embedded source', 'coverage')
        need(svg == (d/(e['panel']+'.svg')).read_bytes() and sha_bytes(svg) == e['svg_sha256'] == listed[e['panel']+'.svg'],
             'VP08_PANEL_COVERAGE', e['panel']+': SVG differs from deterministic re-render of its input', 'coverage')
        need(sorted(units) == e['units'], 'VP08_PANEL_COVERAGE', e['panel']+': ledger units differ from the panel input', 'coverage')
    for name, digest in listed.items():
        need(sha_bytes((d/name).read_bytes()) == digest, 'VP08_PANEL_COVERAGE', 'file digest mismatch: '+name, 'coverage')
    cov = _coverage(src, entries)
    need(cov['status'] == 'COMPLETE' and cov == rep['coverage'], 'VP08_PANEL_COVERAGE',
         'union of panels does not reproduce the recorded complete coverage', 'coverage')
    return {'format': CHECK_FORMAT, 'profile': PROFILE, 'status': 'PASS', 'panels': len(entries), 'coverage': cov,
            'source_sha256': rep['source_sha256'], **NOT_EVALUATED}
