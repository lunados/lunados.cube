"""VP-07 panel export (PE-1…PE-6): partition a migration source into budget-valid panels.

Deterministic: declared order first, then ID. Every (cell, step) unit of the source is shown
in at least one panel; repetitions are listed. The index is a drawn table of contents.
"""
from __future__ import annotations
import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import (PROFILE, P071, LEVELS, LENSES, NOT_EVALUATED, Printer, add, line, rect, text, excerpt, source_digest, sha_bytes,
                     sha_json, encode, load_json, VP07Error, need, publish_dir, no_active_content, MUTED)
from .phases import PhasesPrinter, BUDGET, lanes_for
from .source import validate_source, as_plan
from .styles import apply_styles
from vpprint.core import make_job, render_job, PrintError as VP06PrintError
from vpgranularity import CAPS

PARTITIONS = ('subject', 'object', 'step', 'track')
VIEWS = ('cube.flow', 'cube.phases')
REPORT_FORMAT = 'aiaeao.cube.vp07-panel-report/1'
INPUT_FORMAT = 'aiaeao.cube.vp07-panel-input/1'
CHECK_FORMAT = 'aiaeao.cube.vp07-panel-check/1'
MAX_PANELS = 99


def _key_of(partition, cell, tracks):
    if partition == 'subject':
        return cell['row']
    if partition == 'object':
        return cell['object']
    if partition == 'track':
        need(cell['row'] in tracks, 'VP07_PANEL_PARTITION', 'partition track: row '+repr(cell['row'])+' has no declared track', 'partition')
        return tracks[cell['row']]
    return None


def _groups(cells, partition, tracks):
    order, groups = [], {}
    for c in cells:
        k = _key_of(partition, c, tracks)
        if k not in groups:
            order.append(k); groups[k] = []
        groups[k].append(c)
    return [(k, groups[k]) for k in order]


def _pack(groups, fits, label):
    panels, cur, keys_ = [], [], []
    for k, cs in groups:
        if cur and fits(cur+cs):
            cur = cur+cs; keys_.append(k); continue
        if cur:
            panels.append((keys_, cur))
        need(fits(cs), 'VP07_PANEL_PARTITION', f'{label} {k!r} alone exceeds the panel budget; choose another partition or granularity', 'partition')
        cur, keys_ = list(cs), [k]
    if cur:
        panels.append((keys_, cur))
    return panels


def _phases_fits(src_index, granularity, nsteps):
    rcap, scap, ccap, lcap = BUDGET[granularity]

    def fits(cells):
        rows = []
        for c in cells:
            if c['row'] not in rows:
                rows.append(c['row'])
        if nsteps > scap or len(rows) > rcap or len(cells) > ccap:
            return False
        return all(lanes_for([c for c in cells if c['row'] == r], src_index)[1] <= lcap for r in rows)
    return fits


def _flow_fits(granularity):
    ncap, ecap = CAPS[granularity]['cube.flow']

    def fits(cells):
        nodes = []
        for c in cells:
            for x in (c['row'], c['object']):
                if x not in nodes:
                    nodes.append(x)
        return len(nodes) <= ncap and len(cells) <= ecap
    return fits


def _vp06(fn, *a, **k):
    try:
        return fn(*a, **k)
    except VP06PrintError as e:
        raise VP07Error(e.code, str(e), e.stage) from e


def _flow_bundle(src, cells, title, subtitle):
    rows = {r['id']: r for r in src['rows']}
    objs = {o['id']: o for o in src['objects']}
    order = []
    for c in cells:
        if c['row'] not in order:
            order.append(c['row'])
    for c in cells:
        if c['object'] not in order:
            order.append(c['object'])
    nodes = []
    for i in order:
        n = rows.get(i) or objs[i]
        nodes.append({k: v for k, v in n.items() if k != 'track'})
    edges = [{'from': c['row'], 'to': c['object'], 'predicate_id': c['predicate_id'], 'declaration_ref': c['declaration_ref'],
              'arrow_anchor_id': 'relation-arrows.reference'} for c in cells]
    target = {}
    for i in order:
        target[('row', i)] = ('node', i)
        target[('object', i)] = ('node', i)
    for j, c in enumerate(cells):
        target[('cell', c['id'])] = ('edge', 'e'+str(j+1))
    binds, seen = [], set()
    for b in src['facet_bindings']:
        t = target.get((b['target_kind'], b['target_id']))
        if t is None or (b['lens'],)+t in seen:
            continue
        seen.add((b['lens'],)+t)
        binds.append({'lens': b['lens'], 'target_kind': t[0], 'target_id': t[1], 'declaration_ref': b['declaration_ref'],
                      'note': b['note'], 'basis': 'declared_unverified'})
    plan = {'printer_profile': 'P2-VP-VIEWS/0.2.0', 'reference_version': 'v9.4', 'view': 'cube.flow', 'lens': 'neutral',
            'granularity': 'standard', 'title': title, 'subtitle': subtitle, 'nodes': nodes, 'order': order, 'edges': edges,
            'direction': 'left-to-right', 'declaration_status': 'declared_unverified'}
    return {'format': 'aiaeao.cube.vp03-lens-bundle/1', 'lens_profile': 'P2-VP-LENSES/0.3.0', 'reference_version': 'v9.4',
            'source_view_sha256': source_digest(plan), 'view_plan': plan, 'facet_bindings': binds, 'basis': 'declared_unverified'}


def render_input(inp):
    """Render one panel input wrapper; used by print-panels and check-panels alike."""
    need(isinstance(inp, dict) and inp.get('format') == INPUT_FORMAT, 'VP07_PANEL_COVERAGE', 'not a VP-07 panel input')
    if inp['view'] == 'cube.phases':
        p = PhasesPrinter()
        svg, pr = p.render(inp['plan'], 'reject')
        return p.report(inp['plan'], svg, pr), svg
    result, base = _vp06(render_job, inp['job'])
    if inp.get('edge_styles') is None:
        return result, base
    styles = {s['predicate_id']: s for s in inp['edge_styles']}
    prof = inp.get('profile', PROFILE)
    svg, ledger = apply_styles(base, styles, profile=prof)
    return {'format': 'aiaeao.cube.vp07-styled-print-result/1', 'profile': prof, 'base_svg_sha256': sha_bytes(base),
            'svg_sha256': sha_bytes(svg), 'edge_style_ledger': ledger, 'vp06_result': result,
            'warnings': [{'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': p} for p in ledger['unstyled']], **NOT_EVALUATED}, svg


def units_of(inp, src):
    """(cell_id@step) units actually shown by a panel input (authoritative, not the ledger)."""
    if inp['view'] == 'cube.phases':
        return sorted(f"{c['id']}@{s}" for c in inp['plan']['cells'] for s in c['steps'])
    by_ref = {c['declaration_ref']: c['id'] for c in src['cells']}
    return sorted(f"{by_ref[e['declaration_ref']]}@{inp['step']}" for e in inp['job']['source_bundle']['view_plan']['edges'])


def _all_units(src):
    return sorted(f"{c['id']}@{s}" for c in src['cells'] for s in c['steps'])


def parse_partition(partition, view, profile):
    """NP-1: one key (0.7.0) or `outer,inner` (0.7.1 only, distinct keys, step outer only for cube.phases)."""
    need(isinstance(partition, str), 'VP07_PANEL_PARTITION', 'partition must be a string', 'partition')
    if ',' not in partition:
        return None
    ks = partition.split(',')
    need(profile == P071, 'VP07_PANEL_PARTITION', 'nested partition needs a '+P071+' source', 'partition')
    need(len(ks) == 2, 'VP07_PANEL_PARTITION', 'nested partition takes exactly two keys (D-2), got '+repr(partition), 'partition')
    need(all(k in PARTITIONS for k in ks), 'VP07_PANEL_PARTITION', 'partition keys must be subject|object|step|track, got '+repr(partition), 'partition')
    need(ks[0] != ks[1], 'VP07_PANEL_PARTITION', 'nested partition repeats key '+repr(ks[0]), 'partition')
    need(not (view == 'cube.flow' and ks[0] == 'step'), 'VP07_PANEL_PARTITION', 'cube.flow panels are per step already; step cannot be the outer key (D-3)', 'partition')
    return ks


def _phase_sets(src, d, cells, partition, steps, granularity, tracks, label=None):
    """0.7.0 single-key packing for cube.phases (PE-2), applied to `cells` over `steps`."""
    idx = d['index']
    if partition == 'step':
        scap = BUDGET[granularity][1]
        windows = [steps[i:i+scap] for i in range(0, len(steps), scap)]
        plan_sets = []
        for w in windows:
            ids = {s['id'] for s in w}
            cs = []
            for c in cells:
                st = [s for s in c['steps'] if s in ids]
                if st:
                    cs.append({**c, 'steps': st})
            if cs:
                need(_phases_fits(idx, granularity, len(w))(cs), 'VP07_PANEL_PARTITION',
                     (label+' / ' if label else '')+f'step window {w[0]["id"]}–{w[-1]["id"]} alone exceeds the panel budget', 'partition')
                plan_sets.append(([w[0]['id']+'–'+w[-1]['id']], cs, w))
        return plan_sets
    packed = _pack(_groups(cells, partition, tracks), _phases_fits(idx, granularity, len(steps)),
                   (label+' / ' if label else '')+partition)
    return [(k, cs, steps) for k, cs in packed]


def _outer_groups(d, outer, steps, granularity, tracks):
    """NP-2: outer groups in declared order; `step` (cube.phases only) groups by budget-sized step windows."""
    if outer != 'step':
        return [(k, cs, steps) for k, cs in _groups(d['cells'], outer, tracks)]
    scap = BUDGET[granularity][1]
    out = []
    for i in range(0, len(steps), scap):
        w = steps[i:i+scap]
        ids = {s['id'] for s in w}
        cs = [{**c, 'steps': [s for s in c['steps'] if s in ids]} for c in d['cells'] if set(c['steps']) & ids]
        if cs:
            out.append((w[0]['id']+'–'+w[-1]['id'], cs, w))
    return out


def build_panels(src, view, partition, granularity, lens=None):
    v = validate_source(src)
    need(view in VIEWS, 'VP07_PANEL_PARTITION', 'view must be cube.flow or cube.phases', 'partition')
    nested = parse_partition(partition, view, src['profile'])
    if nested is not None:
        need(granularity in LEVELS, 'VP07_PANEL_PARTITION', 'granularity must be overview|standard|detail', 'partition')
        return v, _build_nested(src, v, view, nested, granularity, lens)
    need(partition in PARTITIONS, 'VP07_PANEL_PARTITION', 'partition key must be subject|object|step|track, got '+repr(partition), 'partition')
    need(granularity in LEVELS, 'VP07_PANEL_PARTITION', 'granularity must be overview|standard|detail', 'partition')
    d = v['derived']
    steps = src['steps']
    idx = d['index']
    inputs = []
    if view == 'cube.phases':
        need(lens in (None, 'neutral'), 'VP07_PHASES_LENS', 'cube.phases supports lens neutral only in 0.7.0 (PV-7)', 'lens')
        if partition == 'step':
            scap = BUDGET[granularity][1]
            windows = [steps[i:i+scap] for i in range(0, len(steps), scap)]
            plan_sets = []
            for w in windows:
                ids = {s['id'] for s in w}
                cs = []
                for c in d['cells']:
                    st = [s for s in c['steps'] if s in ids]
                    if st:
                        cs.append({**c, 'steps': st})
                if cs:
                    need(_phases_fits(idx, granularity, len(w))(cs), 'VP07_PANEL_PARTITION',
                         f'step window {w[0]["id"]}–{w[-1]["id"]} alone exceeds the panel budget', 'partition')
                    plan_sets.append(([w[0]['id']+'–'+w[-1]['id']], cs, w))
        else:
            packed = _pack(_groups(d['cells'], partition, v['tracks']), _phases_fits(idx, granularity, len(steps)), partition)
            plan_sets = [(k, cs, steps) for k, cs in packed]
        n = len(plan_sets)
        need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
        for i, (k, cs, w) in enumerate(plan_sets):
            rows = []
            for c in cs:
                if c['row'] not in rows:
                    rows.append(c['row'])
            title = excerpt(src['title'], 56)+f' · panel {i+1:02d}/{n:02d}'
            sub = excerpt(f'{partition}: '+', '.join(str(x) for x in k), 95)
            plan = as_plan(src, rows, cs, w, granularity, title, sub, ends=v.get('declared_ends'))
            inputs.append({'format': INPUT_FORMAT, 'profile': src['profile'], 'view': view, 'partition': partition, 'key_values': k, 'plan': plan})
    else:
        need(lens in LENSES, 'VP07_PANEL_PARTITION', 'cube.flow panels need --lens cube.lens.* (VP-03 rule)', 'lens')
        refs = [c['declaration_ref'] for c in d['cells']]
        need(len(set(refs)) == len(refs), 'VP07_PANEL_PARTITION', 'cube.flow panels need unique cell declaration_refs', 'partition')
        sets = []
        for s in steps:
            active = [c for c in d['cells'] if s['id'] in c['steps']]
            if not active:
                continue
            if partition == 'step':
                need(_flow_fits(granularity)(active), 'VP07_PANEL_PARTITION', f'step {s["id"]} alone exceeds the flow budget', 'partition')
                sets.append((s, [s['id']], active))
            else:
                for k, cs in _pack(_groups(active, partition, v['tracks']), _flow_fits(granularity), partition):
                    sets.append((s, k, cs))
        n = len(sets)
        need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
        for i, (s, k, cs) in enumerate(sets):
            title = excerpt(src['title'], 56)+f' · panel {i+1:02d}/{n:02d}'
            sub = excerpt(f"step {s['label']} · {partition}: "+', '.join(str(x) for x in k), 95)
            bundle = _flow_bundle(src, cs, title, sub)
            job = _vp06(make_job, bundle, lens, granularity, 'reject')
            inp = {'format': INPUT_FORMAT, 'profile': src['profile'], 'view': view, 'partition': partition, 'key_values': k,
                   'step': s['id'], 'job': job}
            if 'edge_styles' in src:
                inp['edge_styles'] = copy.deepcopy(src['edge_styles'])
            inputs.append(inp)
    need(inputs, 'VP07_PANEL_PARTITION', 'source yields no panel', 'partition')
    return v, inputs


def _build_nested(src, v, view, nested, granularity, lens):
    outer, inner = nested
    d = v['derived']
    steps = src['steps']
    prof = src['profile']
    ends = v.get('declared_ends')
    sets = []  # (outer_value, inner key values, cells, steps-or-step)
    if view == 'cube.phases':
        need(lens in (None, 'neutral'), 'VP07_PHASES_LENS', 'cube.phases supports lens neutral only (PV-7)', 'lens')
        for ov, cs, w in _outer_groups(d, outer, steps, granularity, v['tracks']):
            for k, pcs, pw in _phase_sets(src, d, cs, inner, w, granularity, v['tracks'], f'{outer} {ov!r}'):
                sets.append((ov, k, pcs, pw))
    else:
        need(lens in LENSES, 'VP07_PANEL_PARTITION', 'cube.flow panels need --lens cube.lens.* (VP-03 rule)', 'lens')
        refs = [c['declaration_ref'] for c in d['cells']]
        need(len(set(refs)) == len(refs), 'VP07_PANEL_PARTITION', 'cube.flow panels need unique cell declaration_refs', 'partition')
        fits = _flow_fits(granularity)
        for ov, cs in _groups(d['cells'], outer, v['tracks']):
            for s in steps:
                active = [c for c in cs if s['id'] in c['steps']]
                if not active:
                    continue
                if inner == 'step':
                    need(fits(active), 'VP07_PANEL_PARTITION', f'{outer} {ov!r} / step {s["id"]} alone exceeds the flow budget', 'partition')
                    sets.append((ov, [s['id']], active, s))
                else:
                    for k, pcs in _pack(_groups(active, inner, v['tracks']), fits, f'{outer} {ov!r} / {inner}'):
                        sets.append((ov, k, pcs, s))
    n = len(sets)
    need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
    inputs = []
    for i, (ov, k, cs, w) in enumerate(sets):
        title = excerpt(src['title'], 56)+f' · panel {i+1:02d}/{n:02d}'
        base = {'format': INPUT_FORMAT, 'profile': prof, 'view': view, 'partition': [outer, inner], 'outer_value': ov, 'key_values': k}
        if view == 'cube.phases':
            rows = list(dict.fromkeys(c['row'] for c in cs))
            sub = excerpt(f'{outer}: {ov} · {inner}: '+', '.join(str(x) for x in k), 95)
            inputs.append({**base, 'plan': as_plan(src, rows, cs, w, granularity, title, sub, ends=ends)})
        else:
            sub = excerpt(f"step {w['label']} · {outer}: {ov} · {inner}: "+', '.join(str(x) for x in k), 95)
            job = _vp06(make_job, _flow_bundle(src, cs, title, sub), lens, granularity, 'reject')
            inp = {**base, 'step': w['id'], 'job': job}
            if 'edge_styles' in src:
                inp['edge_styles'] = copy.deepcopy(src['edge_styles'])
            inputs.append(inp)
    need(inputs, 'VP07_PANEL_PARTITION', 'source yields no panel', 'partition')
    return inputs


def _outer_of(src, outer, granularity, tracks):
    """Map every source unit (cell@step) to its outer value (NP-3)."""
    out = {}
    if outer == 'step':
        scap = BUDGET[granularity][1]
        steps = src['steps']
        for i in range(0, len(steps), scap):
            w = steps[i:i+scap]
            for s in w:
                for c in src['cells']:
                    if s['id'] in c['steps']:
                        out[f"{c['id']}@{s['id']}"] = w[0]['id']+'–'+w[-1]['id']
        return out
    for c in src['cells']:
        ov = _key_of(outer, c, tracks)
        for s in c['steps']:
            out[f"{c['id']}@{s}"] = ov
    return out


def _outer_ledger(src, outer, granularity, tracks, entries):
    owner = _outer_of(src, outer, granularity, tracks)
    order = list(dict.fromkeys(owner.values()))
    led = []
    for ov in order:
        total = sorted(u for u, o in owner.items() if o == ov)
        panels = [e['panel'] for e in entries if e.get('outer_value') == ov]
        units = {u for e in entries if e.get('outer_value') == ov for u in e['units']}
        covered = sorted(units & set(total))
        ok = covered == total and units <= set(total)
        led.append({'outer_value': ov, 'panels': panels, 'units_total': len(total), 'units_covered': len(covered),
                    'status': 'COMPLETE' if ok else 'INCOMPLETE'})
    return led


def _index_svg(src, view, partition, granularity, entries, coverage, outer_ledger=None):
    base = Printer()
    h = 260+len(entries)*24+60+(len(outer_ledger)*30 if outer_ledger else 0)
    if isinstance(partition, list):
        partition = ','.join(partition)
    root = base._root({'view_id': 'vp07.panel-index', 'title': excerpt('Panels · '+src['title'], 72),
                       'subtitle': excerpt(f'VP-07 · {view} · partition {partition} · {granularity} · text-only index, no thumbnails', 105)}, h)
    root.set('data-printer-profile', src['profile'])
    root.set('data-vp07-index', 'display-only')
    text(root, 60, 129, 'PANEL INDEX · coverage of declared (cell, step) units · not a verdict', 13, MUTED, 'bold')
    y = 160
    groups = [(None, entries)] if not outer_ledger else \
        [(o, [e for e in entries if e['outer_value'] == o['outer_value']]) for o in outer_ledger]
    for o, es in groups:
        if o is not None:  # NP-5: panels grouped under their outer value
            og = add(root, 'g', **{'data-vp07-outer': str(o['outer_value'])})
            text(og, 62, y+6, excerpt(f"{o['outer_value']} · {len(o['panels'])} panels · {o['units_covered']}/{o['units_total']} units · "
                                      f"{o['status']}", 100), 13, '#0F172A', 'bold')
            y += 30
        for e in es:
            g = add(root, 'g', **{'data-vp07-panel': e['panel']})
            text(g, 68, y, e['panel'], 12, '#0F172A', 'bold')
            text(g, 170, y, excerpt(', '.join(str(x) for x in e['key_values']), 52), 12, '#334155')
            text(g, 600, y, (f"step {e['step']} · " if e.get('step') else '')+f"{len(e['shown_row_ids'])} rows · {len(e['shown_cell_ids'])} cells",
                 12, '#334155')
            text(g, 900, y, e['svg_sha256'][:16]+'…', 10, MUTED)
            y += 24
    line(root, 60, y, 1140, y, '#E2E8F0')
    text(root, 68, y+28, f"Coverage {coverage['status']} · {coverage['units_covered']}/{coverage['units_total']} units · "
         f"{len(coverage['repeated_row_ids'])} repeated rows · {len(coverage['repeated_cell_ids'])} repeated cells", 12, MUTED, 'bold')
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP07_AUDIT', 'index contains active content', 'audit')
    return svg


def _coverage(src, entries):
    total = _all_units(src)
    covered = sorted({u for e in entries for u in e['units']})
    missing = sorted(set(total)-set(covered))
    from collections import Counter
    rc = Counter(r for e in entries for r in e['shown_row_ids'])
    cc = Counter(c for e in entries for c in e['shown_cell_ids'])
    return {'status': 'COMPLETE' if not missing else 'INCOMPLETE', 'units_total': len(total), 'units_covered': len(covered),
            'uncovered_units': missing, 'repeated_row_ids': sorted(k for k, n in rc.items() if n > 1),
            'repeated_cell_ids': sorted(k for k, n in cc.items() if n > 1), 'is_minimum_proven': False}


def print_panels(src, view, partition, granularity, lens=None):
    v, inputs = build_panels(src, view, partition, granularity, lens)
    files, entries, warnings = {}, [], []
    for i, inp in enumerate(inputs):
        name = f'panel-{i+1:02d}'
        rep, svg = render_input(inp)
        raw = encode(inp)
        files[name+'.svg'] = svg
        files[name+'.input.json'] = raw
        if inp['view'] == 'cube.phases':
            rows = [r['id'] for r in inp['plan']['rows']]
            cells = [c['id'] for c in inp['plan']['cells']]
        else:
            byref = {c['declaration_ref']: c for c in src['cells']}
            cs = [byref[e['declaration_ref']] for e in inp['job']['source_bundle']['view_plan']['edges']]
            rows = list(dict.fromkeys(c['row'] for c in cs))
            cells = [c['id'] for c in cs]
        warnings += [dict(w, panel=name) for w in rep.get('warnings', [])]
        extra = {'outer_value': inp['outer_value']} if 'outer_value' in inp else {}
        entries.append({'panel': name, **extra, 'key_values': inp['key_values'], 'step': inp.get('step'), 'shown_row_ids': rows,
                        'shown_cell_ids': cells, 'units': units_of(inp, src), 'svg_sha256': sha_bytes(svg),
                        'input_sha256': sha_bytes(raw), 'panel_report': rep})
    cov = _coverage(src, entries)
    need(cov['status'] == 'COMPLETE', 'VP07_PANEL_COVERAGE', 'panels do not cover units: '+', '.join(cov['uncovered_units'][:10]), 'coverage')
    nested = parse_partition(partition, view, src['profile'])
    outer = None
    if nested is not None:
        outer = _outer_ledger(src, nested[0], granularity, v['tracks'], entries)
        bad = [o['outer_value'] for o in outer if o['status'] != 'COMPLETE']
        need(not bad, 'VP07_PANEL_COVERAGE', 'outer groups not covered by their own panels: '+', '.join(map(str, bad)), 'coverage')
    files['index.svg'] = _index_svg(src, view, nested or partition, granularity, entries, cov, outer)
    conflicts = PhasesPrinter.conflicts(v['derived'])
    prof = src['profile']
    report = {'format': REPORT_FORMAT, 'profile': prof, 'reference_version': 'v9.4', 'status': 'PASS',
              'migration_view_profile': prof, 'view': view, 'partition': nested or partition, 'granularity': granularity, 'lens': lens,
              'source_sha256': sha_json(src), 'source': src, 'panel_count': len(entries), 'panel_ledger': entries,
              'coverage': cov, 'declared_conflicts': conflicts, 'warnings': warnings,
              **({'outer_ledger': outer, 'declared_gaps': PhasesPrinter.gaps(v['derived'])} if nested is not None else
                 {'declared_gaps': PhasesPrinter.gaps(v['derived'])} if prof == P071 else {}),
              'files': {k: sha_bytes(b) for k, b in sorted(files.items())},
              'source_status': 'declared_unverified', **NOT_EVALUATED,
              'notices': ['Panels repeat rows for context; every repetition is listed.',
                          'Partition is deterministic (declared order), not a proven minimal partition.',
                          'The index is a drawn table of contents; it embeds no panel.']}
    files['report.json'] = encode(report)
    return report, files


def check_panels(directory):
    """PE-6: re-verify a finished panel directory; any mismatch → VP07_PANEL_COVERAGE."""
    d = Path(directory)
    need(d.is_dir(), 'VP07_PANEL_COVERAGE', 'not a directory: '+str(d), 'coverage')
    rep = load_json(d/'report.json', 'VP07_PANEL_COVERAGE')
    need(isinstance(rep, dict) and rep.get('format') == REPORT_FORMAT, 'VP07_PANEL_COVERAGE', 'report.json is not a VP-07 panel report', 'coverage')
    listed = rep.get('files', {})
    present = sorted(p.name for p in d.iterdir() if p.is_file() and p.name != 'report.json')
    need(present == sorted(listed), 'VP07_PANEL_COVERAGE', 'directory files differ from report file list', 'coverage')
    for name, digest in listed.items():
        need(sha_bytes((d/name).read_bytes()) == digest, 'VP07_PANEL_COVERAGE', 'file digest mismatch: '+name, 'coverage')
    src = rep['source']
    need(sha_json(src) == rep['source_sha256'], 'VP07_PANEL_COVERAGE', 'embedded source digest mismatch', 'coverage')
    try:
        vs = validate_source(src)
    except VP07Error as e:
        raise VP07Error('VP07_PANEL_COVERAGE', 'embedded source invalid: '+str(e), 'coverage') from e
    entries = rep['panel_ledger']
    need(len(entries) == rep['panel_count'] and len(entries) == len([n for n in listed if n.endswith('.svg') and n.startswith('panel-')]),
         'VP07_PANEL_COVERAGE', 'panel count mismatch', 'coverage')
    for e in entries:
        inp = load_json(d/(e['panel']+'.input.json'), 'VP07_PANEL_COVERAGE')
        _, svg = render_input(inp)
        need(svg == (d/(e['panel']+'.svg')).read_bytes() and sha_bytes(svg) == e['svg_sha256'], 'VP07_PANEL_COVERAGE',
             e['panel']+': SVG differs from deterministic re-render of its input', 'coverage')
        units = units_of(inp, src)
        need(units == e['units'], 'VP07_PANEL_COVERAGE', e['panel']+': ledger units differ from the panel input', 'coverage')
        shown = sorted({u.rsplit('@', 1)[0] for u in units})
        need(shown == sorted(e['shown_cell_ids']), 'VP07_PANEL_COVERAGE', e['panel']+': ledger cell IDs differ from the panel input', 'coverage')
    cov = _coverage(src, entries)
    need(cov['status'] == 'COMPLETE' and cov == rep['coverage'], 'VP07_PANEL_COVERAGE',
         'union of panels does not reproduce the recorded complete coverage', 'coverage')
    extra = {}
    if isinstance(rep.get('partition'), list):
        outer = rep['partition'][0]
        recomputed = []
        for e in entries:  # NP-4: the outer value comes from the panel input, not from the ledger
            inp = load_json(d/(e['panel']+'.input.json'), 'VP07_PANEL_COVERAGE')
            need(inp.get('outer_value') == e.get('outer_value'), 'VP07_PANEL_COVERAGE', e['panel']+': outer value differs from its input', 'coverage')
            recomputed.append({'panel': e['panel'], 'outer_value': inp.get('outer_value'), 'units': units_of(inp, src)})
        ol = _outer_ledger(src, outer, rep['granularity'], vs['tracks'], recomputed)
        need(ol == rep.get('outer_ledger') and all(o['status'] == 'COMPLETE' for o in ol), 'VP07_PANEL_COVERAGE',
             'outer ledger differs from the panels or is incomplete (NP-4)', 'coverage')
        extra = {'outer_ledger': ol}
    return {'format': CHECK_FORMAT, 'profile': rep.get('profile', PROFILE), **extra, 'status': 'PASS', 'panels': len(entries), 'coverage': cov,
            'source_sha256': rep['source_sha256'], **NOT_EVALUATED}
