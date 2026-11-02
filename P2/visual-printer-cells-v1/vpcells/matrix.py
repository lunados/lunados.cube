"""VP-10 0.11.0: the cell matrix of a declared statement set, drawn without a migration plan (DR-1…DR-8).

An own drawer with the 0.10.x conventions (Q-3): the same four states, the same colour-free audit, the same legend
sections. Rows are subjects, columns are objects (D-6). With an aggregation record, derived entries read
"derived · n sources" and the loss line states what the aggregated view cannot show (DR-5, DR-8).
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from vpaxes.common import BUDGET, HIDE_EMPTY, MUTED, INK, add, line, rect, text, fmt, no_active_content
from .common import (PROFILE_110, REPORT_FORMAT, NS, NOT_EVALUATED, Texts, OrderTexts, MatrixTexts, need, sha_bytes, sha_json, cjson, wrap_sep)
from .statements import normalize_matrix
from .cells import CHECK_STROKE, HATCH_STEP, HATCH_COLOR, _key, _ordered

GX0, GX1, W = 300, 1140, 1200
FOOTER = 'DISPLAY-ONLY · not an ACG validation, warrant or authority decision'


class MatrixPrinter:
    # -- states (CS-1…CS-5 on a statement set) --------------------------------------------------
    def project(self, doc, granularity='standard', hide_empty=None, locale=None, axis_order=None):
        doc = normalize_matrix(doc)
        need(granularity in BUDGET, 'VP10_AXIS_INVALID', 'granularity must be overview|standard|detail')
        need(hide_empty in (None,)+HIDE_EMPTY, 'VP10_AXIS_INVALID', 'hide_empty must be rows|cols|both')
        T, MT = Texts(locale), MatrixTexts(locale)
        pred, cov = doc['predicate'], doc['coverage']
        axis = [(a['id'], a['id'], a['concept_id']) for a in doc['axis']]
        entries = {}
        for e in doc['entries']:
            entries.setdefault((e['row'], e['col']), []).append(e)

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
        order = None
        if axis_order is not None:                           # AO-1…AO-4 as in 0.10.1
            need(isinstance(axis_order, list) and axis_order and all(isinstance(v, str) and v for v in axis_order), 'VP10_ORDER_INVALID',
                 'axis_order must be a non-empty list of display IDs')
            need(len(set(axis_order)) == len(axis_order), 'VP10_ORDER_INVALID',
                 'axis_order lists a value twice: '+', '.join(sorted({v for v in axis_order if axis_order.count(v) > 1})))
            known = {v for v, _, _ in axis}
            axis = _ordered(axis, axis_order)
            order = {'axis_order': list(axis_order), 'not_in_view': [v for v in axis_order if v not in known],
                     'unordered_values': [v for v, _, _ in axis if v not in set(axis_order)], 'OT': OrderTexts(locale)}
        states = {}
        for r, _, _ in axis:
            for c, _, _ in axis:
                ents = entries.get((r, c), [])
                if r == c:
                    states[(r, c)] = {'state': 'element', 'entries': ents}
                    continue
                scope, did = scope_of(r, c)
                if ents:
                    st = {'state': 'marked'}
                elif scope:
                    st = {'state': 'checked', 'scope': scope, 'declaration_id': did}
                else:
                    st = {'state': 'unknown'}
                st['entries'] = ents
                states[(r, c)] = st
        quiet = lambda st: st['state'] in ('unknown', 'element') and not st['entries']  # noqa: E731
        hidden_rows = [r for r, _, _ in axis if all(quiet(states[(r, c)]) for c, _, _ in axis)] if hide_empty in ('rows', 'both') else []
        hidden_cols = [c for c, _, _ in axis if all(quiet(states[(r, c)]) for r, _, _ in axis)] if hide_empty in ('cols', 'both') else []
        rv = [x for x in axis if x[0] not in hidden_rows]
        cv = [x for x in axis if x[0] not in hidden_cols]
        rcap, ccap, _ = BUDGET[granularity]
        need(len(rv) <= rcap and len(cv) <= ccap, 'VP09_AXES_BUDGET', f'{len(rv)} rows / {len(cv)} columns exceed {granularity} ({rcap}/{ccap})',
             'granularity')
        hidden_cells = [_key(r, c) for r, _, _ in axis for c, _, _ in axis if r in hidden_rows or c in hidden_cols]
        warnings = []
        if not cov['declared']:
            warnings.append({'code': 'VP10_COVERAGE_NONE', 'detail': 'no coverage_declarations in the context: every empty cell is unknown (D-9)'})
        elif cov['projected']:
            warnings.append({'code': 'VP10_COVERAGE_NOT_PROJECTED',
                             'detail': 'coverage applies to the source statements, not to the aggregated pairs (Q-9); ignored, empty cells are unknown'})
        for x in cov['ignored']:
            if x['reason'] == 'ref_unknown':
                warnings.append({'code': 'VP10_COVERAGE_REF_UNKNOWN', 'declaration_id': x['declaration_id'],
                                 'detail': 'names a referent that is not on the axes of this statement set; ignored'})
            elif x['reason'] == 'instance_ref':
                warnings.append({'code': 'VP10_COVERAGE_INSTANCE_IGNORED', 'declaration_id': x['declaration_id'],
                                 'detail': 'instance-restricted declaration; a statement-set matrix carries no instance (D-7); ignored'})
        if not doc['entries']:
            warnings.append({'code': 'VP10_PREDICATE_EMPTY', 'detail': f'no statement of {pred} in this input: every off-diagonal cell is unknown or checked'})
        if order:
            pos = {v: i for i, (v, _, _) in enumerate(axis)}
            order['feedback_cells'] = sorted(_key(r, c) for (r, c), st in states.items()
                                             if st['state'] == 'marked' and pos[r] < pos[c] and _key(r, c) not in hidden_cells)
            for v in order['not_in_view']:
                warnings.append({'code': 'VP10_ORDER_NOT_IN_VIEW', 'value': v, 'detail': 'axis_order names a value that is not on the axes; ignored'})
            if order['unordered_values']:
                warnings.append({'code': 'VP10_ORDER_PARTIAL', 'values': order['unordered_values'],
                                 'detail': 'values not listed in axis_order follow at the end of their group, marked unordered'})
        return {'doc': doc, 'T': T, 'MT': MT, 'order': order, 'states': states, 'rv': rv, 'cv': cv, 'axis': axis, 'granularity': granularity,
                'hide_empty': hide_empty, 'hidden_rows': hidden_rows, 'hidden_cols': hidden_cols, 'hidden_cells': hidden_cells,
                'warnings': warnings, 'doc_sha': sha_json(doc)}

    # -- texts ------------------------------------------------------------------------------------
    @staticmethod
    def _entry_text(pr, e):
        s = f"{e['statement_id']} · {e['predicate_id']}"
        if e['origin'] == 'derived':
            s += ' · '+pr['MT'].t('matrix.derived', 'derived · {n} sources', n=len(e['derived_from']))
        return s

    @staticmethod
    def loss_line(pr):
        a = pr['doc']['aggregation']; l = a['loss']
        return pr['MT'].t('matrix.loss', 'aggregation {strategy}: sources {sources} → derived {derived}; passed through {passed}; '
                                         'internal {internal}; suppressed {suppressed}; labels dropped {dropped}',
                          strategy=a['parameters']['strategy'], sources=l['sources'], derived=l['derived'], passed=l['passed_through'],
                          internal=l['internal'], suppressed=l['suppressed'], dropped=l['labels_dropped'])

    # -- drawing ----------------------------------------------------------------------------------
    def render(self, pr):
        doc, T, MT, order = pr['doc'], pr['T'], pr['MT'], pr['order']
        OT = order['OT'] if order else None
        pred, home = doc['predicate'], doc['home']
        pair = f'{home}:referent × {home}:referent'
        rv, cv = pr['rv'], pr['cv']
        cw = (GX1-GX0)/max(len(cv), 1)
        width = max(8, int((cw-16)/6.0))
        cell_lines = {k: [s for e in st['entries'] for s in wrap_sep(self._entry_text(pr, e), width)[0]] for k, st in pr['states'].items()}
        k = max([1]+[len(v) for v in cell_lines.values()])
        rh = 14+(k+1)*15                                     # one line in reserve for notes and the feedback mark, as in 0.10.x
        layout, y, last = [], 214, None
        for val, label, kind in rv:
            if kind != last:
                layout.append(('kind', kind, y)); y += 26; last = kind
            layout.append(('row', (val, label, kind), y)); y += rh
        grid_bottom = y
        # legend (DR-2, DR-5, CS-7)
        legend = [MT.t('matrix.legend.convention', 'row = subject, column = object: a cell lists the declared {pred} statements from the row '
                                                   'referent to the column referent; there is no transposed reading', pred=pred),
                  T.t('cells.legend.no_blank', 'no blank cell: every cell carries a state (see CELL STATES)'),
                  MT.t('matrix.legend.equal', 'equal cell size, no shading: nothing is measured, ranked or placed at a distance')]
        body = [MT.t('matrix.legend.entry', 'entry = declared statement "<ID> · <predicate>" of the statement set; labels are in the ledger'),
                T.t('cells.legend.checked', '"none · checked" (bold border) = no declared {pred} statement within the declared scope (pair, row or column); not "does not exist"', pred=pred),
                T.t('cells.legend.unknown', 'horizontal hatching = not surveyed: unknown, not empty'),
                T.t('cells.legend.element', '"element" = the element itself (diagonal); no state'),
                T.t('cells.legend.colour', 'states differ by text and lines, not by colour')]
        if doc['aggregation']:
            body.append(MT.t('matrix.legend.derived', '"derived · n sources" = aggregated statement from n declared sources ({method}); every source, '
                                                      'internal and suppressed sources are listed in the ledger', method=doc['aggregation']['method_id']))
            body.append(self.loss_line(pr))
        if not doc['coverage']['declared']:
            body.append(T.t('cells.legend.none', 'No coverage is declared in the context: every empty cell is unknown (VP10_COVERAGE_NONE).'))
        elif doc['coverage']['projected']:
            body.append(MT.t('matrix.legend.not_projected', 'The coverage of the context applies to the source statements, not to the aggregated '
                                                            'pairs: it is not applied here (VP10_COVERAGE_NOT_PROJECTED).'))
        if not doc['entries']:
            body.append(MT.t('matrix.legend.empty', 'No {pred} statement in this input (VP10_PREDICATE_EMPTY).', pred=pred))
        if pr['hidden_rows']:
            body.append(T.t('cells.legend.hidden_rows', 'hidden rows: {names} (their cells, unknown ones included, are not shown)', names=', '.join(pr['hidden_rows'])))
        if pr['hidden_cols']:
            body.append(T.t('cells.legend.hidden_cols', 'hidden columns: {names} (their cells, unknown ones included, are not shown)', names=', '.join(pr['hidden_cols'])))
        if order:
            body.append(OT.t('order.legend', 'declared axis order: rows and columns follow the declared order; "feedback" = entry above the diagonal: '
                                             'the row depends on an element declared later; follows only from the declared order, not a finding about the system'))
            if order['unordered_values']:
                body.append(OT.t('order.legend.unordered', '"unordered" = not in the declared order: {names} (they follow at the end of their group)',
                                 names=', '.join(order['unordered_values'])))
        legend = [s for b in legend for s in wrap_sep(b, 120)[0]]
        body = [s for b in body for s in wrap_sep(b, 120)[0]]
        height = int(grid_bottom+40+20*len(legend)+34+20*len(body)+10+90)
        title = f"{doc['set_id']} · {pred}"
        root = ET.Element(f'{{{NS}}}svg', {'version': '1.1', 'width': str(W), 'height': str(height), 'viewBox': f'0 0 {W} {height}', 'role': 'img',
                                           'aria-labelledby': 'svg-title svg-desc', 'data-printer-profile': PROFILE_110,
                                           'data-cube-view': 'cube.cells', 'data-vp10-predicate': pred, 'data-vp10-pair': pair})
        add(root, 'title', id='svg-title').text = title
        add(root, 'desc', id='svg-desc').text = ('Display-only AIAEAO v9.4 matrix of a declared statement set. Geometry and colours cannot imply '
                                                 'verification, permission, admission or semantic validation.')
        rect(root, 0, 0, W, height, '#FFFFFF', '#FFFFFF', 0)
        rect(root, 0, 0, W, 9, '#111827', '#111827', 0)
        text(root, 42, 48, title, 27, '#111827', 'bold')
        text(root, 42, 75, MT.t('matrix.subtitle', 'v9.4 · VP-10 0.11.0 · statement set {set_id} · {pair} · categorical, no distances',
                                set_id=doc['set_id'], pair=pair), 14, '#475569')
        line(root, 42, 93, W-42, 93, '#E2E8F0')
        text(root, 60, 125, MT.t('matrix.header', 'CUBE.CELLS · DECLARED STATEMENTS PER CELL · {pair} · categorical matrix, no ranking, no distance',
                                 pair=pair), 13, MUTED, 'bold')
        unordered = set(order['unordered_values']) if order else set()
        for j, (val, label, kind) in enumerate(cv):
            x = GX0+j*cw
            g = add(root, 'g', **{'data-vp10-col': val})
            add(g, 'title').text = f'{val} · {kind}'
            ls = wrap_sep(label, max(6, int((cw-10)/6.6)))[0][:3]
            for n, s in enumerate(ls):
                text(g, fmt(x+cw/2), fmt(160+n*14+(3-len(ls))*7), s, 11.5, '#1E293B', 'bold', anchor='middle')
            if val in unordered:
                g.set('data-vp10-unordered', 'true')
                text(g, fmt(x+cw/2), '196', OT.t('order.unordered', 'unordered'), 10, MUTED, anchor='middle').set('font-style', 'italic')
            line(root, fmt(x), 200, fmt(x), fmt(grid_bottom), '#E2E8F0')
        line(root, GX1, 200, GX1, fmt(grid_bottom), '#E2E8F0')
        line(root, 60, 204, GX1, 204, '#CBD5E1')
        scope_txt = lambda s: T.t('cells.scope.'+s, s)  # noqa: E731
        cvals = [v for v, _, _ in cv]
        drawn = {}
        for what, payload, y0 in layout:
            if what == 'kind':
                g = add(root, 'g', **{'data-vp10-kind': payload})
                text(g, 70, fmt(y0+17), f'{home} · {payload}', 12, MUTED, 'bold')
                continue
            val, label, kind = payload
            g = add(root, 'g', **{'data-vp10-row': val})
            add(g, 'title').text = f'{val} · {kind}'
            ls = wrap_sep(label, 26)[0][:2]
            for n, s in enumerate(ls):
                text(g, 78, fmt(y0+19+n*14), s, 12, INK, 'bold')
            if val in unordered:
                g.set('data-vp10-unordered', 'true')
                text(g, 78, fmt(y0+19+len(ls)*14), OT.t('order.unordered', 'unordered'), 10, MUTED).set('font-style', 'italic')
            line(root, 60, fmt(y0+rh), GX1, fmt(y0+rh), '#F1F5F9')
            for j, c in enumerate(cvals):
                st = pr['states'][(val, c)]
                key, x0 = _key(val, c), GX0+j*cw
                drawn[key] = st['state']
                cg = add(root, 'g', **{'data-vp10-cell': key, 'data-vp10-state': st['state']})
                if st['state'] == 'marked':
                    add(cg, 'title').text = f'{val} × {c} · ' + ' · '.join(e['statement_id'] for e in st['entries'])
                    rect(cg, fmt(x0+3), fmt(y0+3), fmt(cw-6), fmt(rh-6), '#E2E8F0', '#F8FAFC', 4)
                    lines = cell_lines[(val, c)]
                    for n, s in enumerate(lines):
                        text(cg, fmt(x0+9), fmt(y0+17+n*15), s, 11, '#1E293B')
                    if order and key in order['feedback_cells']:   # AO-2, AO-3
                        cg.set('data-vp10-feedback', 'true')
                        text(cg, fmt(x0+9), fmt(y0+17+len(lines)*15), OT.t('order.feedback', 'feedback'), 11, INK).set('font-style', 'italic')
                elif st['state'] == 'checked':
                    cg.set('data-vp10-scope', st['scope'])
                    add(cg, 'title').text = f"{val} × {c} · {pred} · {st['scope']} · {st['declaration_id']}"
                    e = rect(cg, fmt(x0+3), fmt(y0+3), fmt(cw-6), fmt(rh-6), '#334155', '#FFFFFF', 4)
                    e.set('stroke-width', CHECK_STROKE)
                    for n, s in enumerate(wrap_sep(T.t('cells.checked', 'none · checked ({scope})', scope=scope_txt(st['scope'])), width)[0]):
                        text(cg, fmt(x0+9), fmt(y0+17+n*15), s, 11, INK, 'bold')
                elif st['state'] == 'unknown':
                    add(cg, 'title').text = f'{val} × {c} · {pred} · ' + T.t('cells.unknown_title', 'not surveyed (unknown, not empty)')
                    yy = y0+3+HATCH_STEP
                    while yy < y0+rh-3:
                        line(cg, fmt(x0+3), fmt(yy), fmt(x0+cw-3), fmt(yy), HATCH_COLOR).set('stroke-width', '1')
                        yy += HATCH_STEP
                else:
                    add(cg, 'title').text = f'{val} × {c} · ' + T.t('cells.element', 'element')
                    text(cg, fmt(x0+cw/2), fmt(y0+rh/2+4), T.t('cells.element', 'element'), 11, MUTED, anchor='middle')
        y = grid_bottom+40
        lg = add(root, 'g', **{'data-vp10-legend': 'display-only'})
        text(lg, 62, fmt(y), MT.t('matrix.legend.title', 'LEGEND · declared display conventions · not a verdict'), 13, MUTED, 'bold')
        for s in legend:
            y += 20; text(lg, 70, fmt(y), s, 12, '#334155')
        y += 34
        text(lg, 62, fmt(y), T.t('cells.legend.title', 'CELL STATES · VP-10 · declared survey scope, not a verdict'), 13, MUTED, 'bold')
        for s in body:
            y += 20; text(lg, 70, fmt(y), s, 12, '#334155')
        line(root, 42, height-49, W-42, height-49, '#E2E8F0')
        text(root, 42, height-25, MT.t('matrix.footer', FOOTER), 13, '#475569')
        text(root, W-42, height-25, 'cube.cells', 12, '#64748B', anchor='end')
        add(root, 'metadata', id='vp10-cells-ledger').text = cjson(self.ledger(pr))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg, drawn

    # -- ledger, audit, report --------------------------------------------------------------------
    @staticmethod
    def ledger(pr):
        doc = pr['doc']
        cells = {}
        for (r, c), st in pr['states'].items():
            k = _key(r, c)
            if k in pr['hidden_cells']:
                cells[k] = {'state': 'hidden'}
                continue
            cells[k] = {kk: v for kk, v in st.items() if kk != 'entries'}
            if st['entries']:
                cells[k]['entries'] = [e['statement_id'] for e in st['entries']]
        led = {'profile': PROFILE_110, 'set_id': doc['set_id'], 'predicate': doc['predicate'], 'home': doc['home'],
               'convention': 'row = subject, column = object', 'cells': dict(sorted(cells.items())), 'entries': doc['entries'],
               'hidden_rows': pr['hidden_rows'], 'hidden_cols': pr['hidden_cols'], 'ignored_declarations': doc['coverage']['ignored'],
               'aggregation': None, 'sources': doc['sources'], 'locale': pr['T'].record(), 'matrix_locale': pr['MT'].record(),
               'status': 'declared_unverified',
               'nonimplications': ['truth', 'completeness in the world', 'distance', 'rank', 'score', 'causality', 'time']}
        a = doc['aggregation']
        if a:
            led['aggregation'] = {**a, 'derived': {e['statement_id']: e['derived_from'] for e in doc['entries'] if e['origin'] == 'derived'}}
            led['nonimplications'] = led['nonimplications'] + ['a derived statement as an observed relation (it follows from its declared sources only)']
        o = pr['order']
        if o:
            led.update(axis_order=o['axis_order'], unordered_values=o['unordered_values'], order_not_in_view=o['not_in_view'],
                       feedback_cells=o['feedback_cells'], order_locale=o['OT'].record())
            led['nonimplications'] = led['nonimplications'] + ['feedback as a finding (it follows from the declared order only)']
        return led

    def report(self, pr, svg, drawn):
        inv = []

        def verify(ok, name):
            need(ok, 'VP10_AUDIT', 'VP-10 audit invariant failed: '+name, 'audit')
            inv.append(name)
        q = lambda tag: f'{{{NS}}}{tag}'  # noqa: E731
        root = ET.fromstring(svg)
        verify(no_active_content(root) and not any(el.tag == q('pattern') for el in root.iter()), 'NO_ACTIVE_SVG_CONTENT_NO_PATTERN')
        led = self.ledger(pr)
        blocks = [el for el in root.iter() if el.get('id') == 'vp10-cells-ledger']
        verify(len(blocks) == 1 and blocks[0].text == cjson(led), 'EMBEDDED_LEDGER_MATCH')
        visible = {k: v['state'] for k, v in led['cells'].items() if v['state'] != 'hidden'}
        verify(visible == drawn, 'ONE_STATE_PER_DRAWN_CELL')
        sig = {}
        for g in root.iter(q('g')):
            k, st = g.get('data-vp10-cell'), g.get('data-vp10-state')
            if k:
                s = (tuple(sorted({r.get('stroke-width') for r in g.iter(q('rect'))})), any(True for _ in g.iter(q('line'))),
                     any(True for _ in g.iter(q('text'))))
                sig.setdefault(st, set()).add(s)
        flat = {st: next(iter(v)) for st, v in sig.items() if len(v) == 1}
        verify(all(len(v) == 1 for v in sig.values()) and len(set(flat.values())) == len(flat), 'STATES_DIFFER_WITHOUT_COLOUR')
        counts = {s: sum(1 for v in led['cells'].values() if v['state'] == s) for s in ('marked', 'checked', 'unknown', 'element', 'hidden')}
        summary = {}
        for w in pr['warnings']:
            summary.setdefault(w['code'], {'code': w['code'], 'count': 0})['count'] += 1
        extra = {k: led[k] for k in ('axis_order', 'unordered_values', 'order_not_in_view', 'feedback_cells', 'order_locale') if k in led}
        doc = pr['doc']
        return {'format': REPORT_FORMAT, 'profile': PROFILE_110, **extra, 'reference_version': 'v9.4', 'render_status': 'PASS',
                'view': 'cube.cells', 'source': 'statement_set', 'set_id': doc['set_id'], 'home': doc['home'],
                'rows_axis': f"{doc['home']}:referent", 'cols_axis': f"{doc['home']}:referent", 'granularity': pr['granularity'],
                'predicate': doc['predicate'], 'input_sha256': pr['doc_sha'], 'svg_sha256': sha_bytes(svg),
                'row_values': [v for v, _, _ in pr['rv']], 'col_values': [v for v, _, _ in pr['cv']],
                'cells': led['cells'], 'state_counts': counts, 'hide_empty': pr['hide_empty'],
                'hidden_rows': led['hidden_rows'], 'hidden_cols': led['hidden_cols'], 'hidden_cells': pr['hidden_cells'],
                'ignored_declarations': led['ignored_declarations'], 'aggregation': led['aggregation'],
                'loss_line': self.loss_line(pr) if doc['aggregation'] else None,
                'warnings': pr['warnings'], 'warning_summary': list(summary.values()), 'invariants_passed': inv,
                'locale': led['locale'], 'matrix_locale': led['matrix_locale'], 'content_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Rows are subjects, columns are objects; there is no transposed reading (D-6).',
                            '"checked" means no declared statement within the declared survey scope, not that none exists (CV-5).',
                            'A derived entry follows from its declared sources under the chosen strategy only; nothing is recomputed by the Cube.',
                            'No colour, size or position encodes a state or a quantity.']}


def render_matrix(doc, granularity='standard', hide_empty=None, locale=None, axis_order=None):
    p = MatrixPrinter()
    pr = p.project(doc, granularity, hide_empty, locale, axis_order)
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg
