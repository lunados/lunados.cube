"""VP-09 view `cube.axes` (AX, CM, AD): a categorical matrix of declared statements over two declared axes.

Display only. No distance, position, shade, rank or numeric vector encodes anything (`never_infer`);
a blank cell asserts nothing; membership uses declared fields only (no transitive closure).
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from .common import (PROFILE, P091, PAIRS_091, RULES_091, AXES, RESERVED, PAIRS, BUDGET, X_DIMS, LENS_OF, KIND_ORDER, RULES, LEVELS, NOT_EVALUATED, NS,
                     STROKE, INK, MUTED, Printer, add, line, rect, text, excerpt, cjson, fmt, sha_bytes, sha_json, no_active_content,
                     need, wrap_words, kind_label)
from .source import normalize, method_order, profile_of

REPORT_FORMAT = 'aiaeao.cube.vp09-axes-report/1'
GX0, GX1 = 300, 1140


def letter(axis):
    return axis.split(':')[0]


def check_pair(rows, cols, v91=False):
    for a in (rows, cols):
        need(isinstance(a, str), 'VP09_AXIS_INVALID', 'axis must be a string')
        need(letter(a) not in RESERVED, 'VP09_AXIS_INVALID', f'axis {a} is reserved until a declared source exists (D-6)')
        need(a in AXES, 'VP09_AXIS_INVALID', f'axis {a!r} outside X | Y:kind | Y:referent | Z:kind | Z:referent | T | F (AX-1)')
    pair = {letter(rows), letter(cols)}
    need(not (letter(rows) == letter(cols) and letter(rows) != 'X'), 'VP09_AXIS_INVALID', 'the same axis twice (only X × X is a pair, D-2)')
    need(pair in (PAIRS_091 if v91 else PAIRS), 'VP09_AXIS_INVALID', f'pair {rows} × {cols} is not in the declared pair list (D-2)')
    return frozenset(pair)


class Model:
    """Values and cell membership for one input (independent of granularity)."""

    def __init__(self, doc):
        self.src, self.bindings, self.items, self.v = normalize(doc)
        self.profile = profile_of(doc)
        self.v91 = self.profile == P091
        self.local = doc['local_methods'] if self.v91 else []
        self.dropped = doc['dropped_arguments'] if self.v91 else []
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
            if self.v91:                                     # D-4: no binding declared yet is a normal plan state
                return [(m, m, None) for m in ms]
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
        pair = check_pair(rows, cols, self.v91)
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
        elif pair == {'F', 'Z'} or pair == {'F', 'Y'}:
            az = cols if la == 'F' else rows
            swap = la != 'F'
            for b in self.bindings:
                for role, ref in b['arguments'].items():
                    emit(b['method_id'], self.proj(az, ref), f"{b['owner']} · {role}" if self.v91 else f"{b['owner']} ({role})", swap)
        elif pair == {'F', 'T'}:
            swap = la == 'T'
            for b in self.bindings:
                emit(b['method_id'], self.step_of(b), b['owner'], swap)
        return pair, out

    def step_of(self, b):
        if b['owner_kind'] == 'transition':
            return next(t['at'] for t in self.src['transitions'] if t['id'] == b['owner'])
        return b['step'] if self.v91 else self.cellmap[b['owner']]['steps'][-1]   # D-3 in 0.9.1; 0.9.0: last own step

    # -- binding ledger (VP-09.1 FL) -----------------------------------------
    def binding_units(self, rows, cols):
        """FL-1/FL-2: every (binding, role) unit — or (binding, *) in F × T — with exactly one state."""
        la = letter(rows)
        other = cols if la == 'F' else rows
        key = (lambda m, v: f'{m}|{v}') if la == 'F' else (lambda m, v: f'{v}|{m}')
        steps = {s['id'] for s in self.steps}
        out = []
        for i, b in enumerate(self.bindings):
            base = {'owner_kind': b['owner_kind'], 'owner': b['owner'], 'method_id': b['method_id'], 'declaration_ref': b['declaration_ref']}
            if letter(other) == 'T':
                st = self.step_of(b)
                u = dict(base, unit=f'b{i}', role='*', step=st)
                if b['owner_kind'] == 'dependency':
                    u['step_rule'] = b['step_rule']
                u.update({'state': 'drawn', 'cell': key(b['method_id'], st)} if st in steps else {'state': 'out_of_slice', 'reason': 'step_out_of_slice'})
                out.append(u)
                continue
            for role, ref in b['arguments'].items():
                v = self.proj(other, ref)
                u = dict(base, unit=f'b{i}.{role}', role=role, ref=ref)
                u.update({'state': 'drawn', 'cell': key(b['method_id'], v)} if v is not None else
                         {'state': 'off_axis', 'home': self.items[ref]['home']})
                out.append(u)
        seen = set()
        for j, x in enumerate(self.dropped):
            base = {'owner_kind': x['owner_kind'], 'owner': x['owner'], 'method_id': x['method_id'], 'declaration_ref': x['declaration_ref'],
                    'state': 'out_of_slice', 'reason': x['reason']}
            if letter(other) == 'T':
                if x['reason'] == 'owner_out_of_slice' and x['declaration_ref'] not in seen:   # the binding itself, once
                    seen.add(x['declaration_ref'])
                    out.append(dict(base, unit=f'x{j}', role='*'))
                continue
            out.append(dict(base, unit=f'x{j}.{x["role"]}', role=x['role'], ref=x['ref']))
        return out


class AxesPrinter:
    def __init__(self):
        self.base = Printer()

    def project(self, doc, rows, cols, granularity='standard', row_subset=None, col_subset=None, budget_check=True):
        need(granularity in LEVELS, 'VP09_AXES_BUDGET', 'granularity must be overview|standard|detail', 'granularity')
        v91 = profile_of(doc) == P091
        check_pair(rows, cols, v91)
        m = Model(doc)
        rv, cv = m.values(rows), m.values(cols)
        pair, cells = m.entries(rows, cols)
        full = row_subset is None and col_subset is None
        if row_subset is not None:
            rv = [x for x in rv if x[0] in row_subset]
        if col_subset is not None:
            cv = [x for x in cv if x[0] in col_subset]
        rcap, ccap, kcap = BUDGET[granularity]
        if budget_check:
            need(len(rv) <= rcap and len(cv) <= ccap, 'VP09_AXES_BUDGET',
                 f'{len(rv)} rows / {len(cv)} columns exceed {granularity} ({rcap}/{ccap}); use print-panels (D-9)', 'granularity')
        pr = {'model': m, 'pair': pair, 'rows': rows, 'cols': cols, 'rv': rv, 'cv': cv, 'cells': cells, 'k': kcap,
              'granularity': granularity}
        if v91:
            pr['profile'], pr['full'] = P091, full
            pr['fpair'] = 'F' in pair
            if pr['fpair']:
                units = m.binding_units(rows, cols)
                rset = {v for v, _, _ in rv}; cset = {v for v, _, _ in cv}
                pr['units_b'] = units
                pr['drawn_here'] = sorted(u['unit'] for u in units if u['state'] == 'drawn' and tuple(u['cell'].split('|', 1))[0] in rset
                                          and u['cell'].split('|', 1)[1] in cset)
        return pr

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
        v91 = pr.get('profile') == P091
        rule = (RULES_091 if v91 else RULES)[pr['pair']]
        legend_lines = wrap_words('Membership: '+rule, 120)
        if v91:
            legend_lines += self._notes091(pr)
        height = int(grid_bottom+50+(len(legend_lines)+4)*20+60)
        pair_txt = f"{pr['rows']} × {pr['cols']}"
        root = self.base._root({'view_id': 'cube.axes', 'title': excerpt(m.src['title']+' · '+pair_txt, 78),
                                'subtitle': excerpt(f"v9.4 · VP-09{'.1' if v91 else ''} · declared axes {pair_txt} · {pr['granularity']} · categorical, no distances", 105)},
                               height)
        root.set('data-printer-profile', pr.get('profile', PROFILE))
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
    def _notes091(pr):
        """Legend lines of 0.9.1: what the F view does not show, as counts of declared units (FL-2)."""
        out = []
        if pr['fpair'] and not pr['model'].bindings:
            out.append('No method binding is declared in the input: the F axis is empty (VP09_METHODS_NONE), not a statement about the plan.')
        if pr['fpair']:
            off = [u for u in pr['units_b'] if u['state'] == 'off_axis']
            out_ = [u for u in pr['units_b'] if u['state'] == 'out_of_slice']
            for home in sorted({u['home'] for u in off}):
                n = sum(u['home'] == home for u in off)
                out.append(f'{n} binding argument(s) name a referent of home {home}: not a column of this view (see F × {home}); listed in the ledger.')
            if out_:
                out.append(f'{len(out_)} binding unit(s) lie outside the plan slice of this input; listed in the ledger.')
        return [x for line in out for x in wrap_words(line, 120)]

    @staticmethod
    def ledger(pr):
        rset = {v for v, _, _ in pr['rv']}; cset = {v for v, _, _ in pr['cv']}
        cells = {f'{r}|{c}': e for (r, c), e in pr['cells'].items() if r in rset and c in cset}
        led = {'profile': pr.get('profile', PROFILE), 'rows_axis': pr['rows'], 'cols_axis': pr['cols'], 'granularity': pr['granularity'],
               'row_values': [v for v, _, _ in pr['rv']], 'col_values': [v for v, _, _ in pr['cv']], 'cells': cells,
               'status': 'declared_unverified', 'nonimplications': ['truth', 'distance', 'rank', 'score', 'causality', 'time']}
        if pr.get('profile') == P091 and pr['fpair']:
            led['binding_units'] = pr['drawn_here']
            if pr['full']:
                led['binding_ledger'] = pr['units_b']
                led['binding_coverage'] = binding_coverage(pr['units_b'], pr['drawn_here'])
        return led

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
        extra = {}
        if pr.get('profile') == P091 and pr['fpair']:
            if not pr['model'].bindings:
                warnings.append({'code': 'VP09_METHODS_NONE', 'detail': 'the input declares no method binding (D-4)'})
            if pr['full']:
                warnings += binding_warnings(pr['units_b'])
                verify(led['binding_coverage']['status'] == 'COMPLETE', 'BINDING_LEDGER_COMPLETE')
            extra = {k: led[k] for k in ('binding_units', 'binding_ledger', 'binding_coverage') if k in led}
        return {'format': REPORT_FORMAT, 'profile': pr.get('profile', PROFILE), **extra, 'reference_version': 'v9.4', 'render_status': 'PASS', 'view': 'cube.axes',
                'rows_axis': pr['rows'], 'cols_axis': pr['cols'], 'granularity': pr['granularity'],
                'source_sha256': sha_json(pr['model'].src), 'svg_sha256': sha_bytes(svg),
                'row_values': led['row_values'], 'col_values': led['col_values'], 'cells': led['cells'], 'units': units,
                'counts': {'rows': len(pr['rv']), 'cols': len(pr['cv']), 'nonempty_cells': len(led['cells']), 'entries': len(units)},
                'warnings': warnings, 'invariants_passed': inv, 'content_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Cells list declared statements only; a blank cell asserts nothing.',
                            'No size, position or shade encodes a quantity; nothing is ranked.',
                            'Step columns are a declared step order, not a time scale.']}


def binding_coverage(units, drawn_units):
    """FL-2/FL-3: every unit has exactly one state; `drawn` must equal the units drawn in the rendering(s)."""
    keys = [u['unit'] for u in units]
    drawn = sorted(u['unit'] for u in units if u['state'] == 'drawn')
    n = {s: sum(u['state'] == s for u in units) for s in ('drawn', 'off_axis', 'out_of_slice')}
    ok = len(set(keys)) == len(keys) == sum(n.values()) and drawn == sorted(set(drawn_units))
    return {'units_total': len(keys), **n, 'status': 'COMPLETE' if ok else 'INCOMPLETE'}


def binding_warnings(units):
    out = []
    for u in units:
        if u['state'] == 'off_axis':
            out.append({'code': 'VP09_ARGUMENT_OFF_AXIS', 'owner': u['owner'], 'method_id': u['method_id'], 'role': u['role'],
                        'ref': u['ref'], 'home': u['home'], 'declaration_ref': u['declaration_ref']})
        elif u['state'] == 'out_of_slice':
            out.append({'code': 'VP09_ARGUMENT_OUT_OF_SLICE', 'owner': u['owner'], 'method_id': u['method_id'], 'role': u['role'],
                        'reason': u['reason'], 'declaration_ref': u['declaration_ref']})
    return out


def render_axes(doc, rows, cols, granularity='standard'):
    p = AxesPrinter()
    pr = p.project(doc, rows, cols, granularity)
    svg, drawn = p.render(pr)
    return p.report(pr, svg, drawn), svg
