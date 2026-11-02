"""VP-11 `cube.instances`: a declared trace per instance (DR-1…DR-9, §9 DR-1a…DR-7a).

Frames stack vertically, one per instance; inside, one block per gateway the instance touches, in declared order;
flows are rows. Verdict lines come from lunados.lib records only (D-5); the process model stands apart (DR-7).
States differ by text and line style, not by colour (D-6).
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from .common import (PROFILE, VIEW, REPORT_FORMAT, NS, NOT_EVALUATED, INK, MUTED, Texts, CHECKS, add, line, rect, text, fmt, no_active_content,
                     need, sha_bytes, sha_json, cjson, wrap_sep)
from .trace import normalize

W, X0 = 1200, 60
DOTTED, DASHED = '1 4', '5 7'
STYLE = {'taken': None, 'arrived': None, 'token': None, 'not_taken': DOTTED, 'missing': DOTTED, 'no_token': DOTTED}
PRESENT, ABSENT = ('taken', 'arrived', 'token'), ('not_taken', 'missing', 'no_token')
KIND = {'PASS': 'checked', 'FAIL': 'violation', 'UNRESOLVED': 'not_checkable'}
HATCH_COLOR = '#94A3B8'
WRAP = 150


def _out_sorted(g):
    if g['role'] != 'xs':
        return list(g['outgoing'])
    idx = {id(o): i for i, o in enumerate(g['outgoing'])}
    return sorted(g['outgoing'], key=lambda o: (bool(o.get('default')), o.get('order', 10**9), idx[id(o)]))


class InstancesPrinter:
    # -- projection -----------------------------------------------------------------------------
    def project(self, doc, locale=None):
        doc = normalize(doc)
        T = Texts(locale)
        toks = doc['tokens']
        tpos = {t['token']: i for i, t in enumerate(toks)}
        inst_of = {t['token']: t['instance'] for t in toks}
        on_flow, routed = {}, {}
        for st in doc['statements']:
            (on_flow if st['role'] == 'on_flow' else routed).setdefault(st['object'] if st['role'] == 'on_flow' else st['subject'], []).append(
                st['subject'] if st['role'] == 'on_flow' else st['object'])
        frames = []                                           # DR-1a: first token of each instance; undeclared last
        for t in toks:
            if t['instance'] and t['instance'] not in frames:
                frames.append(t['instance'])
        for r in doc['records']:
            if r['claim']['instance'] not in frames:
                frames.append(r['claim']['instance'])
        if any(t['instance'] is None for t in toks):
            frames.append(None)
        recs = {}
        for r in doc['records']:
            recs.setdefault((r['claim']['gateway'], r['claim']['instance']), []).append(r)
        drawn_gws = [g for g in doc['gateways'] if g['role']]

        def mine(tok_list, inst):
            return sorted({k for k in tok_list if inst_of.get(k) == inst}, key=tpos.get)

        def foreign(tok_list, inst):
            if inst is None:                                  # DR-4a: no foreign notes in the undeclared frame
                return []
            return sorted({k for k in tok_list if inst_of.get(k) not in (inst, None)}, key=tpos.get)

        out = []
        for inst in frames:
            blocks = []
            for g in drawn_gws:
                flows = set(g['incoming']) | {o['flow'] for o in g['outgoing']}
                touches = any(inst_of.get(k) == inst for f in flows for k in on_flow.get(f, []))
                touches = touches or any(t['instance'] == inst and t['at'] == g['gateway'] for t in toks)
                touches = touches or (g['gateway'], inst) in recs
                if not touches:
                    continue
                blocks.append(self._block(g, inst, toks, on_flow, routed, mine, foreign, recs.get((g['gateway'], inst), []), T))
            out.append({'instance': inst, 'title': T.t('frame.title', instance=inst) if inst else T.t('frame.undeclared'), 'blocks': blocks})
        model = self._model(doc['gateways'], T)
        warnings = []
        if doc['not_drawn']:
            warnings.append({'code': 'VP11_STATEMENT_NOT_DRAWN', 'statements': list(doc['not_drawn']),
                             'detail': 'statements without control_flow_role are not drawn; listed in the ledger'})
        undecl = [t['token'] for t in toks if t['instance'] is None]
        if undecl:
            warnings.append({'code': 'VP11_INSTANCE_UNDECLARED', 'tokens': undecl, 'detail': 'tokens without instance_ref are drawn in the frame "instance undeclared"'})
        nd = [g['gateway'] for g in doc['gateways'] if not g['role']]
        if nd:
            warnings.append({'code': 'VP11_GATEWAY_NOT_DRAWN', 'gateways': nd, 'detail': 'unsupported type or role: model field only'})
        if not toks:
            warnings.append({'code': 'VP11_TRACE_EMPTY', 'detail': 'the trace has no token: model field only'})
        return {'doc': doc, 'T': T, 'frames': out, 'model': model, 'warnings': warnings, 'doc_sha': sha_json(doc)}

    @staticmethod
    def _block(g, inst, toks, on_flow, routed, mine, foreign, recs, T):
        rows = []
        tl = lambda ks: ', '.join(ks)  # noqa: E731

        def row(s, state, foreign_tokens=()):
            rows.append({'text': s, 'state': state, **({'foreign': list(foreign_tokens)} if foreign_tokens else {})})
        if g['role'] == 'xs':                                 # DR-3a
            outs = _out_sorted(g)
            for t in toks:
                if t['instance'] != inst or t['at'] != g['gateway']:
                    continue
                row(T.t('row.activation', token=t['token']), 'activation')
                targets = set(routed.get(t['token'], []))
                for o in outs:
                    how = T.t('row.default') if o.get('default') else T.t('row.order', n=o['order']) if 'order' in o else None
                    st = 'taken' if o['target'] in targets else 'not_taken'
                    row(' · '.join(x for x in (f"{o['flow']} → {o['target']}", how, T.t('row.'+st)) if x), st)
        else:                                                 # DR-4a
            for f in g['incoming']:
                own = mine(on_flow.get(f, []), inst)
                if g['role'] == 'pj':
                    if own:
                        row(f"{f} · {T.t('row.arrived')} · {tl(own)}", 'arrived')
                    else:
                        fr = foreign(on_flow.get(f, []), inst)
                        notes = ''.join(' · '+T.t('row.foreign', instance=next(x['instance'] for x in toks if x['token'] == k), token=k) for k in fr)
                        row(f"{f} · {T.t('row.missing')}{notes}", 'missing', fr)
                else:
                    row(f"{f} · {T.t('row.token', tokens=tl(own))}" if own else f"{f} · {T.t('row.no_token')}", 'token' if own else 'no_token')
            for o in g['outgoing']:
                own = mine(on_flow.get(o['flow'], []), inst)
                row(f"{o['flow']} → {o['target']} · " + (T.t('row.token', tokens=tl(own)) if own else T.t('row.no_token')), 'token' if own else 'no_token')
        verdicts = []
        for r in sorted(recs, key=lambda r: CHECKS.index(r['claim']['check'])):
            verdicts.append(InstancesPrinter._verdict(r, T))
        if not verdicts:
            verdicts.append({'text': T.t('state.not_checked'), 'kind': 'not_checked', 'check': None, 'claim': None})
        return {'gateway': g['gateway'], 'role': g['role'], 'header': f"{g['gateway']} · {T.t('role.'+g['role'])}", 'rows': rows, 'verdicts': verdicts}

    @staticmethod
    def _verdict(r, T):
        res = r['result']; kind = KIND[res['status']]
        parts = [f"{T.t('check.'+res['check'])}: {T.t('state.'+kind)}", T.t('value.'+res['value'])]
        lst = lambda xs: ', '.join(xs)  # noqa: E731
        if len(res.get('paths', [])) > 1:
            parts.append(f"{T.t('extra.paths')} {lst(res['paths'])}")
        for k in ('taken', 'first_true'):
            if res.get(k):
                parts.append(f"{T.t('extra.'+k)} {res[k]}")
        for k in ('missing', 'foreign'):
            if res.get(k):
                parts.append(f"{T.t('extra.'+k)} {lst(res[k])}")
        if res.get('excess'):
            parts.append(f"{T.t('extra.excess')} {lst(f'{f} {n}' for f, n in res['excess'].items())}")
        if res.get('missing_scope'):
            parts.append(f"{T.t('extra.undeclared')} " + lst(' '.join(x for x in (d['referent'], d['predicate_id'], d['direction'], d.get('instance_ref')) if x)
                                                             for d in res['missing_scope']['declarations']))
        return {'text': ' · '.join(parts), 'kind': kind, 'check': res['check'], 'claim': dict(r['claim'])}

    @staticmethod
    def _model(gws, T):
        lines = []
        for g in gws:                                         # DR-7a
            if not g['role']:
                lines.append(f"{g['gateway']} · {g['type']} · {T.t('model.not_drawn')}")
                continue
            lines.append(f"{g['gateway']} · {T.t('role.'+g['role'])}")
            lines.append(T.t('model.in', flows=', '.join(g['incoming'])))
            for o in _out_sorted(g):
                how = T.t('row.default') if o.get('default') else T.t('row.order', n=o['order']) if g['role'] == 'xs' and 'order' in o else None
                lines.append(' · '.join(x for x in (f"{o['flow']} → {o['target']}", how) if x))
        return lines

    # -- drawing --------------------------------------------------------------------------------
    def render(self, pr):
        doc, T = pr['doc'], pr['T']
        legend = [T.t('legend.solid'), T.t('legend.dotted'), T.t('legend.dashed'), T.t('legend.hatch'), T.t('legend.records'),
                  T.t('legend.started'), T.t('legend.colour')]
        wrapped = lambda s: wrap_sep(s, WRAP)[0]  # noqa: E731
        # layout pass: y of every element
        y = 150
        plan = []
        for fr in pr['frames']:
            y0 = y; y += 44
            items = []
            for b in fr['blocks']:
                items.append(('header', b, y)); y += 24
                for i, r in enumerate(b['rows']):
                    n = len(wrapped(r['text']))
                    items.append(('row', (b, i, r), y)); y += 18*n+4
                for v in b['verdicts']:
                    n = len(wrapped(v['text']))
                    items.append(('verdict', (b, v), y)); y += 18*n+6
                y += 12
            if not fr['blocks']:
                y += 10
            plan.append((fr, y0, y, items)); y += 22
        model_y = y; y += 40+18*sum(len(wrapped(s)) for s in pr['model'])+20
        legend_y = y; y += 30+18*len(legend)+20
        height = int(y+70)
        title = T.t('title', set_id=doc['set_id'])
        root = ET.Element(f'{{{NS}}}svg', {'version': '1.1', 'width': str(W), 'height': str(height), 'viewBox': f'0 0 {W} {height}', 'role': 'img',
                                           'aria-labelledby': 'svg-title svg-desc', 'data-printer-profile': PROFILE, 'data-cube-view': VIEW})
        add(root, 'title', id='svg-title').text = title
        add(root, 'desc', id='svg-desc').text = ('Display-only AIAEAO v9.4 view of a declared trace per instance. Verdicts are read from lunados.lib '
                                                 'records; geometry and colours cannot imply verification, permission, admission or execution.')
        rect(root, 0, 0, W, height, '#FFFFFF', '#FFFFFF', 0)
        rect(root, 0, 0, W, 9, '#111827', '#111827', 0)
        text(root, 42, 48, title, 27, '#111827', 'bold')
        text(root, 42, 75, T.t('subtitle', set_id=doc['set_id'], context_id=doc['context_id']), 14, '#475569')
        line(root, 42, 93, W-42, 93, '#E2E8F0')
        text(root, X0, 125, T.t('header'), 13, MUTED, 'bold')
        marks = 0
        for fr, y0, y1, items in plan:
            key = fr['instance'] or '-'
            fg = add(root, 'g', **{'data-vp11-frame': key})
            add(fg, 'title').text = fr['title']
            rect(fg, X0-18, y0, W-2*(X0-18), y1-y0, INK, '#FFFFFF', 6)
            text(fg, X0, y0+28, '⬠', 18, INK, glyph=True)
            text(fg, X0+26, y0+28, fr['title'], 16, INK, 'bold')
            for what, payload, yy in items:
                if what == 'header':
                    hg = add(fg, 'g', **{'data-vp11-block': f"{key}|{payload['gateway']}", 'data-vp11-role': payload['role']})
                    text(hg, X0+10, yy+14, payload['header'], 13, INK, 'bold')
                elif what == 'row':
                    b, i, r = payload
                    rg = add(fg, 'g', **{'data-vp11-row': f"{key}|{b['gateway']}|{i+1}", 'data-vp11-state': r['state']})
                    add(rg, 'title').text = r['text']
                    if r['state'] != 'activation':
                        mk = line(rg, X0+20, yy+9, X0+56, yy+9, INK)
                        mk.set('stroke-width', '2')
                        if STYLE[r['state']]:
                            mk.set('stroke-dasharray', STYLE[r['state']])
                    if r.get('foreign'):
                        rg.set('data-vp11-foreign', ' '.join(r['foreign']))
                        fm = line(rg, X0+60, yy+9, X0+84, yy+9, INK, dashed=True)
                        fm.set('stroke-width', '2')
                    for n, s in enumerate(wrapped(r['text'])):
                        text(rg, X0+92, yy+13+18*n, s, 12, INK, 'bold' if r['state'] == 'activation' else 'normal')
                else:
                    b, v = payload
                    vg = add(fg, 'g', **{'data-vp11-verdict': f"{key}|{b['gateway']}", 'data-vp11-kind': v['kind']})
                    add(vg, 'title').text = v['text']
                    if v['kind'] == 'violation':                # DR-6, PV-5: hatching from lines, next to the line
                        marks += 1
                        mg = add(vg, 'g', **{'data-vp11-mark': 'violation'})
                        rect(mg, X0+20, yy+1, 36, 14, INK, '#FFFFFF', 0)
                        for k in range(1, 6):
                            hx = X0+20+6*k
                            line(mg, hx, yy+1, hx-6, yy+15, HATCH_COLOR).set('stroke-width', '1')
                    for n, s in enumerate(wrapped(v['text'])):
                        e = text(vg, X0+92, yy+13+18*n, s, 12, INK, 'bold' if v['kind'] == 'violation' else 'normal')
                        e.set('font-style', 'italic')
        mg = add(root, 'g', **{'data-vp11-model': 'no-trace'})
        rect(mg, X0-18, model_y, W-2*(X0-18), legend_y-model_y-14, MUTED, '#FFFFFF', 6, dashed=True)
        text(mg, X0, model_y+26, T.t('model.title'), 14, MUTED, 'bold')
        yy = model_y+48
        heads = {g['gateway'] for g in doc['gateways']}
        for s in pr['model']:
            head = s.split(' · ', 1)[0] in heads                # DR-7a: gateway lines bold, flow lines indented
            for part in wrapped(s):
                text(mg, X0+10 if head else X0+30, yy, part, 12, '#334155', 'bold' if head else 'normal'); yy += 18
        lg = add(root, 'g', **{'data-vp11-legend': 'display-only'})
        text(lg, X0, legend_y+20, T.t('legend.title'), 13, MUTED, 'bold')
        for n, s in enumerate(legend):
            text(lg, X0+10, legend_y+42+18*n, s, 12, '#334155')
        line(root, 42, height-49, W-42, height-49, '#E2E8F0')
        text(root, 42, height-25, T.t('footer'), 13, '#475569')
        text(root, W-42, height-25, VIEW, 12, '#64748B', anchor='end')
        add(root, 'metadata', id='vp11-instances-ledger').text = cjson(self.ledger(pr))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg, marks

    # -- ledger, audit, report ------------------------------------------------------------------
    @staticmethod
    def ledger(pr):
        doc = pr['doc']
        frames = [{'instance': f['instance'], 'title': f['title'],
                   'blocks': [{'gateway': b['gateway'], 'role': b['role'], 'header': b['header'], 'rows': b['rows'], 'verdicts': b['verdicts']}
                              for b in f['blocks']]} for f in pr['frames']]
        return {'profile': PROFILE, 'set_id': doc['set_id'], 'context_id': doc['context_id'], 'frames': frames, 'model': pr['model'],
                'statements': doc['statements'], 'not_drawn': doc['not_drawn'],
                'records': [{'library_ref': r['library_ref'], 'claim': r['claim'], 'status': r['result']['status'], 'value': r['result']['value'],
                             'details': r['result']['details']} for r in doc['records']],
                'sources': doc['sources'], 'locale': pr['T'].record(), 'status': 'declared_unverified',
                'nonimplications': ['execution', 'truth', 'completeness in the world', 'causality between tokens', 'time',
                                    'a verdict not read from a lunados.lib record']}

    def report(self, pr, svg, marks):
        inv = []

        def verify(ok, name):
            need(ok, 'VP11_AUDIT', 'VP-11 audit invariant failed: '+name, 'audit')
            inv.append(name)
        q = lambda tag: f'{{{NS}}}{tag}'  # noqa: E731
        root = ET.fromstring(svg)
        verify(no_active_content(root) and not any(el.tag == q('pattern') for el in root.iter()), 'NO_ACTIVE_SVG_CONTENT_NO_PATTERN')
        led = self.ledger(pr)
        blocks = [el for el in root.iter() if el.get('id') == 'vp11-instances-ledger']
        verify(len(blocks) == 1 and blocks[0].text == cjson(led), 'EMBEDDED_LEDGER_MATCH')
        sig = {}
        for g in root.iter(q('g')):
            st = g.get('data-vp11-state')
            if st:
                marks_ = [ln.get('stroke-dasharray') for ln in g.findall(q('line'))]
                sig.setdefault(st, set()).add(tuple(marks_[:1]))
        one = all(len(v) == 1 for v in sig.values())
        style = {st: next(iter(v)) for st, v in sig.items()}
        cls = {('present' if st in PRESENT else 'absent' if st in ABSENT else st): s for st, s in style.items()}
        same_class = all(style[a] == style[b] for grp in (PRESENT, ABSENT) for a in grp for b in grp if a in style and b in style)
        verify(one and same_class and len(set(cls.values())) == len(cls), 'STATES_DIFFER_WITHOUT_COLOUR')
        claims = {(r['claim']['check'], r['claim']['gateway'], r['claim']['instance']): r['result']['status'] for r in pr['doc']['records']}
        shown = [(v['claim'], v['kind']) for f in pr['frames'] for b in f['blocks'] for v in b['verdicts']]
        ok = all((c is None and k == 'not_checked') or (c is not None and KIND[claims[(c['check'], c['gateway'], c['instance'])]] == k) for c, k in shown)
        ok = ok and marks == sum(1 for _, k in shown if k == 'violation') == sum(1 for g in root.iter(q('g')) if g.get('data-vp11-mark') == 'violation')
        verify(ok, 'VERDICTS_FROM_RECORDS_ONLY')
        model = next(g for g in root.iter(q('g')) if g.get('data-vp11-model'))
        toks = {t['token'] for t in pr['doc']['tokens']}
        verify(not any(tok in (t.text or '') for t in model.iter(q('text')) for tok in toks), 'MODEL_SEPARATE_FROM_TRACE')
        summary = {}
        for w in pr['warnings']:
            summary.setdefault(w['code'], {'code': w['code'], 'count': 0})['count'] += 1
        doc = pr['doc']
        return {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS', 'view': VIEW,
                'set_id': doc['set_id'], 'context_id': doc['context_id'], 'input_sha256': pr['doc_sha'], 'svg_sha256': sha_bytes(svg),
                'frames': led['frames'], 'model': pr['model'], 'records': led['records'], 'not_drawn': doc['not_drawn'],
                'violation_marks': marks, 'warnings': pr['warnings'], 'warning_summary': list(summary.values()), 'invariants_passed': inv,
                'locale': led['locale'], 'content_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Verdicts are read from lunados.lib analyze.trace-conformance/v1 records; the view computes none (D-5).',
                            '"not checked" means no record was given, not that the trace conforms.',
                            'A step counts as started only if a token on its flow shows it; the process model carries no trace.',
                            'No colour, size or position encodes a state or a quantity.']}


def render_instances(doc, locale=None):
    p = InstancesPrinter()
    pr = p.project(doc, locale)
    svg, marks = p.render(pr)
    return p.report(pr, svg, marks), svg
