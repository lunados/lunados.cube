"""VP-12 §1.2…§1.12: projection (columns, bands, presence, markers, edges, outside) and deterministic SVG."""
from __future__ import annotations
import math
from xml.etree import ElementTree as ET

from .common import (PROFILE, VIEW, X_FAMILY, FAMILIES, MAX_COLUMNS, MAX_BANDS, BUDGET, STATUS, ORIGIN_STYLE, UNASSIGNED,
                     NS, Printer, add, line, rect, text, excerpt, cjson, fmt, no_active_content, sha_bytes, sha_json,
                     STROKE, INK, MUTED, DASH, NOT_EVALUATED, need, locale_text)
from .source import validate_input

W, M = 1200, 42
NODE_H, NODE_GAP, BAND_HEAD, BAND_PAD = 46, 24, 34, 24
_PRINTER = None


def _printer():
    global _PRINTER
    if _PRINTER is None:
        _PRINTER = Printer()
    return _PRINTER


def status_line(T):
    st, src = STATUS
    return T['status'].format(status=T.get('status.'+st, st), source=src.replace('Morphology', T.get('status.source', 'Morphology')))


def project(doc):
    validate_input(doc)
    src = doc['source']
    T = locale_text(doc['locale'])
    items = {}
    for it in src['rows']+src['objects']:
        items.setdefault(it['id'], it)
    fam = {i: it['anchor_id'].split('.', 1)[0] for i, it in items.items()}
    isx = {i: fam[i] == X_FAMILY for i in items}
    yz = [i for i in items if not isx[i]]
    layered = 'layer_order' in src
    warnings = []
    if layered:                                                     # §1.3/§1.4 declared layer map (VP-07.2)
        declared = [l for l in src['layer_order'] if l != UNASSIGNED]
        col_of = {i: items[i].get('layer', UNASSIGNED) for i in yz}
        order = [i for i in src['layer_sequence'] if i in col_of]
        loose = [i for i in order if col_of[i] == UNASSIGNED]
        columns = declared+([UNASSIGNED] if loose else [])
        if loose:
            warnings.append({'code': 'VP12_LAYER_PARTIAL', 'nodes': loose})
        labels = {c: (T['unassigned'] if c == UNASSIGNED else c) for c in columns}
    else:                                                           # default: anchor families, first appearance in plan order
        col_of = {i: fam[i] for i in yz}
        bad = sorted({f for f in col_of.values() if f not in FAMILIES})
        need(not bad, 'VP12_INPUT', 'anchor family without a default column: '+', '.join(bad))
        order = list(dict.fromkeys(e for c in src['cells'] for e in (c['row'], c['object']) if e in col_of))
        columns = [f for f in FAMILIES if f in col_of.values()]
        labels = {c: T.get('family.'+c, c) for c in columns}
    need(len(columns) <= MAX_COLUMNS, 'VP12_BUDGET_EXCEEDED', f'{len(columns)} columns exceed {MAX_COLUMNS} (D-6); narrow the layer map', 'budget')
    pids = [s['id'] for s in src['steps']]
    steps = sorted(doc['steps'], key=pids.index)                   # §1.5 declared order whatever the given order
    need(len(steps) <= MAX_BANDS, 'VP12_BUDGET_EXCEEDED', f'{len(steps)} bands exceed {MAX_BANDS} (D-3)', 'budget')
    origin = {e['cell_id']: e for e in src['origin_ledger']}
    placing = set(doc['placement_predicates'])
    cap = BUDGET[doc['granularity']]
    bands, outside = [], {}
    for s in steps:
        hold = [c for c in src['cells'] if s in c['steps']]
        present = {e for c in hold for e in (c['row'], c['object']) if e in col_of}
        cols = {k: [i for i in order if i in present and col_of[i] == k] for k in columns}
        for k, ns in cols.items():
            need(len(ns) <= cap, 'VP12_BUDGET_EXCEEDED', f'band {s}, column {k}: {len(ns)} nodes exceed {cap} ({doc["granularity"]})', 'budget')
        edges = []
        for c in hold:
            if isx[c['row']] or isx[c['object']]:
                outside.setdefault(c['id'], []).append(s)
                continue
            o = origin[c['id']]
            edges.append({'cell': c['id'], 'subject': c['row'], 'object': c['object'], 'predicate': c['predicate_id'],
                          'origin': o['origin'], 'style': ORIGIN_STYLE[o['origin']], 'source_ids': list(o['source_ids']),
                          'placement': c['predicate_id'] in placing, 'declaration_ref': c['declaration_ref']})
        bands.append({'step': s, 'columns': cols, 'present': present, 'edges': edges, 'markers': []})
    trans = src['transitions']
    for k, b in enumerate(bands):                                  # §1.7 markers between consecutive shown bands
        seq = [i for col in columns for i in b['columns'][col]]
        for i in seq:
            if k > 0 and i not in bands[k-1]['present']:
                lo, hi = pids.index(bands[k-1]['step']), pids.index(b['step'])
                by = [t['code'] for t in trans if lo < pids.index(t['at']) <= hi and i in t['introduces']]
                b['markers'].append({'node': i, 'marker': 'introduced', 'declared_by': by})
            if k < len(bands)-1 and i not in bands[k+1]['present']:
                lo, hi = pids.index(b['step']), pids.index(bands[k+1]['step'])
                by = [t['code'] for t in trans if lo < pids.index(t['at']) <= hi and i in t['retires']]
                b['markers'].append({'node': i, 'marker': 'retired', 'retired_at': bands[k+1]['step'], 'declared_by': by})
    return {'doc': doc, 'src': src, 'T': T, 'items': items, 'columns': columns, 'labels': labels, 'col_of': col_of,
            'bands': bands, 'x_outside': [{'cell': c, 'steps': st} for c, st in outside.items()],
            'warnings': warnings, 'status': status_line(T), 'layered': layered}


def ledger(pr):
    bands = [{'step': b['step'], 'columns': b['columns'], 'edges': b['edges'], 'markers': b['markers']} for b in pr['bands']]
    units = [f"{b['step']}|node|{i}" for b in pr['bands'] for col in pr['columns'] for i in b['columns'][col]]
    units += [f"{b['step']}|edge|{e['cell']}" for b in pr['bands'] for e in b['edges']]
    return {'view': VIEW, 'columns': pr['columns'], 'column_labels': pr['labels'], 'bands': bands, 'units': units,
            'x_outside': pr['x_outside'], 'crossing_status': {'status': STATUS[0], 'source': STATUS[1], 'text': pr['status']},
            'layer_map': pr['layered']}


# -- drawing ------------------------------------------------------------------------------------------------------------

def _arrow(g, x1, y1, x2, y2, color):
    a = math.atan2(y2-y1, x2-x1)
    pts = [(x2, y2), (x2-9*math.cos(a-0.4), y2-9*math.sin(a-0.4)), (x2-9*math.cos(a+0.4), y2-9*math.sin(a+0.4))]
    add(g, 'polygon', points=' '.join(f'{fmt(x)},{fmt(y)}' for x, y in pts), fill=color)


def render(pr):
    T, P = pr['T'], _printer()
    cols = pr['columns']
    cw = (W-2*M)/max(len(cols), 1)
    nw = max(min(cw-90, 230), 120)
    heights = [BAND_HEAD+BAND_PAD+max(1, max((len(b['columns'][c]) for c in cols), default=0))*(NODE_H+NODE_GAP) for b in pr['bands']]
    top = 190
    height = top+sum(heights)+16*len(heights)+110
    doc = pr['doc']
    title = excerpt(f"{doc['source']['plan_id']} · landscape · {' / '.join(b['step'] for b in pr['bands'])}", 78)
    root = P._root({'title': title, 'subtitle': excerpt(pr['status']+' · '+PROFILE, 110), 'view_id': VIEW}, height)
    root.set('data-printer-profile', PROFILE)
    root.set('data-vp12-crossing-status', STATUS[0])
    text(root, M, 120, T['header'], 12, MUTED)
    leg = [('solid', T['legend.solid']), ('dashed', T['legend.dashed']), ('dotted', T['legend.dotted'])]
    x = M
    for style, label in leg:
        el = line(root, x, 144, x+28, 144, color=STROKE)
        if style in DASH:
            el.set('stroke-dasharray', DASH[style])
        text(root, x+34, 148, label, 11, MUTED)
        x += 46+7*len(label)
    el = line(root, x, 144, x+28, 144, color=STROKE); el.set('stroke-width', '3.2')
    text(root, x+34, 148, T['legend.placement'], 11, MUTED)
    for k, c in enumerate(cols):
        text(root, M+k*cw+cw/2, 182, excerpt(pr['labels'][c], 30), 13, INK, 'bold', anchor='middle')
    y0 = top
    for b, h in zip(pr['bands'], heights):
        g = add(root, 'g', **{'data-vp12-band': b['step']})
        rect(g, M, y0, W-2*M, h, stroke='#E2E8F0', fill='#FFFFFF', radius=6)
        text(g, M+12, y0+22, T['step'].format(step=b['step']), 13, INK, 'bold')
        mk = {(m['node'], m['marker']): m for m in b['markers']}
        pos = {}
        for k, c in enumerate(cols):
            ns = b['columns'][c]
            if not ns:
                text(g, M+k*cw+cw/2, y0+BAND_HEAD+BAND_PAD+NODE_H/2, T['empty'], 11, '#94A3B8', anchor='middle')
            for r, i in enumerate(ns):
                it = pr['items'][i]
                nx, ny = M+k*cw+(cw-nw)/2, y0+BAND_HEAD+BAND_PAD/2+NODE_GAP/2+r*(NODE_H+NODE_GAP)
                pos[i] = (k, nx, ny)
                retired = (i, 'retired') in mk
                ng = add(g, 'g', **{'data-vp12-node': i, 'data-anchor-id': it['anchor_id'], 'data-semantic-ref': it['semantic_ref'],
                                    'data-vp12-column': c})
                tt = add(ng, 'title'); tt.text = it['label']+' — '+it['anchor_id']
                rr = rect(ng, nx, ny, nw, NODE_H, stroke=STROKE, fill='#F8FAFC' if not retired else '#FFFFFF', radius=8, dashed=retired)
                text(ng, nx+20, ny+30, P.by_id[it['anchor_id']]['unicode'], 20, INK, anchor='middle', glyph=True)
                text(ng, nx+40, ny+20, excerpt(it['label'], int((nw-50)/8)), 13, INK, 'bold')
                sub = it['anchor_id'].split('.', 1)[1]
                if (i, 'introduced') in mk:
                    ng.set('data-vp12-marker', 'introduced'); sub = '+ '+T['introduced']
                if retired:
                    ng.set('data-vp12-marker', 'retired'); sub = '− '+T['retired'].format(step=mk[(i, 'retired')]['retired_at'])
                    rr.set('stroke-dasharray', DASH['dashed'])
                text(ng, nx+40, ny+37, excerpt(sub, int((nw-50)/6.5)), 10, MUTED)
        same, lanes = {}, {}
        for e in b['edges']:
            (ka, xa, ya), (kb, xb, yb) = pos[e['subject']], pos[e['object']]
            eg = add(g, 'g', **{'data-edge-id': e['cell'], 'data-declaration-ref': e['declaration_ref'], 'data-vp12-origin': e['origin'],
                                'data-vp12-edge-style': e['style'], 'data-vp12-placement': 'true' if e['placement'] else 'false'})
            tt = add(eg, 'title')
            tt.text = f"{e['cell']} · {e['subject']} {e['predicate']} {e['object']} · {e['origin']}" + \
                (' from '+', '.join(e['source_ids']) if e['source_ids'] else '')
            ca, cb = ya+NODE_H/2, yb+NODE_H/2
            gap = lambda k, side: M+k*cw+(cw-nw)/2+(nw+(cw-nw)/2 if side > 0 else -(cw-nw)/2)  # noqa: E731  middle of the gap
            if ka == kb:                                           # same column: bracket in the right-hand gap
                n = same[ka] = same.get(ka, 0)+1
                xr = xa+nw+10+8*n
                pts = [(xa+nw, ca), (xr, ca), (xr, cb), (xa+nw+4, cb)]
                lx, ly, anchor = xr+4, (ca+cb)/2, 'start'
            elif abs(ka-kb) == 1:                                  # adjacent columns: straight through the gap
                x1, x2 = (xa+nw, xb) if ka < kb else (xa, xb+nw)
                pts = [(x1, ca), (x2, cb)]
                lx, ly, anchor = (x1+x2)/2, (ca+cb)/2-5, 'middle'
            else:                                                  # farther columns: via gaps and the lane above the target row
                d = 1 if kb > ka else -1
                x1, x2 = (xa+nw, xb) if d > 0 else (xa, xb+nw)
                n = lanes[(kb, yb)] = lanes.get((kb, yb), 0)+1
                lane = yb-NODE_GAP/2-3*(n-1)
                g1, g2 = gap(ka, d), gap(kb, -d)
                pts = [(x1, ca), (g1, ca), (g1, lane), (g2, lane), (g2, cb), (x2, cb)]
                lx, ly, anchor = (g1+g2)/2, lane-3, 'middle'
            segs = list(zip(pts, pts[1:]))
            for (p1, p2) in segs:
                el = line(eg, fmt(p1[0]), fmt(p1[1]), fmt(p2[0]), fmt(p2[1]), color=STROKE)
                el.set('stroke-width', '3.2' if e['placement'] else '1.6')
                if e['style'] in DASH:
                    el.set('stroke-dasharray', DASH[e['style']])
            (p1, p2) = segs[-1]
            _arrow(eg, p1[0], p1[1], p2[0], p2[1], STROKE)
            lt = text(eg, fmt(lx), fmt(ly), e['predicate'], 10, MUTED, anchor=anchor)
            lt.set('data-vp12-label', 'predicate')
        y0 += h+16
    if pr['x_outside']:
        text(root, M, y0+14, T['outside'].format(n=len(pr['x_outside'])), 11, MUTED)
    meta = add(root, 'metadata', id='vp12-landscape-ledger')
    meta.text = cjson(ledger(pr))
    return ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'


def report(pr, svg):
    inv = []

    def verify(ok, name):
        need(ok, 'VP12_AUDIT', 'VP-12 audit invariant failed: '+name, 'audit')
        inv.append(name)
    root = ET.fromstring(svg)
    led = ledger(pr)
    verify(no_active_content(root), 'NO_ACTIVE_SVG_CONTENT')
    blocks = [x for x in root.iter() if x.get('id') == 'vp12-landscape-ledger']
    verify(len(blocks) == 1 and blocks[0].text == cjson(led), 'EMBEDDED_LEDGER_MATCH')
    drawn = []
    for bg in root.iter(f'{{{NS}}}g'):
        s = bg.get('data-vp12-band')
        if s:
            drawn += [f"{s}|node|{g.get('data-vp12-node')}" for g in bg.iter(f'{{{NS}}}g') if g.get('data-vp12-node')]
            drawn += [f"{s}|edge|{g.get('data-edge-id')}" for g in bg.iter(f'{{{NS}}}g') if g.get('data-edge-id')]
    verify(sorted(drawn) == sorted(led['units']) and len(set(drawn)) == len(drawn), 'EACH_UNIT_DRAWN_ONCE')
    xs = {u.split('|')[2] for u in led['units'] if '|node|' in u}
    verify(not any(pr['items'][i]['anchor_id'].startswith(X_FAMILY+'.') for i in xs), 'NO_X_NODE')
    return {'format': 'aiaeao.cube.vp12-landscape-report/1', 'profile': PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS',
            'view': VIEW, 'plan_id': pr['src']['plan_id'], 'locale': pr['doc']['locale'], 'granularity': pr['doc']['granularity'],
            'source_sha256': sha_json(pr['src']), 'svg_sha256': sha_bytes(svg), **led,
            'counts': {'columns': len(pr['columns']), 'bands': len(pr['bands']), 'units': len(led['units'])},
            'warnings': pr['warnings'], 'invariants_passed': inv, 'content_status': 'declared_unverified', **NOT_EVALUATED,
            'notices': ['Nodes and edges are declared dependencies at declared steps; nothing is inferred or ranked.',
                        'Position, size and shade encode no quantity; bands are a declared step order, not a time scale.',
                        'Introduced and retired markers derive from presence between shown bands; declared_by names declared transitions.']}


def render_landscape(doc):
    pr = project(doc)
    svg = render(pr)
    return report(pr, svg), svg
