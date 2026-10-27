"""VP-09 view `cube.axes` (AX, CM, AD): a categorical matrix of declared statements over two declared axes.

Display only. No distance, position, shade, rank or numeric vector encodes anything (`never_infer`);
a blank cell asserts nothing; membership uses declared fields only (no transitive closure).
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from .common import (PROFILE, AXES, RESERVED, PAIRS, BUDGET, X_DIMS, LENS_OF, KIND_ORDER, RULES, LEVELS, NOT_EVALUATED, NS,
                     STROKE, INK, MUTED, Printer, add, line, rect, text, excerpt, cjson, fmt, sha_bytes, sha_json, no_active_content,
                     need, wrap_words, kind_label)
from .source import normalize, method_order

REPORT_FORMAT = 'aiaeao.cube.vp09-axes-report/1'
GX0, GX1 = 300, 1140


def letter(axis):
    return axis.split(':')[0]


def check_pair(rows, cols):
    for a in (rows, cols):
        need(isinstance(a, str), 'VP09_AXIS_INVALID', 'axis must be a string')
        need(letter(a) not in RESERVED, 'VP09_AXIS_INVALID', f'axis {a} is reserved until a declared source exists (D-6)')
        need(a in AXES, 'VP09_AXIS_INVALID', f'axis {a!r} outside X | Y:kind | Y:referent | Z:kind | Z:referent | T | F (AX-1)')
    pair = {letter(rows), letter(cols)}
    need(not (letter(rows) == letter(cols) and letter(rows) != 'X'), 'VP09_AXIS_INVALID', 'the same axis twice (only X × X is a pair, D-2)')
    need(pair in PAIRS, 'VP09_AXIS_INVALID', f'pair {rows} × {cols} is not in the declared pair list (D-2)')
    return frozenset(pair)


class Model:
    """Values and cell membership for one input (independent of granularity)."""

    def __init__(self, doc):
        self.src, self.bindings, self.items, self.v = normalize(doc)
        src = self.src
        self.cells = src['cells']
        self.steps = src['steps']
        self.sindex = {s['id']: k for k, s in enumerate(self.steps)}
        self.facets = src['facet_bindings']
        self.cellmap = {c['id']: c for c in self.cells}
        seq = src.get('layer_sequence')
        self.pos = {i: k for k, i in enumerate(seq)} if seq else {i: k for k, i in enumerate(self.items)}

    # -- values (AX-3) -----------------------------------------------------
    def values(self, axis):
        a = letter(axis)
        if a == 'T':
            return [(s['id'], s['label'], None) for s in self.steps]
        if a == 'X':
            need(self.facets, 'VP09_AXIS_EMPTY', 'X needs declared facet bindings; the source declares none (AX-4)')
            return [(d, f'{g} {n}', None) for d, g, n in X_DIMS]
        if a == 'F':
            ms = method_order(self.bindings)
            need(ms, 'VP09_AXIS_EMPTY', 'F needs declared method bindings (P1.11 via vpaxes from-plan); the input declares none (AQ-3)')
            return [(m, m, None) for m in ms]
        its = [i for i in self.items.values() if i['home'] == a]
        need(its, 'VP09_AXIS_EMPTY', f'no referent of home {a} in the source')
        order = KIND_ORDER[a]
        kinds = sorted(dict.fromkeys(i['kind'] for i in its), key=lambda k: (order.index(k) if k in order else len(order), 0))
        if axis.endswith(':kind'):
            return [(k, kind_label(k), k) for k in kinds]
        out = []
        for k in kinds:
            for i in sorted((i for i in its if i['kind'] == k), key=lambda i: self.pos[i['id']]):
                out.append((i['id'], i['label'], k))
        return out

    def proj(self, axis, item_id):
        it = self.items.get(item_id)
        if it is None or it['home'] != letter(axis):
            return None
        return it['kind'] if axis.endswith(':kind') else item_id

    # -- membership (CM) ---------------------------------------------------
    def entries(self, rows, cols):
        """{(row value, col value): [entries]} in declared order; canonical pair then oriented."""
        pair = check_pair(rows, cols)
        out = {}

        def emit(a_val, b_val, entry, swap):
            if a_val is None or b_val is None:
                return
            key = (b_val, a_val) if swap else (a_val, b_val)
            lst = out.setdefault(key, [])
            if entry not in lst:
                lst.append(entry)
        la, lb = letter(rows), letter(cols)
        if pair in ({'Z', 'T'}, {'Y', 'T'}):
            ax = rows if la != 'T' else cols
            swap = la == 'T'
            for c in self.cells:
                for s in c['steps']:
                    for it in (c['row'], c['object']):
                        emit(self.proj(ax, it), s, c['id'], swap)
            if pair == {'Y', 'T'}:
                for t in self.src['transitions']:
                    for x in t['retires']:
                        emit(self.proj(ax, x), t['at'], f"retired by {t['id']}", swap)
                    for x in t['introduces']:
                        emit(self.proj(ax, x), t['at'], f"introduced by {t['id']}", swap)
        elif pair == {'Y', 'Z'}:
            ay, az = (rows, cols) if la == 'Y' else (cols, rows)
            swap = la == 'Z'
            for c in self.cells:
                a, b = c['row'], c['object']
                for y, z in ((a, b), (b, a)):
                    if self.items[y]['home'] == 'Y' and self.items[z]['home'] == 'Z':
                        emit(self.proj(ay, y), self.proj(az, z), f"{c['id']} · {c['predicate_id']}", swap)
        elif pair == {'X'}:
            lenses = {}
            order = []
            for f in self.facets:
                key = f['target_id']
                if key not in lenses:
                    lenses[key] = set(); order.append(key)
                lenses[key].add(f['lens'])
            for key in order:
                for d1, _, _ in X_DIMS:
                    for d2, _, _ in X_DIMS:
                        if LENS_OF[d1] in lenses[key] and LENS_OF[d2] in lenses[key]:
                            emit(d1, d2, key, False)
        elif pair == {'X', 'Z'}:
            az = cols if la == 'X' else rows
            swap = la == 'Z'
            dim = {LENS_OF[d]: d for d, _, _ in X_DIMS}
            for f in self.facets:
                d = dim.get(f['lens'])
                if f['target_kind'] in ('row', 'object'):
                    emit(d, self.proj(az, f['target_id']), f"{f['target_id']}: {f['note']}", swap)
                else:
                    c = self.cellmap[f['target_id']]
                    for it in dict.fromkeys((c['row'], c['object'])):
                        emit(d, self.proj(az, it), f"{c['id']}: {f['note']}", swap)
        elif pair == {'F', 'Z'}:
            az = cols if la == 'F' else rows
            swap = la == 'Z'
            for b in self.bindings:
                for role, ref in b['arguments'].items():
                    emit(b['method_id'], self.proj(az, ref), f"{b['owner']} ({role})", swap)
        elif pair == {'F', 'T'}:
            swap = la == 'T'
            trs = {t['id']: t for t in self.src['transitions']}
            for b in self.bindings:
                step = trs[b['owner']]['at'] if b['owner_kind'] == 'transition' else self.cellmap[b['owner']]['steps'][-1]
                emit(b['method_id'], step, b['owner'], swap)
        return pair, out


class AxesPrinter:
    def __init__(self):
        self.base = Printer()

    def project(self, doc, rows, cols, granularity='standard', row_subset=None, col_subset=None, budget_check=True):
        need(granularity in LEVELS, 'VP09_AXES_BUDGET', 'granularity must be overview|standard|detail', 'granularity')
        check_pair(rows, cols)
        m = Model(doc)
        rv, cv = m.values(rows), m.values(cols)
        pair, cells = m.entries(rows, cols)
        if row_subset is not None:
            rv = [x for x in rv if x[0] in row_subset]
        if col_subset is not None:
            cv = [x for x in cv if x[0] in col_subset]
        rcap, ccap, kcap = BUDGET[granularity]
        if budget_check:
            need(len(rv) <= rcap and len(cv) <= ccap, 'VP09_AXES_BUDGET',
                 f'{len(rv)} rows / {len(cv)} columns exceed {granularity} ({rcap}/{ccap}); use print-panels (D-9)', 'granularity')
        return {'model': m, 'pair': pair, 'rows': rows, 'cols': cols, 'rv': rv, 'cv': cv, 'cells': cells, 'k': kcap,
                'granularity': granularity}

    # layout --------------------------------------------------------------
    def _lines(self, entries, width_chars, k):
        """AD-3: visible entries are whole (wrapped), never truncated; the rest goes to `+n more`."""
        out, shown = [], 0
        for e in entries:
            ls = wrap_words(e, width_chars)
            room = k-len(out)  # the `+n more` line has its own slot (row height k+1 lines)
            if len(ls) > room:
                break
            out += [(e, j, s) for j, s in enumerate(ls)]
            shown += 1
        return out, shown

    def render(self, pr):
        m = pr['model']
        rv, cv, cells, k = pr['rv'], pr['cv'], pr['cells'], pr['k']
        ncols = len(cv)
        cw = (GX1-GX0)/ncols
        rh = 14+(k+1)*15
        kind_rows = pr['rows'].endswith(':referent')
        layout, y = [], 214
        last_kind = None
        for val, label, kind in rv:
            if kind_rows and kind != last_kind:
                layout.append(('kind', kind, y)); y += 26; last_kind = kind
            layout.append(('row', (val, label, kind), y)); y += rh
        grid_bottom = y
        rule = RULES[pr['pair']]
        legend_lines = wrap_words('Membership: '+rule, 120)
        height = int(grid_bottom+50+(len(legend_lines)+4)*20+60)
        pair_txt = f"{pr['rows']} × {pr['cols']}"
        root = self.base._root({'view_id': 'cube.axes', 'title': excerpt(m.src['title']+' · '+pair_txt, 78),
                                'subtitle': excerpt(f"v9.4 · VP-09 · declared axes {pair_txt} · {pr['granularity']} · categorical, no distances", 105)},
                               height)
        root.set('data-printer-profile', PROFILE)
        root.set('data-cube-view', 'cube.axes')
        root.set('data-vp09-pair', pair_txt)
        text(root, 60, 125, 'CUBE.AXES · DECLARED STATEMENTS PER CELL · categorical matrix, no ranking, no distance', 13, MUTED, 'bold')
        # column headers (AD-2)
        for j, (val, label, kind) in enumerate(cv):
            x = GX0+j*cw
            g = add(root, 'g', **{'data-vp09-col': val})
            add(g, 'title').text = f'{val} · {label}'
            ls = wrap_words(label, max(6, int((cw-10)/6.6)))[:3]
            for n, s in enumerate(ls):
                text(g, fmt(x+cw/2), fmt(160+n*14+(3-len(ls))*7), s, 11.5, '#1E293B', 'bold', anchor='middle')
            line(root, fmt(x), 200, fmt(x), fmt(grid_bottom), '#E2E8F0')
        line(root, GX1, 200, GX1, fmt(grid_bottom), '#E2E8F0')
        line(root, 60, 204, GX1, 204, '#CBD5E1')
        drawn = []
        for kind_, payload, y0 in layout:
            if kind_ == 'kind':
                g = add(root, 'g', **{'data-vp09-kind': payload})
                anchor = next((m.items[v]['anchor_id'] for v, _, kk in rv if kk == payload), None)
                if anchor:
                    text(g, 70, fmt(y0+18), self.base.by_id[anchor]['unicode'], 14, INK, anchor='middle', glyph=True)
                text(g, 86, fmt(y0+17), f"{letter(pr['rows'])} · {kind_label(payload)}", 12, MUTED, 'bold')
                continue
            val, label, kind = payload
            g = add(root, 'g', **{'data-vp09-row': val})
            add(g, 'title').text = f'{val} · {label}'
            gx = 70
            if letter(pr['rows']) in ('Y', 'Z'):
                it = m.items.get(val) if pr['rows'].endswith(':referent') else next((i for i in m.items.values() if i['kind'] == val), None)
                if it:
                    text(g, 78, fmt(y0+20), self.base.by_id[it['anchor_id']]['unicode'], 14, INK, anchor='middle', glyph=True)
                gx = 92
            for n, s in enumerate(wrap_words(label, 26)[:2]):
                text(g, gx, fmt(y0+19+n*14), s, 12, INK, 'bold')
            line(root, 60, fmt(y0+rh), GX1, fmt(y0+rh), '#F1F5F9')
            for j, (cval, _, _) in enumerate(cv):
                ents = cells.get((val, cval), [])
                if not ents:
                    continue                                # AD-4: blank cell asserts nothing; no glyph, no fill
                x = GX0+j*cw
                cg = add(root, 'g', **{'data-vp09-cell': f'{val}|{cval}', 'data-vp09-count': str(len(ents))})
                add(cg, 'title').text = f'{val} × {cval} · ' + ' · '.join(ents)
                rect(cg, fmt(x+3), fmt(y0+3), fmt(cw-6), fmt(rh-6), '#E2E8F0', '#F8FAFC', 4)
                lines, shown = self._lines(ents, max(8, int((cw-16)/6.0)), k)
                for n, (_, _, s) in enumerate(lines):
                    text(cg, fmt(x+9), fmt(y0+17+n*15), s, 11, '#1E293B')
                if shown < len(ents):
                    text(cg, fmt(x+9), fmt(y0+17+len(lines)*15), f'+{len(ents)-shown} more', 11, MUTED, 'bold')
                drawn.append((val, cval, shown, len(ents)))
        # legend (AD-4)
        y = grid_bottom+40
        lg = add(root, 'g', **{'data-vp09-legend': 'display-only'})
        text(lg, 62, fmt(y), 'LEGEND · declared display conventions · not a verdict', 13, MUTED, 'bold')
        for s in legend_lines:
            y += 20; text(lg, 70, fmt(y), s, 12, '#334155')
        for s in ('blank cell = nothing declared for this pair, not "no relation"',
                  '+n more = number of further declared entries in the cell (a cardinality, not a score); full list in the ledger',
                  'equal cell size, no shading: nothing is measured, ranked or placed at a distance'):
            y += 20; text(lg, 70, fmt(y), s, 12, '#334155')
        meta = add(root, 'metadata', id='vp09-axes-ledger')
        meta.text = cjson(self.ledger(pr))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg, drawn

    @staticmethod
    def ledger(pr):
        rset = {v for v, _, _ in pr['rv']}; cset = {v for v, _, _ in pr['cv']}
        cells = {f'{r}|{c}': e for (r, c), e in pr['cells'].items() if r in rset and c in cset}
        return {'profile': PROFILE, 'rows_axis': pr['rows'], 'cols_axis': pr['cols'], 'granularity': pr['granularity'],
                'row_values': [v for v, _, _ in pr['rv']], 'col_values': [v for v, _, _ in pr['cv']], 'cells': cells,
                'status': 'declared_unverified', 'nonimplications': ['truth', 'distance', 'rank', 'score', 'causality', 'time']}

    def report(self, pr, svg, drawn):
        inv = []

        def verify(ok, name):
            need(ok, 'VP09_AUDIT', 'VP-09 audit invariant failed: '+name, 'audit')
            inv.append(name)
        root = ET.fromstring(svg)
        verify(no_active_content(root), 'NO_ACTIVE_SVG_CONTENT')
        blocks = [x for x in root.iter() if x.get('id') == 'vp09-axes-ledger']
        verify(len(blocks) == 1 and blocks[0].text == cjson(self.ledger(pr)), 'EMBEDDED_LEDGER_MATCH')
        led = self.ledger(pr)
        groups = [g for g in root.iter(f'{{{NS}}}g') if g.get('data-vp09-cell')]
        verify(sorted(g.get('data-vp09-cell') for g in groups) == sorted(led['cells']), 'DRAWN_CELLS_MATCH')
        sizes = {(r.get('width'), r.get('height'), r.get('fill')) for g in groups for r in g.iter(f'{{{NS}}}rect')}
        verify(len(sizes) <= 1, 'EQUAL_CELLS_UNIFORM_FILL')
        warnings = [{'code': 'VP09_CELL_OVERFLOW', 'row': r, 'col': c, 'count': n, 'shown': s} for r, c, s, n in drawn if s < n]
        units = sorted(f'{k}|{e}' for k, es in led['cells'].items() for e in es)
        return {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS', 'view': 'cube.axes',
                'rows_axis': pr['rows'], 'cols_axis': pr['cols'], 'granularity': pr['granularity'],
                'source_sha256': sha_json(pr['model'].src), 'svg_sha256': sha_bytes(svg),
                'row_values': led['row_values'], 'col_values': led['col_values'], 'cells': led['cells'], 'units': units,
                'counts': {'rows': len(pr['rv']), 'cols': len(pr['cv']), 'nonempty_cells': len(led['cells']), 'entries': len(units)},
                'warnings': warnings, 'invariants_passed': inv, 'content_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Cells list declared statements only; a blank cell asserts nothing.',
                            'No size, position or shade encodes a quantity; nothing is ranked.',
                            'Step columns are a declared step order, not a time scale.']}


def render_axes(doc, rows, cols, granularity='standard'):
    p = AxesPrinter()
    pr = p.project(doc, rows, cols, granularity)
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg
