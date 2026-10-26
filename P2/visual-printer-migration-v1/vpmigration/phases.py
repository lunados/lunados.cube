"""VP-07 Path P: the `cube.phases` view (subjects × declared migration steps).

Display of declared, unverified cells only. Step order is the declared list order,
never a time axis; no colour or glyph carries status, success, risk or causality.
"""
from __future__ import annotations
import copy
from xml.etree import ElementTree as ET

from .common import (PROFILE, KEY, LEVELS, STYLES, DASH, STROKE, INK, MUTED, NOT_EVALUATED, Printer, VP01Error, NS,
                     add, line, rect, text, wrap_label, excerpt, source_digest, cjson, sha_bytes, VP07Error, need, keys,
                     clean, check_edge_styles, no_active_content, fmt)

REPORT_FORMAT = 'aiaeao.cube.vp07-phases-report/1'
# rows, steps, cells, lanes per row (PV-1, D-1)
BUDGET = {'overview': (3, 4, 6, 2), 'standard': (6, 5, 12, 3), 'detail': (8, 6, 24, 4)}
PLAN_REQUIRED = ('printer_profile', 'reference_version', 'view', 'lens', 'granularity', 'title', 'steps', 'rows', 'objects',
                 'cells', 'transitions', 'declaration_status')
PLAN_OPTIONAL = ('subtitle', 'edge_styles')
W = 1200
GX0, GX1 = 330, 1140
LANE_H, BAR_H = 34, 26
HATCH_GAP = 9


def lanes_for(cells, step_index):
    """Greedy first fit in declared order: one bar per lane, no overlap within a lane."""
    occupied = []
    out = {}
    for c in cells:
        lo = min(step_index[s] for s in c['steps'])
        hi = max(step_index[s] for s in c['steps'])
        for k, spans in enumerate(occupied):
            if all(hi < a or lo > b for a, b in spans):
                spans.append((lo, hi)); out[c['id']] = k; break
        else:
            occupied.append([(lo, hi)]); out[c['id']] = len(occupied)-1
    return out, len(occupied)


def hatch(parent, x, y, w, h, direction):
    """Explicit clipped diagonal lines (no <pattern>, no url()); direction '/' or '\\'."""
    g = add(parent, 'g', **{'data-vp07-hatch': 'A' if direction == '/' else 'B'})
    c = -h
    while c < w:
        pts = []
        for t in (0.0, h):
            # '/' : x = c + (h - yy) ; '\' : x = c + yy
            xx = c + (h - t if direction == '/' else t)
            pts.append((xx, t))
        (xa, ya), (xb, yb) = pts
        if xa > xb:
            (xa, ya), (xb, yb) = (xb, yb), (xa, ya)
        # clip to [0, w] keeping slope 1 or -1
        slope = (yb - ya) / (xb - xa)
        if xa < 0:
            ya += slope * (0 - xa); xa = 0.0
        if xb > w:
            yb -= slope * (xb - w); xb = float(w)
        if xb > xa:
            line(g, fmt(x+xa), fmt(y+ya), fmt(x+xb), fmt(y+yb), '#94A3B8')
        c += HATCH_GAP
    return g


class PhasesPrinter:
    def __init__(self):
        self.base = Printer()

    # -- validation ---------------------------------------------------------
    def validate(self, plan):
        keys(plan, PLAN_REQUIRED, PLAN_OPTIONAL, 'VP07_PHASES_PLAN', 'cube.phases plan')
        need(plan['printer_profile'] == PROFILE, 'VP07_PHASES_PLAN', 'printer_profile must be '+PROFILE)
        need(plan['reference_version'] == 'v9.4', 'VP07_PHASES_PLAN', 'reference_version must be v9.4')
        need(plan['view'] == 'cube.phases', 'VP07_PHASES_PLAN', 'view must be cube.phases')
        need(plan['lens'] == 'neutral', 'VP07_PHASES_LENS', 'cube.phases supports lens neutral only in 0.7.0 (PV-7)', 'lens')
        need(plan['granularity'] in LEVELS, 'VP07_PHASES_PLAN', 'granularity must be overview, standard or detail')
        need(plan['declaration_status'] == 'declared_unverified', 'VP07_PHASES_PLAN', 'declaration_status must be declared_unverified')
        need(clean(plan['title'], 78), 'VP07_PHASES_PLAN', 'title must be clean text <= 78')
        if 'subtitle' in plan:
            need(clean(plan['subtitle'], 95), 'VP07_PHASES_PLAN', 'subtitle must be clean text <= 95')
        steps = plan['steps']
        need(isinstance(steps, list) and len(steps) >= 2, 'VP07_PHASES_STEPS', 'cube.phases needs at least two declared steps')
        index = {}
        for s in steps:
            keys(s, ('id', 'label'), (), 'VP07_PHASES_PLAN', 'step')
            need(isinstance(s['id'], str) and KEY.fullmatch(s['id']) is not None, 'VP07_PHASES_PLAN', 'step id must be a stable ID')
            need(clean(s['label'], 40), 'VP07_PHASES_PLAN', 'step label must be clean text <= 40')
            need(s['id'] not in index, 'VP07_PHASES_STEPS', 'duplicate step '+s['id'])
            index[s['id']] = len(index)
        rows = plan['rows']
        need(isinstance(rows, list) and rows, 'VP07_PHASES_PLAN', 'rows must be a nonempty array')
        rmap = {}
        for r in rows:
            try:
                self.base._node(r)
            except VP01Error as e:
                raise VP07Error('VP07_PHASES_PLAN', 'row: '+str(e)) from e
            need(len(r['label']) <= 60, 'VP07_PHASES_PLAN', 'row label <= 60')
            need(r['id'] not in rmap, 'VP07_PHASES_PLAN', 'duplicate row '+r['id'])
            rmap[r['id']] = r
        objs = plan['objects']
        need(isinstance(objs, list) and objs, 'VP07_PHASES_PLAN', 'objects must be a nonempty array')
        omap = {}
        for o in objs:
            keys(o, ('id', 'anchor_id', 'label'), ('form_id', 'semantic_ref'), 'VP07_PHASES_PLAN', 'object')
            need(isinstance(o['id'], str) and KEY.fullmatch(o['id']) is not None, 'VP07_PHASES_PLAN', 'object id must be a stable ID')
            a = self.base.by_id.get(o['anchor_id'])
            need(a is not None, 'VP07_PHASES_PLAN', 'unknown canonical visual anchor: '+str(o['anchor_id']))
            if 'form_id' in o:
                need(o['form_id'] in (a['form_suggestion'], a['form_default']), 'VP07_PHASES_PLAN', 'form not recommended for anchor: '+o['anchor_id'])
            need(clean(o['label'], 60), 'VP07_PHASES_PLAN', 'object label must be clean text <= 60')
            need(o['id'] not in omap, 'VP07_PHASES_PLAN', 'duplicate object '+o['id'])
            omap[o['id']] = o
        cells = plan['cells']
        need(isinstance(cells, list) and cells, 'VP07_PHASES_PLAN', 'cells must be a nonempty array')
        out_cells = []
        seen = set()
        for i, c in enumerate(cells):
            keys(c, ('row', 'object', 'predicate_id', 'steps', 'declaration_ref'), ('id',), 'VP07_PHASES_PLAN', 'cell')
            c = dict(c)
            c.setdefault('id', 'c'+str(i+1))
            need(isinstance(c['id'], str) and KEY.fullmatch(c['id']) is not None, 'VP07_PHASES_PLAN', 'cell id must be a stable ID')
            need(c['id'] not in seen, 'VP07_PHASES_PLAN', 'duplicate cell '+c['id'])
            seen.add(c['id'])
            need(c['row'] in rmap, 'VP07_PHASES_REFERENCE', 'cell '+c['id']+' references unknown row '+repr(c['row']))
            need(c['object'] in omap, 'VP07_PHASES_REFERENCE', 'cell '+c['id']+' references unknown object '+repr(c['object']))
            need(clean(c['predicate_id'], 60), 'VP07_PHASES_PLAN', 'predicate_id must be clean text <= 60')
            need(clean(c['declaration_ref'], 180) and c['declaration_ref'].startswith(('decl:', 'fixture:')),
                 'VP07_PHASES_PLAN', 'declaration_ref must be scoped decl: or fixture: (<= 180)')
            st = c['steps']
            need(isinstance(st, list) and st and all(isinstance(x, str) for x in st), 'VP07_PHASES_STEPS', 'cell steps must be a nonempty array')
            for x in st:
                need(x in index, 'VP07_PHASES_REFERENCE', 'cell '+c['id']+' references unknown step '+repr(x))
            idx = [index[x] for x in st]
            need(idx == sorted(idx) and len(set(idx)) == len(idx), 'VP07_PHASES_STEPS', 'cell '+c['id']+' steps not in declared step order')
            need(idx == list(range(idx[0], idx[-1]+1)), 'VP07_PHASES_STEPS', 'cell '+c['id']+' steps not contiguous')
            out_cells.append(c)
        trs = plan['transitions']
        need(isinstance(trs, list), 'VP07_PHASES_PLAN', 'transitions must be an array')
        tseen = set()
        for t in trs:
            keys(t, ('id', 'at', 'retires', 'introduces', 'declaration_ref'), (), 'VP07_PHASES_PLAN', 'transition')
            need(isinstance(t['id'], str) and KEY.fullmatch(t['id']) is not None and t['id'] not in tseen, 'VP07_PHASES_PLAN',
                 'transition id must be a unique stable ID')
            tseen.add(t['id'])
            need(t['at'] in index, 'VP07_PHASES_REFERENCE', 'transition '+t['id']+' at unknown step '+repr(t['at']))
            for k in ('retires', 'introduces'):
                need(isinstance(t[k], list) and all(isinstance(x, str) for x in t[k]), 'VP07_PHASES_PLAN', 'transition '+k+' must be an array')
                for x in t[k]:
                    need(x in omap, 'VP07_PHASES_REFERENCE', 'transition '+t['id']+' references unknown object '+repr(x))
            need(t['retires'] or t['introduces'], 'VP07_PHASES_PLAN', 'transition retires or introduces nothing')
            need(clean(t['declaration_ref'], 180) and t['declaration_ref'].startswith(('decl:', 'fixture:')),
                 'VP07_PHASES_PLAN', 'transition declaration_ref must be scoped decl: or fixture:')
        styles = check_edge_styles(plan['edge_styles']) if 'edge_styles' in plan else None
        return {'index': index, 'rows': rmap, 'objects': omap, 'cells': out_cells, 'transitions': trs, 'styles': styles}

    # -- declared conflicts (PV-5, D-7) -------------------------------------
    @staticmethod
    def conflicts(d):
        retire, intro = {}, {}
        for t in d['transitions']:
            k = d['index'][t['at']]
            for o in t['retires']:
                retire[o] = min(k, retire.get(o, k))
            for o in t['introduces']:
                intro[o] = min(k, intro.get(o, k))
        out = []
        for c in d['cells']:
            idx = [d['index'][s] for s in c['steps']]
            o = c['object']
            if o in retire and idx[-1] >= retire[o]:
                out.append({'cell_id': c['id'], 'kind': 'holds_after_retirement', 'code': 'VP07_DECLARED_CONFLICT', 'object': o,
                            'steps': [s for s in c['steps'] if d['index'][s] >= retire[o]]})
            if o in intro and idx[0] < intro[o]:
                out.append({'cell_id': c['id'], 'kind': 'holds_before_introduction', 'code': 'VP07_DECLARED_PREMATURE', 'object': o,
                            'steps': [s for s in c['steps'] if d['index'][s] < intro[o]]})
        return out

    # -- budget / reduction (PV-1, PV-1a) -----------------------------------
    def project(self, plan, overflow='summarize'):
        d = self.validate(plan)
        need(overflow in ('summarize', 'reject'), 'VP07_PHASES_PLAN', 'overflow must be summarize or reject')
        g = plan['granularity']
        rcap, scap, ccap, lcap = BUDGET[g]
        need(len(plan['steps']) <= scap, 'VP07_PHASES_BUDGET', f'{len(plan["steps"])} steps exceed {g} ({scap}); steps are never summarized', 'granularity')
        by_row = {r: [c for c in d['cells'] if c['row'] == r] for r in d['rows']}
        lane_need = {r: lanes_for(cs, d['index'])[1] for r, cs in by_row.items()}
        over = []
        if len(d['rows']) > rcap:
            over.append(f'{len(d["rows"])} rows > {rcap}')
        if len(d['cells']) > ccap:
            over.append(f'{len(d["cells"])} cells > {ccap}')
        for r, n in lane_need.items():
            if n > lcap:
                over.append(f'row {r} needs {n} lanes > {lcap}')
        if over:
            need(g != 'detail', 'VP07_PHASES_BUDGET', 'detail never omits: '+'; '.join(over), 'granularity')
            need(overflow != 'reject', 'VP07_PHASES_BUDGET', 'overflow=reject: '+'; '.join(over), 'granularity')
        row_ids = [r['id'] for r in plan['rows']]
        kept_rows = row_ids[:rcap]
        kept, omitted = [], []
        for c in d['cells']:
            if c['row'] not in kept_rows:
                omitted.append({'id': c['id'], 'reason': 'row_omitted'}); continue
            if len(kept) >= ccap:
                omitted.append({'id': c['id'], 'reason': 'cell_budget'}); continue
            trial = [x for x in kept if x['row'] == c['row']]+[c]
            if lanes_for(trial, d['index'])[1] > lcap:
                omitted.append({'id': c['id'], 'reason': 'lane_budget'}); continue
            kept.append(c)
        shown_rows = [r for r in kept_rows if any(c['row'] == r for c in kept)]
        omitted_rows = [r for r in row_ids if r not in shown_rows]
        shown_objects = []
        for c in kept:
            if c['object'] not in shown_objects:
                shown_objects.append(c['object'])
        shown_tr = [t for t in d['transitions'] if set(t['retires']+t['introduces']) & set(shown_objects)]
        omitted_tr = [t['id'] for t in d['transitions'] if t not in shown_tr]
        lanes = {}
        for r in shown_rows:
            lanes.update(lanes_for([c for c in kept if c['row'] == r], d['index'])[0])
        nlanes = {r: max([lanes[c['id']] for c in kept if c['row'] == r]+[0])+1 for r in shown_rows}
        conf = self.conflicts(d)
        kept_ids = {c['id'] for c in kept}
        for x in conf:
            x['shown'] = x['cell_id'] in kept_ids
        used = []
        for c in d['cells']:
            if c['predicate_id'] not in used:
                used.append(c['predicate_id'])
        styles = d['styles']
        ledger = {'styled': {p: styles[p]['style'] for p in used if styles and p in styles},
                  'unstyled': [p for p in used if styles is not None and p not in styles],
                  'edge_styles_present': styles is not None}
        warnings = [{'code': x['code'], 'cell_id': x['cell_id'], 'shown': x['shown']} for x in conf]
        warnings += [{'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': p} for p in ledger['unstyled']]
        return {'derived': d, 'cells': kept, 'omitted_cells': omitted, 'rows': shown_rows, 'omitted_rows': omitted_rows,
                'objects': shown_objects, 'transitions': shown_tr, 'omitted_transitions': omitted_tr, 'lanes': lanes,
                'nlanes': nlanes, 'conflicts': conf, 'edge_style_ledger': ledger, 'warnings': warnings,
                'overflow': overflow, 'over_budget': over}

    # -- rendering (PV-2…PV-6) -----------------------------------------------
    def _bar(self, p, c, x, y, w, style, d, conflicts):
        o = d['objects'][c['object']]
        a = self.base.by_id[o['anchor_id']]
        g = add(p, 'g', **{'data-cell-id': c['id'], 'data-object-id': c['object'], 'data-predicate-id': c['predicate_id'],
                           'data-declaration-ref': c['declaration_ref'], 'data-vp07-edge-style': style})
        add(g, 'title').text = f"{c['row']} → {c['object']} | {c['predicate_id']} | {', '.join(c['steps'])} | {c['declaration_ref']}"
        r = rect(g, fmt(x), fmt(y), fmt(w), BAR_H, STROKE, '#F8FAFC', 5)
        if style in DASH:
            r.set('stroke-dasharray', DASH[style])
        if style == 'double':
            rect(g, fmt(x+3), fmt(y+3), fmt(w-6), BAR_H-6, STROKE, 'none', 3).set('data-vp07-double', 'twin')
        for x0, w0, kind in conflicts:
            hatch(g, x0, y, w0, BAR_H, '/' if kind == 'holds_after_retirement' else '\\')
        legend = (d['styles'] or {}).get(c['predicate_id'], {}).get('legend', c['predicate_id'])
        chars = max(6, int((w-34)/6.6))
        for t in (text(g, fmt(x+14), fmt(y+18), a['unicode'], 14, INK, anchor='middle', glyph=True),
                  text(g, fmt(x+28), fmt(y+17), excerpt(o['label']+' · '+legend, chars), 11, '#1E293B')):
            # light halo keeps the declared label legible over a hatch (no colour semantics)
            t.set('stroke', '#F8FAFC'); t.set('stroke-width', '3'); t.set('paint-order', 'stroke')
        return g

    def render(self, plan, overflow='summarize'):
        pr = self.project(plan, overflow)
        return self._render(plan, pr), pr

    def _render(self, plan, pr):
        d = pr['derived']
        steps = plan['steps']
        n = len(steps)
        cw = (GX1-GX0)/n
        top = 196
        row_y = {}
        y = top
        for r in pr['rows']:
            row_y[r] = y
            y += 18+pr['nlanes'][r]*LANE_H
        grid_bottom = max(y, top+40)
        styles = d['styles'] or {}
        used_styles = []
        for c in pr['cells']:
            st = styles.get(c['predicate_id'], {}).get('style', 'solid')
            if (c['predicate_id'], st) not in used_styles:
                used_styles.append((c['predicate_id'], st))
        shown_conf = [x for x in pr['conflicts'] if x['shown']]
        legend_lines = len(used_styles)+2+(1 if any(x['kind'] == 'holds_after_retirement' for x in shown_conf) else 0) + \
            (1 if any(x['kind'] == 'holds_before_introduction' for x in shown_conf) else 0)
        ledger_lines = len(pr['cells'])
        height = int(grid_bottom+70+legend_lines*22+40+ledger_lines*19+70)
        root = self.base._root({'view_id': 'cube.phases', 'title': plan['title'],
                                'subtitle': plan.get('subtitle', 'v9.4 · VP-07 · declared migration steps · display-only projection')}, height)
        root.set('data-printer-profile', PROFILE)
        root.set('data-cube-view', 'cube.phases')
        root.set('data-vp07-granularity', plan['granularity'])
        text(root, 60, 129, 'CUBE.PHASES · DECLARED STEPS AND DEPENDENCIES · step order is declared, not a time axis', 13, MUTED, 'bold')
        # header: steps
        for i, s in enumerate(steps):
            x = GX0+i*cw
            hg = add(root, 'g', **{'data-step-id': s['id']})
            rect(hg, fmt(x+2), 156, fmt(cw-4), 30, '#CBD5E1', '#F1F5F9', 6)
            text(hg, fmt(x+cw/2), 176, excerpt(s['label'], max(6, int((cw-12)/6.8))), 12, '#1E293B', 'bold', anchor='middle')
            line(root, fmt(x), 190, fmt(x), fmt(grid_bottom), '#E2E8F0')
        line(root, GX1, 190, GX1, fmt(grid_bottom), '#E2E8F0')
        # rows
        for r in pr['rows']:
            y0 = row_y[r]
            h = 8+pr['nlanes'][r]*LANE_H
            item = d['rows'][r]
            a = self.base.by_id[item['anchor_id']]
            rg = add(root, 'g', **{'data-item-id': r, 'data-anchor-id': item['anchor_id'], 'data-form-id': item['form_id']})
            if item.get('semantic_ref'):
                rg.set('data-semantic-ref', item['semantic_ref'])
            add(rg, 'title').text = item['label']+' · '+item['anchor_id']
            rect(rg, 60, fmt(y0), 255, fmt(h), '#94A3B8', '#F8FAFC', 8)
            text(rg, 82, fmt(y0+26), a['unicode'], 20, INK, anchor='middle', glyph=True)
            for j, s in enumerate(wrap_label(item['label'], 24)):
                text(rg, 102, fmt(y0+20+j*16), s, 12, INK, 'bold')
            line(root, 60, fmt(y0+h+5), GX1, fmt(y0+h+5), '#F1F5F9')
        # bars
        for c in pr['cells']:
            idx = [d['index'][s] for s in c['steps']]
            x = GX0+idx[0]*cw+6
            w = (idx[-1]-idx[0]+1)*cw-12
            y0 = row_y[c['row']]+6+pr['lanes'][c['id']]*LANE_H
            parts = []
            for k in [q for q in pr['conflicts'] if q['cell_id'] == c['id']]:
                ks = [d['index'][s] for s in k['steps']]
                xs = max(x, GX0+ks[0]*cw)
                xe = min(x+w, GX0+(ks[-1]+1)*cw)
                if xe > xs:
                    parts.append((xs, xe-xs, k['kind']))
            st = styles.get(c['predicate_id'], {}).get('style', 'solid')
            self._bar(root, c, x, y0, w, st, d, parts)
        # transitions (PV-4): vertical tick on the boundary of the declared step
        per_step = {}
        for t in pr['transitions']:
            k = d['index'][t['at']]
            off = per_step.get(k, 0)
            per_step[k] = off+1
            x = GX0+k*cw
            tg = add(root, 'g', **{'data-transition-id': t['id'], 'data-declaration-ref': t['declaration_ref'], 'data-step-id': t['at']})
            add(tg, 'title').text = f"{t['id']} at {t['at']} | retires {', '.join(t['retires']) or '–'} | introduces {', '.join(t['introduces']) or '–'}"
            line(tg, fmt(x), 186, fmt(x), fmt(grid_bottom), '#94A3B8')
            mx = x+8+off*30
            if t['retires']:
                add(tg, 'circle', cx=fmt(mx), cy=146, r=5, fill='#FFFFFF', stroke=MUTED, stroke_width=2)
            if t['introduces']:
                add(tg, 'circle', cx=fmt(mx+12 if t['retires'] else mx), cy=146, r=5, fill=MUTED, stroke=MUTED, stroke_width=2)
            text(tg, fmt(mx-6), 141, excerpt(t['id'], 10), 9, MUTED, anchor='end')
        # legend (ES-3, PV-4, PV-5)
        y = grid_bottom+40
        lg = add(root, 'g', **{'data-vp07-legend': 'display-only'})
        text(lg, 62, fmt(y), 'LEGEND · declared display conventions · not a verdict', 13, MUTED, 'bold')
        y += 24
        if d['styles'] is None:
            rect(lg, 70, fmt(y-12), 60, 12, STROKE, '#F8FAFC', 3)
            text(lg, 142, fmt(y), 'bar · one declared dependency across its declared steps (object · predicate)', 12, '#334155')
            y += 22
        for pid, st in (used_styles if d['styles'] is not None else []):
            sample = line(lg, 70, fmt(y-4), 130, fmt(y-4), STROKE)
            if st in DASH:
                sample.set('stroke-dasharray', DASH[st])
            if st == 'double':
                line(lg, 70, fmt(y-1), 130, fmt(y-1), STROKE)
            lab = styles[pid]['legend'] if pid in styles else pid+' · unstyled'
            text(lg, 142, fmt(y), f'{st} · {lab}', 12, '#334155')
            y += 22
        add(lg, 'circle', cx=76, cy=fmt(y-4), r=5, fill='#FFFFFF', stroke=MUTED, stroke_width=2)
        text(lg, 142, fmt(y), 'outlined marker · transition declares a retirement at this step boundary', 12, '#334155')
        y += 22
        add(lg, 'circle', cx=76, cy=fmt(y-4), r=5, fill=MUTED, stroke=MUTED, stroke_width=2)
        text(lg, 142, fmt(y), 'filled marker · transition declares an introduction at this step boundary', 12, '#334155')
        y += 22
        for kind, label in (('holds_after_retirement', 'hatch / · declared to hold after its object is retired'),
                            ('holds_before_introduction', 'hatch \\ · declared to hold before its object is introduced')):
            if any(x['kind'] == kind for x in shown_conf):
                hatch(lg, 70, y-14, 60, 14, '/' if kind == 'holds_after_retirement' else '\\')
                rect(lg, 70, fmt(y-14), 60, 14, STROKE, 'none', 2)
                text(lg, 142, fmt(y), label, 12, '#334155')
                y += 22
        # declaration ledger
        y += 18
        text(root, 62, fmt(y), 'DECLARATION LEDGER · each bar is a declared, unverified assertion', 13, MUTED, 'bold')
        for c in pr['cells']:
            y += 19
            text(root, 68, fmt(y), f"{c['id']} · {excerpt(c['row'], 18)} → {excerpt(c['object'], 18)} · {excerpt(c['predicate_id'], 18)} · "
                 f"{c['steps'][0]}–{c['steps'][-1]}", 11, '#334155')
            text(root, 640, fmt(y), excerpt(c['declaration_ref'], 82), 10, MUTED)
        s = self.summary(plan, pr)
        text(root, 62, fmt(y+30), f"Shown {s['rows_shown']} rows / {s['cells_shown']} cells · omitted {s['rows_omitted']} rows / "
             f"{s['cells_omitted']} cells / {s['transitions_omitted']} transitions · {plan['granularity'].upper()} budget", 12, MUTED)
        meta = add(root, 'metadata', id='vp07-phases-ledger')
        meta.text = cjson(self.ledger(plan, pr))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg

    @staticmethod
    def summary(plan, pr):
        return {'rows_shown': len(pr['rows']), 'rows_omitted': len(pr['omitted_rows']), 'cells_shown': len(pr['cells']),
                'cells_omitted': len(pr['omitted_cells']), 'transitions_shown': len(pr['transitions']),
                'transitions_omitted': len(pr['omitted_transitions'])}

    @staticmethod
    def ledger(plan, pr):
        return {'profile': PROFILE, 'source_plan_sha256': source_digest(plan), 'granularity': plan['granularity'],
                'overflow': pr['overflow'], 'shown_row_ids': pr['rows'], 'omitted_row_ids': pr['omitted_rows'],
                'shown_cell_ids': [c['id'] for c in pr['cells']], 'omitted_cells': pr['omitted_cells'],
                'shown_transition_ids': [t['id'] for t in pr['transitions']], 'omitted_transition_ids': pr['omitted_transitions'],
                'declared_conflicts': pr['conflicts'], 'status': 'declared_unverified',
                'nonimplications': ['truth', 'causality', 'authority', 'admission', 'completeness', 'time']}

    def report(self, plan, svg, pr):
        d = pr['derived']
        all_cells = {c['id'] for c in d['cells']}
        shown = {c['id'] for c in pr['cells']}
        omitted = {c['id'] for c in pr['omitted_cells']}
        root = ET.fromstring(svg)
        inv = []

        def verify(ok, name):
            need(ok, 'VP07_AUDIT', 'VP-07 audit invariant failed: '+name, 'audit')
            inv.append(name)
        verify(shown | omitted == all_cells and not shown & omitted, 'EXACT_CELL_PARTITION')
        verify(set(pr['rows']) | set(pr['omitted_rows']) == set(d['rows']) and not set(pr['rows']) & set(pr['omitted_rows']), 'EXACT_ROW_PARTITION')
        verify(no_active_content(root), 'NO_ACTIVE_SVG_CONTENT')
        blocks = [x for x in root.iter() if x.get('id') == 'vp07-phases-ledger']
        verify(len(blocks) == 1, 'ONE_EMBEDDED_LEDGER')
        verify(blocks[0].text == cjson(self.ledger(plan, pr)), 'EMBEDDED_REPORT_MATCH')
        verify(sorted(g.get('data-cell-id') for g in root.iter(f'{{{NS}}}g') if g.get('data-cell-id')) == sorted(shown), 'DRAWN_CELLS_MATCH')
        verify(all(c['steps'] == next(x for x in plan['cells'] if x.get('id', 'c'+str(plan['cells'].index(x)+1)) == c['id'])['steps']
                   for c in pr['cells']), 'ORIGINAL_CELLS_UNCHANGED')
        s = self.summary(plan, pr)
        return {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS',
                'view': 'cube.phases', 'lens': 'neutral', 'granularity': plan['granularity'], 'overflow': pr['overflow'],
                'migration_view_profile': PROFILE, 'source_plan_sha256': source_digest(plan), 'svg_sha256': sha_bytes(svg),
                'counts': {'source_rows': len(d['rows']), 'source_cells': len(d['cells']), 'source_transitions': len(d['transitions']), **s},
                **{k: v for k, v in self.ledger(plan, pr).items() if k not in ('profile', 'status', 'nonimplications')},
                'completeness': 'PARTIAL_EXPLICIT' if omitted or pr['omitted_rows'] or pr['omitted_transitions'] else 'COMPLETE_INPUT_VIEW',
                'edge_style_ledger': pr['edge_style_ledger'], 'warnings': pr['warnings'], 'invariants_passed': inv,
                'content_status': 'declared_unverified', 'source_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Step order is the declared list order, not a time axis.',
                            'Hatches mirror declared cells and transitions only; they never replace a P1 report.',
                            'Bar styles carry only their declared legend text; no colour or glyph carries status.']}


def render_plan(plan, overflow='summarize'):
    p = PhasesPrinter()
    svg, pr = p.render(plan, overflow)
    return p.report(plan, svg, pr), svg
