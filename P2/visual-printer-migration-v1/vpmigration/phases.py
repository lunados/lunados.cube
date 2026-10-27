"""VP-07 Path P: the `cube.phases` view (subjects × declared migration steps).

Display of declared, unverified cells only. Step order is the declared list order,
never a time axis; no colour or glyph carries status, success, risk or causality.
"""
from __future__ import annotations
import copy
from xml.etree import ElementTree as ET

from .common import (PROFILE, PROFILES, P071, P072, V71UP, CODE, END_REASONS, DECLARED_ENDS, KEY, LEVELS, STYLES, DASH, STROKE, INK, MUTED, NOT_EVALUATED, Printer, VP01Error, NS,
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
MAX_STACK, STACK_PITCH = 4, 16  # VP-07.1 D-4
CELL_071 = ('successor', 'dropped', 'ends_reason', 'declared_end')
LW1 = {'holds_after_retirement': 'Hatch A (diagonal lines rising) — declared to hold after its object is retired',
       'holds_before_introduction': 'Hatch B (diagonal lines falling) — declared to hold before its object is introduced'}
GAP_LEGEND = 'Gap — declared to end before the target step without retirement, successor, drop or end reason'


def wrap_words(s, width):
    """Wrap on spaces without truncation (TM-5); an overlong word is split, never cut."""
    out, cur = [], ''
    for w in s.split(' '):
        while len(w) > width:
            if cur:
                out.append(cur); cur = ''
            out.append(w[:width]); w = w[width:]
        if cur and len(cur)+1+len(w) > width:
            out.append(cur); cur = w
        else:
            cur = (cur+' '+w) if cur else w
    if cur:
        out.append(cur)
    return out or ['']


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
        v71 = isinstance(plan, dict) and plan.get('printer_profile') in V71UP
        v72 = v71 and plan.get('printer_profile') == P072
        keys(plan, PLAN_REQUIRED, PLAN_OPTIONAL+(('target_step',) if v71 else ())+(('layer_order', 'row_layers') if v72 else ()),
             'VP07_PHASES_PLAN', 'cube.phases plan')
        need(plan['printer_profile'] in PROFILES, 'VP07_PHASES_PLAN', 'printer_profile must be '+' or '.join(PROFILES))
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
            keys(c, ('row', 'object', 'predicate_id', 'steps', 'declaration_ref'), ('id',)+(CELL_071 if v71 else ()), 'VP07_PHASES_PLAN', 'cell')
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
            if v71:
                self._cell071(c)
            out_cells.append(c)
        trs = plan['transitions']
        need(isinstance(trs, list), 'VP07_PHASES_PLAN', 'transitions must be an array')
        tseen = set()
        codes, cseen = {}, set()
        for ti, t in enumerate(trs):
            keys(t, ('id', 'at', 'retires', 'introduces', 'declaration_ref'), ('code',) if v71 else (), 'VP07_PHASES_PLAN', 'transition')
            need(isinstance(t['id'], str) and KEY.fullmatch(t['id']) is not None and t['id'] not in tseen, 'VP07_PHASES_PLAN',
                 'transition id must be a unique stable ID')
            tseen.add(t['id'])
            need(t['at'] in index, 'VP07_PHASES_REFERENCE', 'transition '+t['id']+' at unknown step '+repr(t['at']))
            for k in ('retires', 'introduces'):
                need(isinstance(t[k], list) and all(isinstance(x, str) for x in t[k]), 'VP07_PHASES_PLAN', 'transition '+k+' must be an array')
                for x in t[k]:
                    need(x in omap or (v71 and x in rmap), 'VP07_PHASES_REFERENCE', 'transition '+t['id']+' references unknown object '+repr(x))
            need(t['retires'] or t['introduces'], 'VP07_PHASES_PLAN', 'transition retires or introduces nothing')
            need(clean(t['declaration_ref'], 180) and t['declaration_ref'].startswith(('decl:', 'fixture:')),
                 'VP07_PHASES_PLAN', 'transition declaration_ref must be scoped decl: or fixture:')
            if v71:
                code = t.get('code', 'T'+str(ti+1))
                need(isinstance(code, str) and CODE.fullmatch(code) is not None, 'VP07_PHASES_PLAN', 'transition code must be T + 1…3 digits (PD-3)')
                need(code not in cseen, 'VP07_PHASES_PLAN', 'transition code '+code+' used twice (TM-1)')
                cseen.add(code); codes[t['id']] = code
        styles = check_edge_styles(plan['edge_styles']) if 'edge_styles' in plan else None
        d = {'index': index, 'rows': rmap, 'objects': omap, 'cells': out_cells, 'transitions': trs, 'styles': styles}
        if v71:
            target = plan.get('target_step', steps[-1]['id'])
            need(isinstance(target, str) and KEY.fullmatch(target) is not None, 'VP07_PHASES_PLAN', 'target_step must be a stable ID (GM-2)')
            d.update(v71=True, codes=codes, target=target, tindex=index.get(target, len(steps)))
            d['layers'] = self._layers072(plan, rmap) if v72 else None
        else:
            d['v71'] = False
        return d

    @staticmethod
    def _layers072(plan, rmap):
        """VP-07.2 LS-2: optional declared layer order and row → layer assignment (display input only)."""
        if 'layer_order' not in plan and 'row_layers' not in plan:
            return None
        lo, rl = plan.get('layer_order'), plan.get('row_layers')
        need(isinstance(lo, list) and 1 <= len(lo) <= 13 and all(clean(x, 24) for x in lo) and len(set(lo)) == len(lo),
             'VP07_PHASES_PLAN', 'layer_order must be 1…13 distinct clean names <= 24')
        need(isinstance(rl, dict) and set(rl) == set(rmap) and all(v in lo for v in rl.values()), 'VP07_PHASES_PLAN',
             'row_layers must assign every row to a layer of layer_order')
        return {'order': lo, 'rows': rl}

    @staticmethod
    def _cell071(c):
        if 'successor' in c:
            need(isinstance(c['successor'], str) and KEY.fullmatch(c['successor']) is not None, 'VP07_PHASES_PLAN', 'cell successor must be a stable ID')
        if 'dropped' in c:
            need(isinstance(c['dropped'], bool), 'VP07_PHASES_PLAN', 'cell dropped must be boolean')
            need(not (c['dropped'] and 'successor' in c), 'VP07_PHASES_PLAN', 'cell successor and dropped are exclusive')
        if 'ends_reason' in c:
            need(clean(c['ends_reason'], 40), 'VP07_PHASES_PLAN', 'cell ends_reason must be clean text <= 40')
        if 'declared_end' in c:
            need(c['declared_end'] in DECLARED_ENDS, 'VP07_PHASES_PLAN', 'declared_end must be one of '+', '.join(DECLARED_ENDS)+' (GM-3)')

    # -- declared gaps (VP-07.1 GM-1…GM-5, mirrors P1.10.1 DG-2…DG-7) -------
    @staticmethod
    def gaps(d):
        if not d.get('v71'):
            return []
        retire, intro = {}, {}
        for t in d['transitions']:
            k = d['index'][t['at']]
            for r in t['retires']:
                retire.setdefault(r, []).append(k)
            for r in t['introduces']:
                intro.setdefault(r, []).append(k)
        conflict = {r for r in set(retire) | set(intro) if len(retire.get(r, [])) > 1 or len(intro.get(r, [])) > 1
                    or (r in retire and r in intro and min(retire[r]) <= min(intro[r]))}
        R = {r: min(v) for r, v in retire.items()}
        out = []
        for c in d['cells']:
            k = d['index'][c['steps'][-1]]
            de = c.get('declared_end')
            if de is not None:
                if de == 'unexplained':
                    out.append({'cell_id': c['id'], 'code': 'VP07_DECLARED_GAP', 'object': c['object'], 'last_step': c['steps'][-1],
                                'target_step': d['target'], 'basis': 'declared_end'})
                continue
            if k >= d['tindex']:
                continue
            o, s = c['object'], c['row']
            if o in conflict or s in conflict:
                continue
            if (o in R and R[o] <= k+1) or (s in R and R[s] <= k+1):
                continue
            if c.get('dropped') or 'successor' in c or c.get('ends_reason') in END_REASONS:
                continue
            out.append({'cell_id': c['id'], 'code': 'VP07_DECLARED_GAP', 'object': o, 'last_step': c['steps'][-1],
                        'target_step': d['target'], 'basis': 'plan'})
        return out

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
        visible = set(shown_objects) | (set(shown_rows) if d['v71'] else set())
        shown_tr = [t for t in d['transitions'] if set(t['retires']+t['introduces']) & visible]
        if d['v71']:
            stack = {}
            for t in shown_tr:
                stack[t['at']] = stack.get(t['at'], 0)+1
            for at, k in stack.items():
                need(k <= MAX_STACK, 'VP07_PHASES_BUDGET', f'{k} transitions at step boundary {at} exceed the marker stack ({MAX_STACK}, D-4)', 'granularity')
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
        gaps = self.gaps(d)
        for x in gaps:
            x['shown'] = x['cell_id'] in kept_ids
        warnings += [{'code': x['code'], 'cell_id': x['cell_id'], 'shown': x['shown']} for x in gaps]
        warnings += [{'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': p} for p in ledger['unstyled']]
        return {'gaps': gaps, 'derived': d, 'cells': kept, 'omitted_cells': omitted, 'rows': shown_rows, 'omitted_rows': omitted_rows,
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

    @staticmethod
    def _bands(root, pr, row_y, layers):
        """VP-07.2 LD-1: a band left of the row cards per run of rows in one declared layer, rules between layers; no fill."""
        runs = []
        for r in pr['rows']:
            lay = layers['rows'][r]
            if runs and runs[-1][0] == lay:
                runs[-1][1].append(r)
            else:
                runs.append((lay, [r]))
        for k, (lay, rs) in enumerate(runs):
            top = row_y[rs[0]]
            bottom = row_y[rs[-1]]+8+pr['nlanes'][rs[-1]]*LANE_H
            g = add(root, 'g', **{'data-vp07-layer': lay, 'data-vp07-layer-rows': ' '.join(rs)})
            add(g, 'title').text = f'declared layer {lay}: '+', '.join(rs)
            rect(g, 43, fmt(top), 14, fmt(bottom-top), '#CBD5E1', 'none', 3)
            cx, cy = 50, (top+bottom)/2
            t = text(g, fmt(cx+4), fmt(cy), excerpt(lay, max(3, int((bottom-top-8)/6.2))), 10, MUTED, 'bold', anchor='middle')
            t.set('transform', f'rotate(-90 {fmt(cx)} {fmt(cy)})')
            if k:
                line(g, 43, fmt(top-6), GX1, fmt(top-6), '#CBD5E1')

    @staticmethod
    def _cap(parent, x, y, h):
        """Gap end cap (GM-4): short vertical line plus a bracket opening back onto the bar end; no colour."""
        line(parent, fmt(x), fmt(y), fmt(x), fmt(y+h), STROKE)
        line(parent, fmt(x-5), fmt(y), fmt(x), fmt(y), STROKE)
        line(parent, fmt(x-5), fmt(y+h), fmt(x), fmt(y+h), STROKE)

    @staticmethod
    def _marker(tg, t, code, x, cy, slot, grid_bottom, y_top):
        """TM-1…TM-4: coded marker in slot `slot` (stacked upwards, fixed pitch); glyph meaning unchanged."""
        tg.set('data-vp07-code', code)
        tg.set('data-vp07-marker-slot', str(slot))
        line(tg, fmt(x), fmt(y_top), fmt(x), fmt(grid_bottom), '#94A3B8')
        gx = x+8
        last = gx
        if t['retires']:
            add(tg, 'circle', cx=fmt(gx), cy=fmt(cy), r=5, fill='#FFFFFF', stroke=MUTED, stroke_width=2)
        if t['introduces']:
            last = gx+12 if t['retires'] else gx
            add(tg, 'circle', cx=fmt(last), cy=fmt(cy), r=5, fill=MUTED, stroke=MUTED, stroke_width=2)
        text(tg, fmt(last+9), fmt(cy+4), code, 11, INK, 'bold')

    @staticmethod
    def _tlegend(plan, pr):
        """TM-5: per shown transition its code, full ID, declared step and object/subject labels (wrapped, never cut)."""
        d = pr['derived']
        steps = {s['id']: s['label'] for s in plan['steps']}

        def lab(x):
            it = d['objects'].get(x) or d['rows'].get(x)
            return it['label']
        out = []
        for t in pr['transitions']:
            parts = []
            if t['retires']:
                parts.append('retires '+', '.join(lab(x) for x in t['retires']))
            if t['introduces']:
                parts.append('introduces '+', '.join(lab(x) for x in t['introduces']))
            body = f"{t['id']} · at {steps[t['at']]} · "+' · '.join(parts)
            code = d['codes'][t['id']]
            out.append((code, t['id'], wrap_words(body, 110), code+' · '+body+' · '+t['declaration_ref']))
        return out

    def render(self, plan, overflow='summarize'):
        pr = self.project(plan, overflow)
        return self._render(plan, pr), pr

    def _render(self, plan, pr):
        d = pr['derived']
        steps = plan['steps']
        n = len(steps)
        cw = (GX1-GX0)/n
        v71 = d['v71']
        depth = {}
        for t in pr['transitions']:
            depth[t['at']] = depth.get(t['at'], 0)+1
        dy = STACK_PITCH*(max(depth.values())-1) if v71 and depth else 0
        tlegend = self._tlegend(plan, pr) if v71 else []
        shown_gaps = [x for x in pr['gaps'] if x['shown']]
        top = 196+dy
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
        if v71:
            height += (22 if shown_gaps else 0)+(44+sum(18*(len(e[2])-1)+24 for e in tlegend) if tlegend else 0)
        root = self.base._root({'view_id': 'cube.phases', 'title': plan['title'],
                                'subtitle': plan.get('subtitle', 'v9.4 · VP-07 · declared migration steps · display-only projection')}, height)
        root.set('data-printer-profile', plan['printer_profile'])
        root.set('data-cube-view', 'cube.phases')
        root.set('data-vp07-granularity', plan['granularity'])
        text(root, 60, 129, 'CUBE.PHASES · DECLARED STEPS AND DEPENDENCIES · step order is declared, not a time axis', 13, MUTED, 'bold')
        # header: steps
        for i, s in enumerate(steps):
            x = GX0+i*cw
            hg = add(root, 'g', **{'data-step-id': s['id']})
            rect(hg, fmt(x+2), 156+dy, fmt(cw-4), 30, '#CBD5E1', '#F1F5F9', 6)
            text(hg, fmt(x+cw/2), 176+dy, excerpt(s['label'], max(6, int((cw-12)/6.8))), 12, '#1E293B', 'bold', anchor='middle')
            line(root, fmt(x), 190+dy, fmt(x), fmt(grid_bottom), '#E2E8F0')
        line(root, GX1, 190+dy, GX1, fmt(grid_bottom), '#E2E8F0')
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
        if d.get('layers'):
            self._bands(root, pr, row_y, d['layers'])
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
            gap = next((q for q in shown_gaps if q['cell_id'] == c['id']), None)
            if gap is not None:
                gg = add(root, 'g', **{'data-vp07-gap': c['id']})
                add(gg, 'title').text = f"{c['id']} · declared to end at {gap['last_step']} before target {gap['target_step']} " \
                    f"without retirement, successor, drop or end reason ({gap['basis']})"
                self._cap(gg, x+w+3, y0-2, BAR_H+4)
        # transitions (PV-4): vertical tick on the boundary of the declared step
        per_step = {}
        for t in pr['transitions']:
            k = d['index'][t['at']]
            off = per_step.get(k, 0)
            per_step[k] = off+1
            x = GX0+k*cw
            tg = add(root, 'g', **{'data-transition-id': t['id'], 'data-declaration-ref': t['declaration_ref'], 'data-step-id': t['at']})
            add(tg, 'title').text = f"{t['id']} at {t['at']} | retires {', '.join(t['retires']) or '–'} | introduces {', '.join(t['introduces']) or '–'}"
            if v71:
                self._marker(tg, t, d['codes'][t['id']], x, 146+dy-off*STACK_PITCH, off, grid_bottom, 186+dy)
                continue
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
                text(lg, 142, fmt(y), LW1[kind] if v71 else label, 12, '#334155')
                y += 22
        if v71 and shown_gaps:
            rect(lg, 70, fmt(y-14), 48, 14, STROKE, '#F8FAFC', 2)
            self._cap(lg, 124, y-16, 18)
            text(lg, 142, fmt(y), GAP_LEGEND, 12, '#334155')
            y += 22
        if tlegend:
            y += 22
            tl = add(root, 'g', **{'data-vp07-transition-legend': 'display-only'})
            text(tl, 62, fmt(y), 'TRANSITIONS · declared step boundaries · codes are stable across panels', 13, MUTED, 'bold')
            y += 22
            for code, tid, lines, full in tlegend:
                eg = add(tl, 'g', **{'data-vp07-legend-code': code, 'data-transition-id': tid})
                add(eg, 'title').text = full
                text(eg, 70, fmt(y), code, 12, INK, 'bold')
                text(eg, 120, fmt(y), lines[0], 12, '#334155')
                for extra in lines[1:]:
                    y += 18
                    text(eg, 120, fmt(y), extra, 11, '#334155')
                y += 24
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
        led = {'profile': plan['printer_profile'], 'source_plan_sha256': source_digest(plan), 'granularity': plan['granularity'],
                'overflow': pr['overflow'], 'shown_row_ids': pr['rows'], 'omitted_row_ids': pr['omitted_rows'],
                'shown_cell_ids': [c['id'] for c in pr['cells']], 'omitted_cells': pr['omitted_cells'],
                'shown_transition_ids': [t['id'] for t in pr['transitions']], 'omitted_transition_ids': pr['omitted_transitions'],
                'declared_conflicts': pr['conflicts'], 'status': 'declared_unverified',
                'nonimplications': ['truth', 'causality', 'authority', 'admission', 'completeness', 'time']}
        if pr['derived']['v71']:
            led.update(target_step=pr['derived']['target'], declared_gaps=pr['gaps'],
                       transition_codes={t['id']: pr['derived']['codes'][t['id']] for t in pr['transitions']})
        if pr['derived'].get('layers'):
            led['row_layers'] = {r: pr['derived']['layers']['rows'][r] for r in pr['rows']}
        return led

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
        if d['v71']:
            verify(sorted(g.get('data-vp07-gap') for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-gap'))
                   == sorted(x['cell_id'] for x in pr['gaps'] if x['shown']), 'DRAWN_GAPS_MATCH')
            verify(sorted(g.get('data-vp07-code') for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-code'))
                   == sorted(d['codes'][t['id']] for t in pr['transitions']), 'DRAWN_CODES_MATCH')
        s = self.summary(plan, pr)
        prof = plan['printer_profile']
        return {'format': REPORT_FORMAT, 'profile': prof, 'reference_version': 'v9.4', 'render_status': 'PASS',
                'view': 'cube.phases', 'lens': 'neutral', 'granularity': plan['granularity'], 'overflow': pr['overflow'],
                'migration_view_profile': prof, 'source_plan_sha256': source_digest(plan), 'svg_sha256': sha_bytes(svg),
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
