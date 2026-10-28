"""VP-07 panel export (PE-1…PE-6): partition a migration source into budget-valid panels.

Deterministic: declared order first, then ID. Every (cell, step) unit of the source is shown
in at least one panel; repetitions are listed. The index is a drawn table of contents.
"""
from __future__ import annotations
import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import (PROFILE, P071, P072, P073, P074, P075, V73UP, V74UP, METHOD_SETS, tag_profile, NONE_GROUP, METHOD_CATALOG, method_short, method_sorted, V71UP, UNASSIGNED, LEVELS, LENSES, NOT_EVALUATED, Printer, add, line, rect, text, excerpt, source_digest, sha_bytes,
                     sha_json, encode, load_json, fs_isdir, fs_names, fs_bytes, fs_json, VP07Error, need, publish_dir, no_active_content, MUTED, NS)
from .phases import PhasesPrinter, BUDGET, lanes_for, step_label
from .locale import load as load_locale, hide_flow_ledger
from .source import validate_source, as_plan, layer_key
from .styles import apply_styles
from vpprint.core import make_job, render_job, PrintError as VP06PrintError
from vpgranularity import CAPS

PARTITIONS = ('subject', 'object', 'step', 'track', 'layer', 'method')
SELECTIONS = (METHOD_SETS,)  # VP-07.5 (e): a selection mode, not a partition (a bar may be in several sets)
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
    if partition == 'layer':  # VP-07.2: declared layer of the row
        lay = getattr(tracks, 'layers', None)
        need(lay is not None, 'VP07_PANEL_PARTITION', 'partition layer needs a '+P072+' source with a declared layer map', 'partition')
        return lay[cell['row']]
    if partition == 'method':  # VP-07.4 PM-1: the bar's own declared method; bars without one form the group `none`
        need(getattr(tracks, 'methods', False), 'VP07_PANEL_PARTITION', 'partition method needs a '+P073+' or later source', 'partition')
        return cell['method']['method_id'] if 'method' in cell else NONE_GROUP
    return None


def _method_rank(keys):
    """PM-2: catalog order, local methods in first appearance, `none` last (no rank, MP-5)."""
    return method_sorted([k for k in keys if k != NONE_GROUP])+([NONE_GROUP] if NONE_GROUP in keys else [])


def _kv(partition, x):
    """PM-5: subtitles read the short name of a method group; ledger and index keep the full ID."""
    return method_short(x) if partition == 'method' and x != NONE_GROUP else str(x)


def _groups(cells, partition, tracks):
    order, groups = [], {}
    for c in cells:
        k = _key_of(partition, c, tracks)
        if k not in groups:
            order.append(k); groups[k] = []
        groups[k].append(c)
    if partition == 'method':
        order = _method_rank(order)
    return [(k, groups[k]) for k in order]


def _pack_key(cells, partition, tracks, fits, label):
    """PE-2 packing by one key; VP-07.2: `layer` never merges layers and splits a large layer by subject."""
    if partition not in ('layer', 'method'):
        return _pack(_groups(cells, partition, tracks), fits, label)
    out = []  # VP-07.4 PM-3: `method` like `layer` — groups never merged, a large group split by subject
    for lay, cs in _groups(cells, partition, tracks):
        for _, pcs in _pack(_groups(cs, 'subject', tracks), fits, f'{label} {lay!r} / subject'):
            out.append(([lay], pcs))
    return out


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


def _flow_bundle(src, cells, title, subtitle, layers=None):
    rows = {r['id']: r for r in src['rows']}
    objs = {o['id']: o for o in src['objects']}
    order = []
    for c in cells:
        if c['row'] not in order:
            order.append(c['row'])
    for c in cells:
        if c['object'] not in order:
            order.append(c['object'])
    if layers:  # VP-07.2 LS-4: node order follows the declared layer sequence
        order.sort(key=lambda i: layer_key(layers, i))
    nodes = []
    for i in order:
        n = rows.get(i) or objs[i]
        nodes.append({k: v for k, v in n.items() if k not in ('track', 'layer')})
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
        svg, pr = p.render(inp['plan'], 'reject', inp.get('locale'), inp.get('hide_ledger', False))
        return p.report(inp['plan'], svg, pr), svg
    if inp.get('locale') is not None or inp.get('hide_ledger'):  # VP-07.5: post-processing of the finished flow panel
        return _flow_display(inp)
    return _render_flow(inp)


def _flow_display(inp):
    """VP-07.5 D-3: own lines in the locale, then the frozen ledger block dropped (b), then exact replacements (a)."""
    L = load_locale(inp.get('locale'))
    inner, base = _render_flow(inp, L)
    svg = hide_flow_ledger(base) if inp.get('hide_ledger') else base
    svg = L.post(svg, 'flow')
    disp = ({'locale': L.record()} if not L.identity else {})|({'ledger_hidden': True} if inp.get('hide_ledger') else {})
    return {'format': 'aiaeao.cube.vp07-display-print-result/1', 'profile': inp['profile'], 'base_svg_sha256': sha_bytes(base),
            'svg_sha256': sha_bytes(svg), **disp, 'inner_result': inner, 'warnings': inner.get('warnings', []), **NOT_EVALUATED}, svg


def _render_flow(inp, L=None):
    result, base = _vp06(render_job, inp['job'])
    if inp.get('edge_styles') is not None:
        styles = {s['predicate_id']: s for s in inp['edge_styles']}
        prof = inp.get('profile', PROFILE)
        svg, ledger = apply_styles(base, styles, profile=prof)
        result, base = {'format': 'aiaeao.cube.vp07-styled-print-result/1', 'profile': prof, 'base_svg_sha256': sha_bytes(base),
                        'svg_sha256': sha_bytes(svg), 'edge_style_ledger': ledger, 'vp06_result': result,
                        'warnings': [{'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': p} for p in ledger['unstyled']], **NOT_EVALUATED}, svg
    if inp.get('layer_caption'):
        svg = _caption(base, inp['layer_caption'], L)
        result = {'format': 'aiaeao.cube.vp07-layered-print-result/1', 'profile': inp['profile'], 'base_svg_sha256': sha_bytes(base),
                  'svg_sha256': sha_bytes(svg), 'layer_caption': inp['layer_caption'], 'inner_result': result,
                  'warnings': result.get('warnings', []), **NOT_EVALUATED}
        if 'methods_line' not in inp and 'edge_methods' not in inp:
            return result, svg
        base = svg
    if 'methods_line' in inp or 'edge_methods' in inp:  # VP-07.4 FL / FE: post-processing, inner result kept (FL-4)
        svg, methods = _methods_post(base, inp, L)
        result = {'format': 'aiaeao.cube.vp07-methods-print-result/1', 'profile': inp['profile'], 'base_svg_sha256': sha_bytes(base),
                  'svg_sha256': sha_bytes(svg), 'methods': methods, 'inner_result': result,
                  'warnings': result.get('warnings', []), **NOT_EVALUATED}
        return result, svg
    return result, base


ML_X0, ML_X1, ML_Y = 60, 820, (147, 162)  # VP-07.4 FL-3 / D-7 (reopened): strip above the layer caption, left of the lens box
ML_CHARS = 118


def _flow_methods(src, cells, step_id):
    """VP-07.4 FL-1/FL-2 and FE-1 from declared fields only: transitions at the panel's step that concern the panel,
    and the edges whose bar declares a method."""
    rows = {c['row'] for c in cells}
    nodes = rows | {c['object'] for c in cells}
    of_rows = {c['object'] for c in src['cells'] if c['row'] in rows}  # FL-1 (ii), D-5 amended: any step of a panel row
    line_ = []
    for j, t in enumerate(src['transitions']):
        if t['at'] == step_id and (set(t['retires']) | set(t['introduces'])) & (nodes | of_rows):
            line_.append({'code': t.get('code', 'T'+str(j+1)), 'id': t['id'],
                          'methods': method_sorted(b['method_id'] for b in t.get('methods', []))})
    edges = {c['declaration_ref']: c['method']['method_id'] for c in cells if 'method' in c}
    return line_, edges


def _flow_method_fields(src, cells, step_id):
    if src['profile'] not in V74UP:  # D-1: only 0.7.4 (and 0.7.5) sources get the line and the edge metadata
        return {}
    line_, edges = _flow_methods(src, cells, step_id)
    out = {}
    if line_:
        out['methods_line'] = {'step': step_id, 'transitions': line_}
    if edges:
        out['edge_methods'] = edges
    return out


def _entry(t):
    return f"{t['code']} {t['id']}"+(' · '+', '.join(method_short(m) for m in t['methods']) if t['methods'] else '')


def _line_texts(ml, L=None):
    """FL-3: whole entries on at most two lines of ML_CHARS, then `+n more`; the full list stays in title and ledger."""
    entries = [_entry(t) for t in ml['transitions']]
    head = L.t('flow.methods', 'TRANSITIONS AT {step} (declared)', step=ml['step']) if L else f"TRANSITIONS AT {ml['step']} (declared)"
    lines, cur, i = [], head, 0
    while i < len(entries):
        cand = cur+' · '+entries[i]
        if len(cand) <= ML_CHARS:
            cur, i = cand, i+1
            continue
        if len(lines) == 1:
            break
        lines.append(cur); cur = '   '+entries[i] if len('   '+entries[i]) <= ML_CHARS else excerpt('   '+entries[i], ML_CHARS); i += 1
    rest = len(entries)-i
    if rest:
        tail = f' · +{rest} more'
        while len(cur)+len(tail) > ML_CHARS and ' · ' in cur.strip():
            cur = cur[:cur.rindex(' · ')]; rest += 1; tail = f' · +{rest} more'
        cur += tail
    lines.append(cur)
    return lines, entries


def _overlaps(root, box):
    """Conservative boxes of drawn text and rects; True if any intersects `box` = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    for e in root.iter():
        tag = e.tag.split('}')[-1]
        try:
            if tag == 'rect' and e.get('width') and e.get('height'):
                ex, ey, ew, eh = (float(e.get(k)) for k in ('x', 'y', 'width', 'height'))
                if ew >= 1200 and eh >= 500:
                    continue                                   # page background
                b = (ex, ey, ex+ew, ey+eh)
            elif tag == 'text' and e.get('x') and e.get('y'):
                size = float(e.get('font-size', 12)); ex, ey = float(e.get('x')), float(e.get('y'))
                w = len(e.text or '')*size*0.62
                ex = ex-w/2 if e.get('text-anchor') == 'middle' else ex-w if e.get('text-anchor') == 'end' else ex
                b = (ex, ey-size, ex+w, ey+size*0.3)
            else:
                continue
        except ValueError:
            continue
        if b[0] < x1 and b[2] > x0 and b[1] < y1 and b[3] > y0:
            return True
    return False


def _methods_post(svg, inp, L=None):
    """FL-1…FL-4, FE-1: add the methods line and edge metadata to a finished flow panel; nothing is moved."""
    root = ET.fromstring(svg)
    edges = inp.get('edge_methods', {})
    for g in root.iter(f'{{{NS}}}g'):
        mid = edges.get(g.get('data-declaration-ref')) if g.get('data-edge-id') else None
        if mid:
            g.set('data-vp07-method', mid)
            t = g.find(f'{{{NS}}}title')
            if t is not None:
                t.text = (t.text or '')+' | method '+method_short(mid)
    methods = {'edges': dict(edges)}
    ml = inp.get('methods_line')
    if ml:
        lines, entries = _line_texts(ml, L)
        need(not _overlaps(root, (ML_X0, ML_Y[0]-12, ML_X1, ML_Y[len(lines)-1]+4)), 'VP07_AUDIT',
             'methods line would overlap the drawn panel (VP-07.4 D-7)', 'audit')
        g = add(root, 'g', **{'data-vp07-methods-line': ' '.join(t['code'] for t in ml['transitions']), 'data-step-id': ml['step']})
        add(g, 'title').text = f"transitions at {ml['step']} (declared): "+' · '.join(entries)
        for y, s in zip(ML_Y, lines):
            text(g, ML_X0, y, s, 11, MUTED, 'bold')
        methods.update(step=ml['step'], transitions=ml['transitions'])
    out = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(out)), 'VP07_AUDIT', 'methods SVG contains active content', 'audit')
    return out, methods


def _caption(svg, layers, L=None):
    """VP-07.2 LD-2: one caption line naming the declared layers of the flow panel, left to right (post-processing)."""
    root = ET.fromstring(svg)
    g = add(root, 'g', **{'data-vp07-layers': ' '.join(layers)})
    head = L.t('flow.layers', 'LAYERS (declared, left to right) · ') if L else 'LAYERS (declared, left to right) · '
    text(g, 60, 178, excerpt(head+' · '.join(layers), 150), 11, MUTED, 'bold')
    out = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(out)), 'VP07_AUDIT', 'layered SVG contains active content', 'audit')
    return out


def _layer_caption(src, cells, layers):
    rows = [c['row'] for c in cells]+[c['object'] for c in cells]
    ids = sorted(set(rows), key=lambda i: layer_key(layers, i))
    return list(dict.fromkeys(layers['of'][i] for i in ids))


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
    need(profile in V71UP, 'VP07_PANEL_PARTITION', 'nested partition needs a '+P071+' or later source', 'partition')
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
    packed = _pack_key(cells, partition, tracks, _phases_fits(idx, granularity, len(steps)),
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


def display_options(src, partition, locale, hide_ledger):
    """VP-07.5 D-1: locale, hidden ledger and method sets only for 0.7.5 sources; `en` is the identity (LC-1)."""
    v75 = isinstance(src, dict) and src.get('profile') == P075
    need(not hide_ledger or v75, 'VP07_PANEL_PARTITION', 'hide_ledger needs a '+P075+' source (VP-07.5 D-1)', 'partition')
    need(partition != METHOD_SETS or v75, 'VP07_PANEL_PARTITION', 'method sets need a '+P075+' source (VP-07.5 D-1)', 'partition')
    need(locale is None or v75, 'VP07_LOCALE_INVALID', 'locale needs a '+P075+' source (VP-07.5 D-1)')
    L = load_locale(locale)
    disp = {}
    if not L.identity:
        disp['locale'] = L.code
    if hide_ledger:
        disp['hide_ledger'] = True
    return L, disp


def _memberships(src):
    """MS-1: a binding names a bar it carries, or a bar whose subject or object is an argument value of a transition binding."""
    tb = [b for t in src['transitions'] for b in t.get('methods', [])]
    mem = {}
    for c in src['cells']:
        ms = [b['method_id'] for b in tb if {c['row'], c['object']} & set(b['arguments'].values())]
        if 'method' in c:
            ms.append(c['method']['method_id'])
        mem[c['id']] = _method_rank(list(dict.fromkeys(ms))) or [NONE_GROUP]  # MS-2 order, `none` only without a binding
    return mem


def _set_order(mem):
    seen = list(dict.fromkeys(m for ms in mem.values() for m in ms))
    return _method_rank(seen)


def _method_set_units(src, mem, m):
    return sorted(f"{c['id']}@{s}" for c in src['cells'] if m in mem[c['id']] for s in c['steps'])


def _method_set_ledger(src, mem, entries):
    """MS-3: per set its panels, member cells and coverage (each set proves its own coverage, D-6)."""
    out = {}
    for m in _set_order(mem):
        total = _method_set_units(src, mem, m)
        es = [e for e in entries if e.get('method_set') == m]
        units = {u for e in es for u in e['units']}
        ok = units == set(total)
        out[m] = {'panels': [e['panel'] for e in es], 'cells': [c['id'] for c in src['cells'] if m in mem[c['id']]],
                  'units_total': len(total), 'units_covered': len(units & set(total)), 'status': 'COMPLETE' if ok else 'INCOMPLETE'}
    return out


def _title(src, L, i, n):
    return excerpt(src['title'], 56)+L.t('panel.suffix', ' · panel {i}/{n}', i=f'{i+1:02d}', n=f'{n:02d}')


def build_panels(src, view, partition, granularity, lens=None, locale=None, hide_ledger=False):
    L, disp = display_options(src, partition, locale, hide_ledger)
    v = validate_source(src)
    if v['layers']:  # VP-07.2 LS-4: cells ordered by the declared layer of their row (stable within a row)
        lay = v['layers']
        v['derived'] = {**v['derived'], 'cells': sorted(v['derived']['cells'], key=lambda c: layer_key(lay, c['row']))}
    need(view in VIEWS, 'VP07_PANEL_PARTITION', 'view must be cube.flow or cube.phases', 'partition')
    if partition == METHOD_SETS:
        need(granularity in LEVELS, 'VP07_PANEL_PARTITION', 'granularity must be overview|standard|detail', 'partition')
        return v, _build_sets(src, v, view, granularity, lens, L, disp)
    nested = parse_partition(partition, view, src['profile'])
    if nested is not None:
        need(granularity in LEVELS, 'VP07_PANEL_PARTITION', 'granularity must be overview|standard|detail', 'partition')
        return v, _build_nested(src, v, view, nested, granularity, lens, L, disp)
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
            packed = _pack_key(d['cells'], partition, v['tracks'], _phases_fits(idx, granularity, len(steps)), partition)
            plan_sets = [(k, cs, steps) for k, cs in packed]
        n = len(plan_sets)
        need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
        for i, (k, cs, w) in enumerate(plan_sets):
            rows = []
            for c in cs:
                if c['row'] not in rows:
                    rows.append(c['row'])
            title = _title(src, L, i, n)
            sub = excerpt(f'{L.partition(partition)}: '+', '.join(_kv(partition, x) for x in k), 95)
            plan = as_plan(src, rows, cs, w, granularity, title, sub, ends=v.get('declared_ends'))
            inputs.append({'format': INPUT_FORMAT, 'profile': src['profile'], 'view': view, 'partition': partition, 'key_values': k, 'plan': plan,
                           **disp})
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
                for k, cs in _pack_key(active, partition, v['tracks'], _flow_fits(granularity), partition):
                    sets.append((s, k, cs))
        n = len(sets)
        need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
        for i, (s, k, cs) in enumerate(sets):
            title = _title(src, L, i, n)
            sub = excerpt(_flow_sub(L, s, L.partition(partition), ', '.join(_kv(partition, x) for x in k)), 95)
            bundle = _flow_bundle(src, cs, title, sub, v['layers'])
            job = _vp06(make_job, bundle, lens, granularity, 'reject')
            inp = {'format': INPUT_FORMAT, 'profile': src['profile'], 'view': view, 'partition': partition, 'key_values': k,
                   'step': s['id'], 'job': job, **disp}
            if v['layers']:
                inp['layer_caption'] = _layer_caption(src, cs, v['layers'])
            if 'edge_styles' in src:
                inp['edge_styles'] = copy.deepcopy(src['edge_styles'])
            inp.update(_flow_method_fields(src, cs, s['id']))
            inputs.append(inp)
    need(inputs, 'VP07_PANEL_PARTITION', 'source yields no panel', 'partition')
    return v, inputs


def _flow_sub(L, s, part, values):
    return L.t('flow.subtitle', 'step {step} · {partition}: {values}', step=step_label(s, L), partition=part, values=values)


def _flow_input(src, v, view, cs, s, title, sub, granularity, lens, base):
    job = _vp06(make_job, _flow_bundle(src, cs, title, sub, v['layers']), lens, granularity, 'reject')
    inp = {**base, 'step': s['id'], 'job': job}
    if v['layers']:
        inp['layer_caption'] = _layer_caption(src, cs, v['layers'])
    if 'edge_styles' in src:
        inp['edge_styles'] = copy.deepcopy(src['edge_styles'])
    inp.update(_flow_method_fields(src, cs, s['id']))
    return inp


def _build_sets(src, v, view, granularity, lens, L, disp):
    """VP-07.5 (e) MS-1…MS-3: per method set its own panels, packed by subject (PM-3); a bar may be in several sets."""
    d = v['derived']
    steps = src['steps']
    mem = _memberships(src)
    order = _set_order(mem)
    tracks = v['tracks']
    sets = []  # (method, subjects, cells, steps-or-step)
    if view == 'cube.phases':
        need(lens in (None, 'neutral'), 'VP07_PHASES_LENS', 'cube.phases supports lens neutral only (PV-7)', 'lens')
        fits = _phases_fits(d['index'], granularity, len(steps))
        for m in order:
            cs = [c for c in d['cells'] if m in mem[c['id']]]
            for k, pcs in _pack(_groups(cs, 'subject', tracks), fits, f'method set {m!r} / subject'):
                sets.append((m, k, pcs, steps))
    else:
        need(lens in LENSES, 'VP07_PANEL_PARTITION', 'cube.flow panels need --lens cube.lens.* (VP-03 rule)', 'lens')
        refs = [c['declaration_ref'] for c in d['cells']]
        need(len(set(refs)) == len(refs), 'VP07_PANEL_PARTITION', 'cube.flow panels need unique cell declaration_refs', 'partition')
        fits = _flow_fits(granularity)
        for m in order:
            cs = [c for c in d['cells'] if m in mem[c['id']]]
            for s in steps:
                active = [c for c in cs if s['id'] in c['steps']]
                if active:
                    for k, pcs in _pack(_groups(active, 'subject', tracks), fits, f'method set {m!r} / step {s["id"]} / subject'):
                        sets.append((m, k, pcs, s))
    n = len(sets)
    need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
    inputs = []
    for i, (m, k, cs, w) in enumerate(sets):
        title = _title(src, L, i, n)
        vals = f"{_kv('method', m)} · {L.partition('subject')}: "+', '.join(map(str, k))
        base = {'format': INPUT_FORMAT, 'profile': src['profile'], 'view': view, 'partition': METHOD_SETS, 'method_set': m,
                'key_values': k, **disp}
        if view == 'cube.phases':
            rows = list(dict.fromkeys(c['row'] for c in cs))
            sub = excerpt(f'{L.partition(METHOD_SETS)}: {vals}', 95)
            inputs.append({**base, 'plan': as_plan(src, rows, cs, w, granularity, title, sub, ends=v.get('declared_ends'))})
        else:
            sub = excerpt(_flow_sub(L, w, L.partition(METHOD_SETS), vals), 95)
            inputs.append(_flow_input(src, v, view, cs, w, title, sub, granularity, lens, base))
    need(inputs, 'VP07_PANEL_PARTITION', 'source yields no panel', 'partition')
    return inputs


def _build_nested(src, v, view, nested, granularity, lens, L=None, disp=None):
    L, disp = L or load_locale(None), disp or {}
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
                    for k, pcs in _pack_key(active, inner, v['tracks'], fits, f'{outer} {ov!r} / {inner}'):
                        sets.append((ov, k, pcs, s))
    n = len(sets)
    need(n <= MAX_PANELS, 'VP07_PANEL_PARTITION', f'{n} panels exceed {MAX_PANELS}', 'partition')
    inputs = []
    for i, (ov, k, cs, w) in enumerate(sets):
        title = _title(src, L, i, n)
        base = {'format': INPUT_FORMAT, 'profile': prof, 'view': view, 'partition': [outer, inner], 'outer_value': ov, 'key_values': k, **disp}
        if view == 'cube.phases':
            rows = list(dict.fromkeys(c['row'] for c in cs))
            sub = excerpt(f'{L.partition(outer)}: {_kv(outer, ov)} · {L.partition(inner)}: '+', '.join(_kv(inner, x) for x in k), 95)
            inputs.append({**base, 'plan': as_plan(src, rows, cs, w, granularity, title, sub, ends=ends)})
        else:
            vals = f'{_kv(outer, ov)} · {L.partition(inner)}: '+', '.join(_kv(inner, x) for x in k)
            sub = excerpt(_flow_sub(L, w, L.partition(outer), vals), 95)
            inputs.append(_flow_input(src, v, view, cs, w, title, sub, granularity, lens, base))
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
    order = list(dict.fromkeys([e['outer_value'] for e in entries if e.get('outer_value') in set(owner.values())]+list(owner.values())))
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


def _index_svg(src, view, partition, granularity, entries, coverage, outer_ledger=None, L=None, sets=None):
    L = L or load_locale(None)
    if sets is not None:  # VP-07.5 MS-3: panels grouped under their method set, like outer groups (NP-5)
        outer_ledger = [{'outer_value': m, **x} for m, x in sets.items()]
        entries = [dict(e, outer_value=e['method_set']) for e in entries]
    base = Printer()
    h = 260+len(entries)*24+60+(len(outer_ledger)*30 if outer_ledger else 0)+sum(12 for e in entries if e.get('layers'))
    if isinstance(partition, list):
        partition = ','.join(partition)
    root = base._root({'view_id': 'vp07.panel-index', 'title': excerpt(L.t('index.title', 'Panels · ')+src['title'], 72),
                       'subtitle': excerpt(L.t('index.subtitle', 'VP-07 · {view} · partition {partition} · {granularity} · text-only index, no thumbnails',
                                               view=view, partition=L.partition(partition) if ',' not in partition else
                                               ','.join(L.partition(x) for x in partition.split(',')), granularity=granularity), 105)}, h)
    root.set('data-printer-profile', src['profile'])
    root.set('data-vp07-index', 'display-only')
    text(root, 60, 129, L.t('index.header', 'PANEL INDEX · coverage of declared (cell, step) units · not a verdict'), 13, MUTED, 'bold')
    y = 160
    groups = [(None, entries)] if not outer_ledger else \
        [(o, [e for e in entries if e['outer_value'] == o['outer_value']]) for o in outer_ledger]
    for o, es in groups:
        if o is not None:  # NP-5: panels grouped under their outer value
            og = add(root, 'g', **{'data-vp07-outer': str(o['outer_value'])})
            text(og, 62, y+6, excerpt(L.t('index.outer', '{value} · {panels} panels · {covered}/{total} units · {status}', value=o['outer_value'],
                                          panels=len(o['panels']), covered=o['units_covered'], total=o['units_total'], status=o['status']),
                                      100), 13, '#0F172A', 'bold')
            y += 30
        for e in es:
            g = add(root, 'g', **{'data-vp07-panel': e['panel']})
            text(g, 68, y, e['panel'], 12, '#0F172A', 'bold')
            text(g, 170, y, excerpt(', '.join(str(x) for x in e['key_values']), 52), 12, '#334155')
            text(g, 600, y, (L.t('index.step', 'step {step} · ', step=e['step']) if e.get('step') else '')
                 + L.t('index.rows_cells', '{rows} rows · {cells} cells', rows=len(e['shown_row_ids']), cells=len(e['shown_cell_ids'])),
                 12, '#334155')
            if e.get('layers'):
                g.set('data-vp07-layers', ' '.join(e['layers']))
                text(g, 170, y+13, excerpt(L.t('index.layers', 'layers: ')+' · '.join(e['layers']), 70), 10, MUTED)
                y += 12
            text(g, 900, y, e['svg_sha256'][:16]+'…', 10, MUTED)
            y += 24
    line(root, 60, y, 1140, y, '#E2E8F0')
    text(root, 68, y+28, L.t('index.coverage', 'Coverage {status} · {covered}/{total} units · {rr} repeated rows · {rc} repeated cells',
                             status=coverage['status'], covered=coverage['units_covered'], total=coverage['units_total'],
                             rr=len(coverage['repeated_row_ids']), rc=len(coverage['repeated_cell_ids'])), 12, MUTED, 'bold')
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP07_AUDIT', 'index contains active content', 'audit')
    return L.post(svg, 'index')


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


def warning_summary(warnings):
    """WS-1: per code in first-appearance order, `items` = the warning objects without `code`."""
    out = {}
    for w in warnings:
        x = out.setdefault(w['code'], {'code': w['code'], 'count': 0, 'items': []})
        x['count'] += 1
        x['items'].append({k: val for k, val in w.items() if k != 'code'})
    return list(out.values())


def print_panels(src, view, partition, granularity, lens=None, locale=None, hide_ledger=False):
    L, disp = display_options(src, partition, locale, hide_ledger)
    v, inputs = build_panels(src, view, partition, granularity, lens, locale, hide_ledger)
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
        if v['layers']:  # VP-07.2 LD-3: declared layers of the rows shown in the panel
            ids = sorted(set(rows), key=lambda i: layer_key(v['layers'], i))
            extra['layers'] = list(dict.fromkeys(v['layers']['of'][i] for i in ids))
        if 'method_set' in inp:
            extra['method_set'] = inp['method_set']
        entries.append({'panel': name, **extra, 'key_values': inp['key_values'], 'step': inp.get('step'), 'shown_row_ids': rows,
                        'shown_cell_ids': cells, 'units': units_of(inp, src), 'svg_sha256': sha_bytes(svg),
                        'input_sha256': sha_bytes(raw), 'panel_report': rep})
    cov = _coverage(src, entries)
    need(cov['status'] == 'COMPLETE', 'VP07_PANEL_COVERAGE', 'panels do not cover units: '+', '.join(cov['uncovered_units'][:10]), 'coverage')
    if v['layers']:  # VP-07.2 LS-3
        warnings += [{'code': 'VP07_LAYER_UNASSIGNED', 'item_id': i} for i, lay in v['layers']['of'].items() if lay == UNASSIGNED]
    if src['profile'] in V73UP:  # VP-07.3 D-7: arguments outside the slice, once per binding role
        owned = [(t['id'], b) for t in src['transitions'] for b in t.get('methods', [])]+[(c['id'], c['method']) for c in src['cells'] if 'method' in c]
        warnings += [{'code': 'VP07_METHOD_ARGUMENT_HIDDEN', 'owner': o, 'method_id': b['method_id'], 'role': r, 'ref': b['arguments'][r],
                      'declaration_ref': b['declaration_ref']} for o, b in owned for r in b.get('hidden_roles', [])]
    v75 = src['profile'] == P075
    if v75:  # VP-07.5 §2: a predicate without a display name in the locale shows its ID
        warnings += [{'code': 'VP07_LOCALE_FALLBACK', 'predicate_id': x, 'locale': L.code}
                     for x in L.missing_predicates(c['predicate_id'] for c in src['cells'])]
    sets = mem = None
    if partition == METHOD_SETS:
        mem = _memberships(src)
        sets = _method_set_ledger(src, mem, entries)
        bad = [m for m, x in sets.items() if x['status'] != 'COMPLETE']
        need(not bad, 'VP07_PANEL_COVERAGE', 'method sets not covered by their own panels: '+', '.join(bad), 'coverage')
    nested = None if partition == METHOD_SETS else parse_partition(partition, view, src['profile'])
    outer = None
    if nested is not None:
        outer = _outer_ledger(src, nested[0], granularity, v['tracks'], entries)
        bad = [o['outer_value'] for o in outer if o['status'] != 'COMPLETE']
        need(not bad, 'VP07_PANEL_COVERAGE', 'outer groups not covered by their own panels: '+', '.join(map(str, bad)), 'coverage')
    files['index.svg'] = _index_svg(src, view, nested or partition, granularity, entries, cov, outer, L, sets)
    conflicts = PhasesPrinter.conflicts(v['derived'])
    prof = src['profile']
    report = {'format': REPORT_FORMAT, 'profile': prof, 'reference_version': 'v9.4', 'status': 'PASS',
              'migration_view_profile': prof, 'view': view, 'partition': nested or partition, 'granularity': granularity, 'lens': lens,
              'source_sha256': sha_json(src), 'source': src, 'panel_count': len(entries), 'panel_ledger': entries,
              'coverage': cov, 'declared_conflicts': conflicts, 'warnings': warnings,
              **({'outer_ledger': outer, 'declared_gaps': PhasesPrinter.gaps(v['derived'])} if nested is not None else
                 {'declared_gaps': PhasesPrinter.gaps(v['derived'])} if prof in V71UP else {}),
              **({'layer_order': v['layers']['order']} if v['layers'] else {}),
              **({'locale': L.record()} if not L.identity else {}), **({'ledger_hidden': True} if hide_ledger else {}),
              **({'method_sets': sets, 'memberships': mem} if sets is not None else {}),
              **({'warning_summary': warning_summary(warnings)} if v75 else {}),
              'files': {k: sha_bytes(b) for k, b in sorted(files.items())},
              'source_status': 'declared_unverified', **NOT_EVALUATED,
              'notices': ['Panels repeat rows for context; every repetition is listed.',
                          'Partition is deterministic (declared order), not a proven minimal partition.',
                          'The index is a drawn table of contents; it embeds no panel.']}
    files['report.json'] = encode(report)
    return report, files


def check_panels(directory):
    """Directory form (CLI); reads files and applies the same checks as check_files (G6 MA-2)."""
    return _check(Path(directory))


def check_files(files):
    """In-memory form (G6 MA-2): `files` maps the names print-panels writes to their bytes."""
    need(isinstance(files, dict), 'VP07_PANEL_COVERAGE', 'files must be a mapping of names to bytes', 'coverage')
    return _check(dict(files))


def _check(d):
    """PE-6: re-verify a finished panel directory; any mismatch → VP07_PANEL_COVERAGE."""
    need(fs_isdir(d), 'VP07_PANEL_COVERAGE', 'not a directory: '+str(d), 'coverage')
    rep = fs_json(d, 'report.json', 'VP07_PANEL_COVERAGE')
    need(isinstance(rep, dict) and rep.get('format') == REPORT_FORMAT, 'VP07_PANEL_COVERAGE', 'report.json is not a VP-07 panel report', 'coverage')
    listed = rep.get('files', {})
    present = [n for n in fs_names(d) if n != 'report.json']
    need(present == sorted(listed), 'VP07_PANEL_COVERAGE', 'directory files differ from report file list', 'coverage')
    for name, digest in listed.items():
        need(sha_bytes(fs_bytes(d, name, 'VP07_PANEL_COVERAGE')) == digest, 'VP07_PANEL_COVERAGE', 'file digest mismatch: '+name, 'coverage')
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
        inp = fs_json(d, e['panel']+'.input.json', 'VP07_PANEL_COVERAGE')
        _, svg = render_input(inp)
        need(svg == fs_bytes(d, e['panel']+'.svg', 'VP07_PANEL_COVERAGE') and sha_bytes(svg) == e['svg_sha256'], 'VP07_PANEL_COVERAGE',
             e['panel']+': SVG differs from deterministic re-render of its input', 'coverage')
        units = units_of(inp, src)
        need(units == e['units'], 'VP07_PANEL_COVERAGE', e['panel']+': ledger units differ from the panel input', 'coverage')
        if inp['view'] == 'cube.flow' and src['profile'] in V74UP:  # VP-07.4: line and edge metadata follow from the source
            byref = {c['declaration_ref']: c for c in src['cells']}
            cs = [byref[x['declaration_ref']] for x in inp['job']['source_bundle']['view_plan']['edges']]
            want = _flow_method_fields(src, cs, inp['step'])
            need({k: inp[k] for k in ('methods_line', 'edge_methods') if k in inp} == want, 'VP07_PANEL_COVERAGE',
                 e['panel']+': methods line or edge methods differ from the embedded source (VP-07.4)', 'coverage')
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
            inp = fs_json(d, e['panel']+'.input.json', 'VP07_PANEL_COVERAGE')
            need(inp.get('outer_value') == e.get('outer_value'), 'VP07_PANEL_COVERAGE', e['panel']+': outer value differs from its input', 'coverage')
            recomputed.append({'panel': e['panel'], 'outer_value': inp.get('outer_value'), 'units': units_of(inp, src)})
        ol = _outer_ledger(src, outer, rep['granularity'], vs['tracks'], recomputed)
        need(ol == rep.get('outer_ledger') and all(o['status'] == 'COMPLETE' for o in ol), 'VP07_PANEL_COVERAGE',
             'outer ledger differs from the panels or is incomplete (NP-4)', 'coverage')
        extra = {'outer_ledger': ol}
    if rep.get('partition') == METHOD_SETS:  # MS-3: memberships and set ledger recomputed from the source and the panel inputs
        mem = _memberships(src)
        recomputed = []
        for e in entries:
            inp = fs_json(d, e['panel']+'.input.json', 'VP07_PANEL_COVERAGE')
            need(inp.get('method_set') == e.get('method_set'), 'VP07_PANEL_COVERAGE', e['panel']+': method set differs from its input', 'coverage')
            need(all(inp['method_set'] in mem[c] for c in e['shown_cell_ids']), 'VP07_PANEL_COVERAGE',
                 e['panel']+': a shown bar is not named by its method set (MS-1)', 'coverage')
            recomputed.append({'panel': e['panel'], 'method_set': inp.get('method_set'), 'units': units_of(inp, src)})
        ms = _method_set_ledger(src, mem, recomputed)
        need(mem == rep.get('memberships') and ms == rep.get('method_sets') and all(x['status'] == 'COMPLETE' for x in ms.values()),
             'VP07_PANEL_COVERAGE', 'method sets or memberships differ from the panels or are incomplete (MS-3)', 'coverage')
        extra = {'method_sets': ms}
    return {'format': CHECK_FORMAT, 'profile': rep.get('profile', PROFILE), **extra, 'status': 'PASS', 'panels': len(entries), 'coverage': cov,
            'source_sha256': rep['source_sha256'], **NOT_EVALUATED}


print_panels = tag_profile(print_panels, lambda src, *a, **k: src.get('profile') if isinstance(src, dict) else None)
build_panels = tag_profile(build_panels, lambda src, *a, **k: src.get('profile') if isinstance(src, dict) else None)
