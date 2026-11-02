"""VP-10 view `cube.cells`: the VP-09.2 Y × Y matrix with four cell states from declared coverage (CS-1…CS-7).

Display only. The VP-09.2 printer draws the grid and every declared entry unchanged; VP-10 assigns each cell
exactly one state, draws checked-empty, unknown and element cells, names hidden values and audits that the
states differ without colour. "checked" means no declared statement within the declared survey scope (CV-5).
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from vpaxes.axes import AxesPrinter, GX0, GX1
from vpaxes.common import BUDGET, HIDE_EMPTY, MUTED, INK, add, line, rect, text, fmt, no_active_content
from .common import (PROFILE, PROFILE_101, BASE_PROFILE, REPORT_FORMAT, NS, NOT_EVALUATED, MATRIX_FORMAT, Texts, OrderTexts, need, sha_bytes, sha_json, cjson,
                     wrap_sep)
from .source import normalize

CHECK_STROKE = '2.6'      # bold border: checked empty (non-colour attribute, CS-6)
HATCH_STEP = 6            # hatch C: explicit horizontal lines (PV-5 technique, D-5)
HATCH_COLOR = '#94A3B8'


def _key(r, c):
    return f'{r}|{c}'


def _ordered(values, axis_order):
    """AO-1 (Q-3, Q-5): declared order within each kind group; unlisted values follow in their previous order."""
    rank = {v: i for i, v in enumerate(axis_order)}
    out, kinds = [], []
    for v in values:
        if v[2] not in kinds:
            kinds.append(v[2])
    for k in kinds:
        grp = [v for v in values if v[2] == k]
        out += sorted((v for v in grp if v[0] in rank), key=lambda v: rank[v[0]]) + [v for v in grp if v[0] not in rank]
    return out


class CellsPrinter:
    def __init__(self):
        self.axes = AxesPrinter()

    # -- states (CS-1…CS-5) ---------------------------------------------------
    def project(self, doc, rows, cols, granularity='standard', hide_empty=None, locale=None, axis_order=None):
        doc = normalize(doc)
        need(rows == 'Y:referent' and cols == 'Y:referent', 'VP10_PAIR_INVALID', 'VP-10 draws cell states in Y:referent × Y:referent only (D-3)')
        need(hide_empty in (None,)+HIDE_EMPTY, 'VP10_AXIS_INVALID', 'hide_empty must be rows|cols|both')
        T = Texts(locale)
        pr = self.axes.project(doc['axes'], rows, cols, granularity, budget_check=False, locale=locale)
        cov = doc['coverage']
        pred = cov['predicate']
        cells = pr['cells']
        shown_ids = {c['id'] for c in pr['model'].cells}
        star = {}                                            # D-4: declared, but only outside the slice
        for pp in cov['plan_pairs']:
            if pp['dependency_id'] not in shown_ids:
                star.setdefault((pp['row'], pp['col']), []).append(f"{pp['dependency_id']}* · {pred}")
        suffix = ' · '+pred

        def scope_of(r, c):
            for d in cov['declarations']:                    # CS-2, precedence pair > row > column
                if d['scope'] == 'pair' and (d['row'], d['col']) == (r, c):
                    return 'pair', d['declaration_id']
            for d in cov['declarations']:
                if d['scope'] == 'row' and d['row'] == r:
                    return 'row', d['declaration_id']
            for d in cov['declarations']:
                if d['scope'] == 'column' and d['col'] == c:
                    return 'column', d['declaration_id']
            return None, None
        rall, call = list(pr['rv']), list(pr['cv'])
        order = None
        if axis_order is not None:                           # VP-10.1 (Q-1, Q-2): a display option; its presence selects 0.10.1
            need(isinstance(axis_order, list) and axis_order and all(isinstance(v, str) and v for v in axis_order), 'VP10_ORDER_INVALID',
                 'axis_order must be a non-empty list of display IDs')
            need(len(set(axis_order)) == len(axis_order), 'VP10_ORDER_INVALID',
                 'axis_order lists a value twice: '+', '.join(sorted({v for v in axis_order if axis_order.count(v) > 1})))
            known = {v for v, _, _ in rall}
            rall, call = _ordered(rall, axis_order), _ordered(call, axis_order)
            order = {'axis_order': list(axis_order), 'not_in_view': [v for v in axis_order if v not in known],
                     'unordered_values': [v for v, _, _ in rall if v not in set(axis_order)]}
        states = {}
        for r, _, _ in rall:
            for c, _, _ in call:
                ents = list(cells.get((r, c), []))
                if r == c:
                    states[(r, c)] = {'state': 'element', 'entries': ents}
                    continue
                mine = [e for e in ents if e.endswith(suffix)]
                scope, did = scope_of(r, c)
                if mine:
                    st = {'state': 'marked'}
                elif star.get((r, c)) and scope:
                    st = {'state': 'marked'}; ents = ents + star[(r, c)]
                elif scope:
                    st = {'state': 'checked', 'scope': scope, 'declaration_id': did}
                else:
                    st = {'state': 'unknown'}
                st['entries'] = ents
                states[(r, c)] = st
        for (r, c), st in states.items():                    # the star entries are drawn by the unchanged VP-09.2 code
            if st['entries'] and st['entries'] != cells.get((r, c), []):
                cells[(r, c)] = st['entries']
        quiet = lambda st: st['state'] in ('unknown', 'element') and not st['entries']  # noqa: E731
        hidden_rows, hidden_cols = [], []
        if hide_empty in ('rows', 'both'):                   # CS-5 (D-6): only values without marked or checked cells
            hidden_rows = [r for r, _, _ in rall if all(quiet(states[(r, c)]) for c, _, _ in call)]
        if hide_empty in ('cols', 'both'):
            hidden_cols = [c for c, _, _ in call if all(quiet(states[(r, c)]) for r, _, _ in rall)]
        pr['rv'] = [x for x in rall if x[0] not in hidden_rows]
        pr['cv'] = [x for x in call if x[0] not in hidden_cols]
        rcap, ccap, _ = BUDGET[granularity]
        need(len(pr['rv']) <= rcap and len(pr['cv']) <= ccap, 'VP09_AXES_BUDGET',
             f"{len(pr['rv'])} rows / {len(pr['cv'])} columns exceed {granularity} ({rcap}/{ccap})", 'granularity')
        hidden_cells = [_key(r, c) for r, _, _ in rall for c, _, _ in call if r in hidden_rows or c in hidden_cols]
        warnings = []
        if not cov['declared']:
            warnings.append({'code': 'VP10_COVERAGE_NONE', 'detail': 'no coverage_declarations in the context: every empty cell is unknown (D-9)'})
        for x in cov['ignored']:
            if x['reason'] == 'ref_unknown':
                warnings.append({'code': 'VP10_COVERAGE_REF_UNKNOWN', 'declaration_id': x['declaration_id'],
                                 'detail': 'names a referent that is not an item of this input (undeclared or outside the slice); ignored'})
            elif x['reason'] == 'instance_ref':
                warnings.append({'code': 'VP10_COVERAGE_INSTANCE_IGNORED', 'declaration_id': x['declaration_id'],
                                 'detail': 'instance-restricted declaration; a plan dependency carries no instance (D-7); ignored'})
        if order is not None:
            pos = {v: i for i, (v, _, _) in enumerate(rall)}
            order['feedback_cells'] = sorted(_key(r, c) for (r, c), st in states.items()
                                             if st['state'] == 'marked' and pos[r] < pos[c] and _key(r, c) not in hidden_cells)
            for v in order['not_in_view']:
                warnings.append({'code': 'VP10_ORDER_NOT_IN_VIEW', 'value': v,
                                 'detail': 'axis_order names a value that is not a Y:referent of this view (unknown or outside the slice); ignored'})
            if order['unordered_values']:
                warnings.append({'code': 'VP10_ORDER_PARTIAL', 'values': order['unordered_values'],
                                 'detail': 'values not listed in axis_order follow at the end of their group, marked unordered'})
            order['OT'] = OrderTexts(locale)
        pr.update(vp10={'T': T, 'predicate': pred, 'states': states, 'hidden_rows': hidden_rows, 'hidden_cols': hidden_cols,
                        'hidden_cells': hidden_cells, 'hide_empty': hide_empty, 'warnings': warnings, 'coverage': cov,
                        'doc_sha': sha_json(doc), 'order': order})
        pr['hidden'], pr['all_empty'] = None, False         # VP-09.2 hiding is replaced by CS-5; its count note is not drawn
        return pr

    # -- drawing --------------------------------------------------------------
    def render(self, pr):
        x = pr['vp10']; T = x['T']; pred = x['predicate']
        order = x['order']; OT = order['OT'] if order else None
        L = pr['L']
        pname = L.pred(pred)                                 # display name as in the VP-09.2 cells (ID unchanged in en)
        blank_line = L.t('axes.legend.blank', 'blank cell = nothing declared for this pair, not "no relation"')
        svg0, drawn = self.axes.render(pr)
        ET.register_namespace('', NS)
        root = ET.fromstring(svg0)
        q = lambda tag: f'{{{NS}}}{tag}'  # noqa: E731
        old_h = int(float(root.get('height')))
        cv = [v for v, _, _ in pr['cv']]
        cw = (GX1-GX0)/max(len(cv), 1)
        rh = 14+(pr['k']+1)*15
        width = max(8, int((cw-16)/6.0))
        rows_y = {}
        for g in root.iter(q('g')):
            if g.get('data-vp09-row'):
                rows_y[g.get('data-vp09-row')] = float(next(g.iter(q('text'))).get('y'))-19
        groups = {g.get('data-vp09-cell'): g for g in root.iter(q('g')) if g.get('data-vp09-cell')}
        scope_txt = lambda s: T.t('cells.scope.'+s, s)  # noqa: E731
        states_drawn = {}
        for (r, c), st in x['states'].items():
            if r not in rows_y or c not in cv:
                continue
            k = _key(r, c)
            y0, x0 = rows_y[r], GX0+cv.index(c)*cw
            states_drawn[k] = st['state']
            g = groups.get(k)
            if g is not None:                                # drawn by VP-09.2: entries (marked, or mixed with another predicate)
                g.set('data-vp10-state', st['state'])
                note = None
                if st['state'] == 'checked':
                    note = T.t('cells.checked_pred', 'none {pred} · checked ({scope})', pred=pname, scope=scope_txt(st['scope']))
                    g.set('data-vp10-scope', st['scope'])
                elif st['state'] == 'unknown':
                    note = T.t('cells.unknown_pred', '{pred} · not surveyed', pred=pname)
                if note:
                    n = sum(1 for _ in g.iter(q('text')))
                    for j, s in enumerate(wrap_sep(note, width)[0]):
                        text(g, fmt(x0+9), fmt(y0+17+(n+j)*15), s, 11, INK, 'bold')
                if order and k in order['feedback_cells']:      # AO-2, AO-3: a text line, no colour or line style
                    n = sum(1 for _ in g.iter(q('text')))
                    g.set('data-vp10-feedback', 'true')
                    text(g, fmt(x0+9), fmt(y0+17+n*15), OT.t('order.feedback', 'feedback'), 11, INK).set('font-style', 'italic')
                continue
            cg = add(root, 'g', **{'data-vp10-cell': k, 'data-vp10-state': st['state']})
            if st['state'] == 'checked':
                cg.set('data-vp10-scope', st['scope'])
                add(cg, 'title').text = f"{r} × {c} · {pred} · {st['scope']} · {st['declaration_id']}"
                e = rect(cg, fmt(x0+3), fmt(y0+3), fmt(cw-6), fmt(rh-6), '#334155', '#FFFFFF', 4)
                e.set('stroke-width', CHECK_STROKE)
                for j, s in enumerate(wrap_sep(T.t('cells.checked', 'none · checked ({scope})', scope=scope_txt(st['scope'])), width)[0]):
                    text(cg, fmt(x0+9), fmt(y0+17+j*15), s, 11, INK, 'bold')
            elif st['state'] == 'unknown':
                add(cg, 'title').text = f'{r} × {c} · {pred} · ' + T.t('cells.unknown_title', 'not surveyed (unknown, not empty)')
                yy = y0+3+HATCH_STEP
                while yy < y0+rh-3:
                    line(cg, fmt(x0+3), fmt(yy), fmt(x0+cw-3), fmt(yy), HATCH_COLOR).set('stroke-width', '1')
                    yy += HATCH_STEP
            else:
                add(cg, 'title').text = f'{r} × {c} · ' + T.t('cells.element', 'element')
                text(cg, fmt(x0+cw/2), fmt(y0+rh/2+4), T.t('cells.element', 'element'), 11, MUTED, anchor='middle')
        # legend (CS-5, CS-7) below the VP-09.2 legend; the picture grows by the added lines
        lines = [T.t('cells.legend.title', 'CELL STATES · VP-10 · declared survey scope, not a verdict')]
        body = [T.t('cells.legend.marked', 'entry = declared statement; "d-x*" = declared in the plan, outside the slice of this input'),
                T.t('cells.legend.checked', '"none · checked" (bold border) = no declared {pred} statement within the declared scope (pair, row or column); not "does not exist"', pred=pname),
                T.t('cells.legend.unknown', 'horizontal hatching = not surveyed: unknown, not empty'),
                T.t('cells.legend.element', '"element" = the element itself (diagonal); no state'),
                T.t('cells.legend.colour', 'states differ by text and lines, not by colour')]
        if not x['coverage']['declared']:
            body.append(T.t('cells.legend.none', 'No coverage is declared in the context: every empty cell is unknown (VP10_COVERAGE_NONE).'))
        if x['hidden_rows']:
            body.append(T.t('cells.legend.hidden_rows', 'hidden rows: {names} (their cells, unknown ones included, are not shown)', names=', '.join(x['hidden_rows'])))
        if x['hidden_cols']:
            body.append(T.t('cells.legend.hidden_cols', 'hidden columns: {names} (their cells, unknown ones included, are not shown)', names=', '.join(x['hidden_cols'])))
        if order:                                           # AO-4
            body.append(OT.t('order.legend', 'declared axis order: rows and columns follow the declared order; "feedback" = entry above the diagonal: '
                                             'the row depends on an element declared later; follows only from the declared order, not a finding about the system'))
            if order['unordered_values']:
                body.append(OT.t('order.legend.unordered', '"unordered" = not in the declared order: {names} (they follow at the end of their group)',
                                 names=', '.join(order['unordered_values'])))
            unordered = set(order['unordered_values'])
            for g in root.iter(q('g')):
                for attr, is_row in (('data-vp09-row', True), ('data-vp09-col', False)):
                    v = g.get(attr)
                    if v in unordered:
                        ts = list(g.iter(q('text')))
                        g.set('data-vp10-unordered', 'true')
                        if is_row:
                            text(g, ts[-1].get('x'), fmt(float(ts[-1].get('y'))+14), OT.t('order.unordered', 'unordered'), 10, MUTED).set('font-style', 'italic')
                        else:
                            text(g, ts[-1].get('x'), '196', OT.t('order.unordered', 'unordered'), 10, MUTED, anchor='middle').set('font-style', 'italic')
        body = [s for b in body for s in wrap_sep(b, 120)[0]]
        leg = next(g for g in root.iter(q('g')) if g.get('data-vp09-legend'))
        for t in leg.iter(q('text')):                       # VP-10 draws no blank cell: the VP-09.2 blank-cell line is replaced in place
            if t.text == blank_line:
                t.text = T.t('cells.legend.no_blank', 'no blank cell: every cell carries a state (see CELL STATES)')
        y = max(float(t.get('y')) for t in leg.iter(q('text')))+34
        lg = add(root, 'g', **{'data-vp10-legend': 'display-only'})
        text(lg, 62, fmt(y), lines[0], 13, MUTED, 'bold')
        for s in body:
            y += 20; text(lg, 70, fmt(y), s, 12, '#334155')
        delta = int(34+20*len(body)+10)
        new_h = old_h+delta
        for el in root.iter():                              # footer and frame follow the new height
            for a in ('y', 'y1', 'y2'):
                v = el.get(a)
                if v is not None and float(v) in (old_h-49, old_h-25):
                    el.set(a, fmt(float(v)+delta))
            if el.tag == q('rect') and el.get('x') == '0' and el.get('y') == '0' and el.get('height') == str(old_h):
                el.set('height', str(new_h))
        root.set('height', str(new_h)); root.set('viewBox', f'0 0 1200 {new_h}')
        root.set('data-printer-profile', PROFILE_101 if order else PROFILE); root.set('data-cube-view', 'cube.cells')
        root.set('data-vp10-predicate', pred)
        for t in root.iter(q('text')):
            if t.text and 'VP-09.2' in t.text and t.get('y') == '75':      # subtitle names the printer
                t.text = t.text.replace('VP-09.2', 'VP-10')
            elif t.text == 'cube.axes' and t.get('y') == str(new_h-25):   # footer view id
                t.text = 'cube.cells'
        meta = add(root, 'metadata', id='vp10-cells-ledger')
        meta.text = cjson(self.ledger(pr, states_drawn))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg, states_drawn

    # -- ledger, audit, report ------------------------------------------------
    @staticmethod
    def ledger(pr, states_drawn):
        x = pr['vp10']
        cells = {}
        for (r, c), st in x['states'].items():
            k = _key(r, c)
            if k in x['hidden_cells']:
                cells[k] = {'state': 'hidden'}
                continue
            cells[k] = {kk: v for kk, v in st.items() if kk != 'entries' or v}
        led = {'profile': PROFILE, 'base_profile': BASE_PROFILE, 'predicate': x['predicate'], 'cells': dict(sorted(cells.items())),
               'hidden_rows': x['hidden_rows'], 'hidden_cols': x['hidden_cols'], 'ignored_declarations': x['coverage']['ignored'],
               'locale': x['T'].record(), 'status': 'declared_unverified',
               'nonimplications': ['truth', 'completeness in the world', 'distance', 'rank', 'score', 'causality', 'time']}
        o = x['order']
        if o:                                               # VP-10.1 keys only with a declared order (0.10.0 bytes unchanged)
            led.update(profile=PROFILE_101, axis_order=o['axis_order'], unordered_values=o['unordered_values'],
                       order_not_in_view=o['not_in_view'], feedback_cells=o['feedback_cells'], order_locale=o['OT'].record())
            led['nonimplications'] = led['nonimplications'] + ['feedback as a finding (it follows from the declared order only)']
        return led

    def report(self, pr, svg, states_drawn):
        inv = []

        def verify(ok, name):
            need(ok, 'VP10_AUDIT', 'VP-10 audit invariant failed: '+name, 'audit')
            inv.append(name)
        q = lambda tag: f'{{{NS}}}{tag}'  # noqa: E731
        root = ET.fromstring(svg)
        verify(no_active_content(root) and not any(el.tag == q('pattern') for el in root.iter()), 'NO_ACTIVE_SVG_CONTENT_NO_PATTERN')
        led = self.ledger(pr, states_drawn)
        blocks = [el for el in root.iter() if el.get('id') == 'vp10-cells-ledger']
        verify(len(blocks) == 1 and blocks[0].text == cjson(led), 'EMBEDDED_LEDGER_MATCH')
        visible = {k: v['state'] for k, v in led['cells'].items() if v['state'] != 'hidden'}
        verify(visible == states_drawn, 'ONE_STATE_PER_DRAWN_CELL')
        sig = {}
        for g in root.iter(q('g')):
            k, st = g.get('data-vp10-cell'), g.get('data-vp10-state')
            if not k:
                continue
            rects = [r.get('stroke-width') for r in g.iter(q('rect'))]
            s = (tuple(sorted(set(rects))), sum(1 for _ in g.iter(q('line'))) > 0, sum(1 for _ in g.iter(q('text'))) > 0)
            sig.setdefault(st, set()).add(s)
        for g in root.iter(q('g')):
            if g.get('data-vp09-cell') and g.get('data-vp10-state') == 'marked':
                sig.setdefault('marked', set()).add((tuple(sorted({r.get('stroke-width') for r in g.iter(q('rect'))})), False, True))
        flat = {st: next(iter(v)) for st, v in sig.items() if len(v) == 1}
        verify(all(len(v) == 1 for v in sig.values()) and len(set(flat.values())) == len(flat), 'STATES_DIFFER_WITHOUT_COLOUR')
        counts = {s: sum(1 for v in led['cells'].values() if v['state'] == s) for s in ('marked', 'checked', 'unknown', 'element', 'hidden')}
        warnings = pr['vp10']['warnings']
        summary = {}
        for w in warnings:
            summary.setdefault(w['code'], {'code': w['code'], 'count': 0})['count'] += 1
        extra = {k: led[k] for k in ('axis_order', 'unordered_values', 'order_not_in_view', 'feedback_cells', 'order_locale') if k in led}
        return {'format': REPORT_FORMAT, 'profile': led['profile'], **extra, 'base_profile': BASE_PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS',
                'view': 'cube.cells', 'rows_axis': pr['rows'], 'cols_axis': pr['cols'], 'granularity': pr['granularity'],
                'predicate': led['predicate'], 'input_sha256': pr['vp10']['doc_sha'], 'svg_sha256': sha_bytes(svg),
                'row_values': [v for v, _, _ in pr['rv']], 'col_values': [v for v, _, _ in pr['cv']],
                'cells': led['cells'], 'state_counts': counts, 'hide_empty': pr['vp10']['hide_empty'],
                'hidden_rows': led['hidden_rows'], 'hidden_cols': led['hidden_cols'], 'hidden_cells': pr['vp10']['hidden_cells'],
                'ignored_declarations': led['ignored_declarations'],
                'declarations_other_predicate': sum(1 for i in led['ignored_declarations'] if i['reason'] == 'other_predicate'),
                'warnings': warnings, 'warning_summary': list(summary.values()), 'invariants_passed': inv, 'locale': led['locale'],
                'content_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['"checked" means no declared statement within the declared survey scope, not that none exists (CV-5).',
                            'Unknown cells are hatched, not blank; hidden values are named.',
                            'No colour, size or position encodes a state or a quantity.']}


def render_cells(doc, rows='Y:referent', cols='Y:referent', granularity='standard', hide_empty=None, locale=None, axis_order=None):
    if isinstance(doc, dict) and doc.get('format') == MATRIX_FORMAT:   # 0.11.0: a statement set; rows and cols are its home (Q-2)
        from .matrix import render_matrix
        return render_matrix(doc, granularity, hide_empty, locale, axis_order)
    p = CellsPrinter()
    pr = p.project(doc, rows, cols, granularity, hide_empty, locale, axis_order)
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg
