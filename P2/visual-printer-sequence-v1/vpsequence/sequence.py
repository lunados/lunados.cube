"""VP-08 view `cube.sequence` (SP, SM, SF, SS-6): one declared trigger as lifelines and numbered messages.

Display only. Message order is the declared list order, never a time axis; an arrow never asserts
causation, success, permission or authority. Nothing is inferred: returns are drawn only when declared.
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from .common import (PROFILE, BUDGET, LEVELS, OVERFLOWS, NOT_EVALUATED, NS, STROKE, INK, MUTED, Printer, add, line, rect, text,
                     excerpt, cjson, sha_bytes, sha_json, fmt, no_active_content, need, two_lines)
from .source import validate_source

REPORT_FORMAT = 'aiaeao.cube.vp08-sequence-report/1'
W = 1200
X0, X1 = 150, 1140  # participant columns
PITCH = {'overview': 48, 'standard': 44, 'detail': 40}  # SM-4
DASH_RETURN = '6 4'
LEGEND = {'call': 'call · declared synchronous call (filled head)',
          'return': 'return · declared return, drawn only when declared (dashed, open head)',
          'async': 'async · declared asynchronous message (open head)',
          'self': 'self · declared call on the same participant'}


# -- analysis -----------------------------------------------------------------
def flatten(seq, depth=0, path=()):
    """Depth-first list of (item, depth, operand path); numbering follows this order (SM-1)."""
    out = []
    for it in seq:
        if 'fragment' in it:
            out.append(('frag', it, depth, path))
            for k, o in enumerate(it['operands']):
                out += flatten(o['sequence'], depth+1, path+((it['id'], k),))
        else:
            out.append(('msg', it, depth, path))
    return out


def analyse(trigger, methods):
    flat = flatten(trigger['sequence'])
    msgs = [x[1] for x in flat if x[0] == 'msg']
    numbering = {m['id']: i+1 for i, m in enumerate(msgs)}
    warnings, matched, ends = [], {}, {}

    def walk(seq, open_calls):
        opened = list(open_calls)
        for it in seq:
            if 'fragment' in it:
                for o in it['operands']:
                    walk(o['sequence'], opened)  # operands are alternatives: they never change the enclosing scope
                continue
            if it['kind'] == 'call':
                opened.append(it)
            elif it['kind'] == 'return':
                hit = next((c for c in reversed(opened) if c['from'] == it['to'] and c['to'] == it['from']), None)
                if hit is None:
                    warnings.append({'code': 'VP08_RETURN_UNMATCHED', 'message_id': it['id']})
                else:
                    matched.setdefault(hit['id'], []).append(it['id'])
                    if hit in opened[len(open_calls):]:
                        opened.remove(hit)
            if methods is not None and it.get('method_id') and it['method_id'] not in methods:
                warnings.append({'code': 'VP08_METHOD_UNKNOWN', 'message_id': it['id'], 'method_id': it['method_id']})
    walk(trigger['sequence'], [])
    if trigger.get('returns') == 'expected':
        for m in msgs:
            if m['kind'] == 'call' and m['id'] not in matched:
                warnings.append({'code': 'VP08_RETURN_UNDECLARED', 'message_id': m['id']})
    for c, rs in matched.items():
        ends[c] = max(rs, key=lambda r: numbering[r])
    warnings.sort(key=lambda w: (numbering[w['message_id']], w['code']))
    return {'flat': flat, 'messages': msgs, 'numbering': numbering, 'warnings': warnings, 'activation_end': ends}


def _touched(it):
    if 'fragment' not in it:
        return [it['from'], it['to']]
    out = []
    for o in it['operands']:
        for x in o['sequence']:
            out += _touched(x)
    return out


def _depth(it):
    if 'fragment' not in it:
        return 0
    return 1+max(_depth(x) for o in it['operands'] for x in o['sequence'])


def _msgs(it):
    if 'fragment' not in it:
        return [it]
    return [m for o in it['operands'] for x in o['sequence'] for m in _msgs(x)]


def windows(trigger, participants, granularity, overflow):
    """SS-6: top-level items packed greedily into windows that fit; fragments are never split."""
    pcap, mcap, dcap = BUDGET[granularity]

    def fits(items, first):
        ps = {trigger['enters']} if first else set()
        for it in items:
            ps |= set(_touched(it))
        return len(ps) <= pcap and sum(len(_msgs(i)) for i in items) <= mcap and max(_depth(i) for i in items) <= dcap
    items = trigger['sequence']
    depth = max(_depth(i) for i in items)
    need(depth <= dcap, 'VP08_SEQUENCE_BUDGET', f'fragment depth {depth} exceeds {granularity} ({dcap}); depth is never summarized', 'granularity')
    if fits(items, True):
        return [items]
    need(granularity != 'detail', 'VP08_SEQUENCE_BUDGET', f'trigger {trigger["id"]} exceeds the detail budget; detail never continues', 'granularity')
    need(overflow != 'reject', 'VP08_SEQUENCE_BUDGET', f'trigger {trigger["id"]} exceeds the {granularity} budget (overflow=reject)', 'granularity')
    out, cur = [], []
    for it in items:
        if cur and fits(cur+[it], not out):
            cur.append(it); continue
        if cur:
            out.append(cur)
        need(fits([it], not out and not cur), 'VP08_SEQUENCE_BUDGET',
             f'item {it["id"]} alone exceeds the {granularity} budget; choose detail or split the declaration', 'granularity')
        cur = [it]
    out.append(cur)
    return out


# -- rendering ----------------------------------------------------------------
class SequencePrinter:
    def __init__(self):
        self.base = Printer()

    def project(self, src, trigger_id, granularity='standard', overflow='summarize'):
        v = validate_source(src)
        need(trigger_id in v['triggers'], 'VP08_TRIGGER_INVALID', 'unknown trigger '+repr(trigger_id))
        need(granularity in LEVELS, 'VP08_SEQUENCE_BUDGET', 'granularity must be overview|standard|detail', 'granularity')
        need(overflow in OVERFLOWS, 'VP08_SEQUENCE_BUDGET', 'overflow must be summarize or reject', 'granularity')
        t = v['triggers'][trigger_id]
        a = analyse(t, v['methods'])
        wins = windows(t, v['participants'], granularity, overflow)
        warnings = list(a['warnings'])
        if len(wins) > 1:
            warnings.append({'code': 'VP08_SEQUENCE_CONTINUED', 'windows': len(wins)})
        return {'src': src, 'v': v, 'trigger': t, 'analysis': a, 'windows': wins, 'warnings': warnings, 'granularity': granularity,
                'overflow': overflow}

    # layout of one window: participants (declared order), rows with y
    def _layout(self, pr, k):
        items = pr['windows'][k]
        t = pr['trigger']
        P = PITCH[pr['granularity']]
        touched = ({t['enters']} if k == 0 else set()) | {p for it in items for p in _touched(it)}
        cols = [p for p in pr['v']['participants'] if p in touched]
        n = len(cols)
        cw = (X1-X0)/n
        cx = {p: X0+cw*(i+0.5) for i, p in enumerate(cols)}
        y = 236
        ops = []
        if k == 0:
            ops.append(('trigger', None, y, 0, ()))
            y += P
        else:
            ops.append(('cont', None, y-20, 0, ()))

        def lay(seq, depth, path):
            nonlocal y
            for it in seq:
                if 'fragment' in it:
                    top = y-26
                    y = top+58
                    seps = []
                    for j, o in enumerate(it['operands']):
                        if j:
                            seps.append(y-26)
                            y = seps[-1]+52
                        lay(o['sequence'], depth+1, path+((it['id'], j),))
                    bottom = y-P+12
                    ops.append(('frame', it, top, depth, (bottom, seps)))
                    y = bottom+36
                else:
                    ops.append(('msg', it, y, depth, path))
                    y += P
        lay(items, 0, ())
        return {'cols': cols, 'cx': cx, 'cw': cw, 'ops': ops, 'bottom': y-P+30, 'items': items}

    def _arrow_head(self, g, x, y, direction, filled):
        d = 1 if direction > 0 else -1
        pts = f'{fmt(x-d*9)},{fmt(y-5)} {fmt(x)},{fmt(y)} {fmt(x-d*9)},{fmt(y+5)}'
        if filled:
            add(g, 'polygon', points=pts, fill=STROKE, stroke=STROKE, stroke_width=1)
        else:
            add(g, 'polyline', points=pts, fill='none', stroke=STROKE, stroke_width=1.6)
        g.set('data-vp08-head', 'filled' if filled else 'open')

    def _message(self, root, m, y, num, lay, pr):
        cx = lay['cx']
        g = add(root, 'g', **{'data-vp08-message': m['id'], 'data-vp08-number': str(num), 'data-vp08-kind': m['kind'],
                              'data-declaration-ref': m['declaration_ref']})
        title = f"{num} · {m['label']} | {m['kind']} {m['from']} → {m['to']} | {m['declaration_ref']}"
        if m.get('method_id'):
            g.set('data-method-id', m['method_id'])
            title += ' | method '+m['method_id']
        add(g, 'title').text = title
        x1, x2 = cx[m['from']], cx[m['to']]
        if m['kind'] == 'self':
            sx = x1+6
            for a, b, c, d in ((sx, y-12, sx+34, y-12), (sx+34, y-12, sx+34, y+4), (sx+34, y+4, sx+8, y+4)):
                line(g, fmt(a), fmt(b), fmt(c), fmt(d), STROKE)
            self._arrow_head(g, sx+1, y+4, -1, True)
            anchor_x = sx+40
            lines = two_lines(f'{num} · {m["label"]}', max(10, int(lay['cw']*0.8/6.2)))
            for j, s in enumerate(lines):
                t = text(g, fmt(anchor_x), fmt(y-8+j*13), s, 11, '#1E293B')
                t.set('data-vp08-label-line', str(j+1))
            return g
        d = 1 if x2 > x1 else -1
        a, b = x1+d*6, x2-d*6
        ln = line(g, fmt(a), fmt(y), fmt(b), fmt(y), STROKE)
        if m['kind'] == 'return':
            ln.set('stroke-dasharray', DASH_RETURN)
        self._arrow_head(g, b, y, d, m['kind'] == 'call')
        width = max(10, int((abs(x2-x1)-24)/6.2))
        lines = two_lines(f'{num} · {m["label"]}', width)
        mid = (x1+x2)/2
        for j, s in enumerate(lines):
            t = text(g, fmt(mid), fmt(y-6-(len(lines)-1-j)*13), s, 11, '#1E293B', anchor='middle')
            t.set('stroke', '#FFFFFF'); t.set('stroke-width', '3'); t.set('paint-order', 'stroke')
            t.set('data-vp08-label-line', str(j+1))
        return g

    def render_window(self, pr, k):
        lay = self._layout(pr, k)
        t, a = pr['trigger'], pr['analysis']
        cx, cw = lay['cx'], lay['cw']
        nwin = len(pr['windows'])
        win_msgs = [m['id'] for it in lay['items'] for m in _msgs(it)]
        kinds = []
        for it in lay['items']:
            for m in _msgs(it):
                if m['kind'] not in kinds:
                    kinds.append(m['kind'])
        has_frames = any(op[0] == 'frame' for op in lay['ops'])
        legend_rows = len(kinds)+1+(1 if has_frames else 0)+(1 if k == 0 else 0)
        height = int(lay['bottom']+40+legend_rows*22+40+len(win_msgs)*19+100)
        src = pr['src']
        parts = pr['v']['participants']
        sub = src.get('subtitle') or f"v9.4 · VP-08 · trigger {t['label']} ({t['kind']})" + (f" · use case {t['use_case']}" if 'use_case' in t else '')
        title = excerpt(src['title']+' · '+t['label'], 78)
        if nwin > 1:
            title = excerpt(src['title']+' · '+t['label'], 66)+f' · {k+1}/{nwin}'
        root = self.base._root({'view_id': 'cube.sequence', 'title': title, 'subtitle': excerpt(sub, 105)}, height)
        root.set('data-printer-profile', PROFILE)
        root.set('data-cube-view', 'cube.sequence')
        root.set('data-vp08-trigger-id', t['id'])
        root.set('data-vp08-window', f'{k+1}/{nwin}')
        text(root, 60, 125, 'CUBE.SEQUENCE · DECLARED MESSAGES IN DECLARED ORDER · not a time axis, not a causal claim', 13, MUTED, 'bold')
        # participant headers and lifelines (SP-1…SP-3)
        hw = min(cw-14, 210)
        for p in lay['cols']:
            item = parts[p]
            anc = self.base.by_id[item['anchor_id']]
            g = add(root, 'g', **{'data-item-id': p, 'data-anchor-id': item['anchor_id'], 'data-form-id': item['form_id'],
                                  'data-vp08-participant': p})
            if item.get('semantic_ref'):
                g.set('data-semantic-ref', item['semantic_ref'])
            add(g, 'title').text = item['label']+' · '+item['anchor_id']
            x = cx[p]
            rect(g, fmt(x-hw/2), 142, fmt(hw), 46, '#94A3B8', '#F8FAFC', 8)
            text(g, fmt(x-hw/2+16), 171, anc['unicode'], 16, INK, anchor='middle', glyph=True)
            lines = two_lines(item['label'], max(8, int((hw-36)/6.6)))
            for j, s in enumerate(lines):
                text(g, fmt(x-hw/2+30), fmt(162+j*14 if len(lines) > 1 else 169), s, 11.5, INK, 'bold')
            ll = line(g, fmt(x), 190, fmt(x), fmt(lay['bottom']), '#94A3B8')
            ll.set('stroke-dasharray', '4 5')
        # activation bars (SP-3): callee lifeline from call to its last declared matching return
        ys = {op[1]['id']: op[2] for op in lay['ops'] if op[0] == 'msg'}
        for op in lay['ops']:
            if op[0] != 'msg' or op[1]['kind'] != 'call':
                continue
            m = op[1]
            end = a['activation_end'].get(m['id'])
            y_end = ys.get(end, lay['bottom']-24) if end else lay['bottom']-24
            if end is None:
                same = [o for o in lay['ops'] if o[0] == 'msg' and o[4] == op[4]]
                y_end = same[-1][2] if same else op[2]
                if y_end <= op[2]:
                    y_end = op[2]+12
            r = rect(root, fmt(cx[m['to']]-5), fmt(op[2]), 10, fmt(max(12, y_end-op[2])), '#94A3B8', '#E2E8F0', 1)
            r.set('data-vp08-activation', m['id'])
        # frames (SF-1…SF-3)
        for op in lay['ops']:
            if op[0] != 'frame':
                continue
            it, top, depth = op[1], op[2], op[3]
            bottom, seps = op[4]
            ps = [p for p in lay['cols'] if p in set(_touched(it))]
            xl = min(cx[p] for p in ps)-cw*0.42+depth*8
            xr = max(cx[p] for p in ps)+cw*0.42-depth*8
            if len(ps) == 1:
                xr = max(xr, xl+220)
            g = add(root, 'g', **{'data-vp08-frame': it['id'], 'data-vp08-fragment': it['fragment'], 'data-vp08-participants': ' '.join(ps)})
            label = it['fragment']+' '+' / '.join('['+(o.get('guard') or o.get('bound'))+']' for o in it['operands'])
            add(g, 'title').text = f"{it['id']} · {label} · guards and bounds are declared text, never evaluated"
            rect(g, fmt(xl), fmt(top), fmt(xr-xl), fmt(bottom-top), '#64748B', 'none', 3)
            tag_w = 12+7.2*len(it['fragment'])
            add(g, 'polygon', points=f"{fmt(xl)},{fmt(top)} {fmt(xl+tag_w+8)},{fmt(top)} {fmt(xl+tag_w+8)},{fmt(top+12)} "
                                     f"{fmt(xl+tag_w)},{fmt(top+19)} {fmt(xl)},{fmt(top+19)}", fill='#F1F5F9', stroke='#64748B', stroke_width=1.2)
            text(g, fmt(xl+6), fmt(top+14), it['fragment'], 11, INK, 'bold')
            first = it['operands'][0]
            guards = [text(g, fmt(xl+tag_w+16), fmt(top+14), '['+(first.get('guard') or first.get('bound'))+']', 11, '#334155')]
            for j, sy in enumerate(seps):
                sl = line(g, fmt(xl), fmt(sy), fmt(xr), fmt(sy), '#64748B')
                sl.set('stroke-dasharray', '6 4')
                guards.append(text(g, fmt(xl+8), fmt(sy+14), '['+it['operands'][j+1]['guard']+']', 11, '#334155'))
            for gt in guards:  # halo keeps declared guard text legible over lifelines (no colour semantics)
                gt.set('stroke', '#FFFFFF'); gt.set('stroke-width', '3'); gt.set('paint-order', 'stroke')
        # trigger arrow 0 / continuation (ST-3)
        for op in lay['ops']:
            if op[0] == 'trigger':
                y = op[2]
                g = add(root, 'g', **{'data-vp08-trigger': t['id'], 'data-vp08-number': '0', 'data-declaration-ref': t['declaration_ref']})
                add(g, 'title').text = f"0 · trigger {t['label']} ({t['kind']}) enters {t['enters']} | {t['declaration_ref']}"
                add(g, 'circle', cx=66, cy=fmt(y), r=5, fill=STROKE, stroke=STROKE, stroke_width=1)
                xe = cx[t['enters']]-6
                line(g, 72, fmt(y), fmt(xe), fmt(y), STROKE)
                self._arrow_head(g, xe, y, 1, True)
                tl = two_lines(f"0 · {t['label']} ({t['kind']})", max(12, int((xe-90)/6.4)))
                for j, s_ in enumerate(tl):
                    tt = text(g, 80, fmt(y-7-(len(tl)-1-j)*13), s_, 11, '#1E293B', 'bold')
                    tt.set('stroke', '#FFFFFF'); tt.set('stroke-width', '3'); tt.set('paint-order', 'stroke')
            elif op[0] == 'cont':
                first = win_msgs[0]
                g = add(root, 'g', **{'data-vp08-continued-from': str(a['numbering'][first]-1)})
                text(g, 66, fmt(op[2]), f"… continued from message {a['numbering'][first]-1} (window {k}/{nwin})", 11, MUTED, 'bold')
        for op in lay['ops']:
            if op[0] == 'msg':
                self._message(root, op[1], op[2], a['numbering'][op[1]['id']], lay, pr)
        if k+1 < nwin:
            nxt = [m['id'] for it in pr['windows'][k+1] for m in _msgs(it)][0]
            g = add(root, 'g', **{'data-vp08-continues-at': str(a['numbering'][nxt])})
            text(g, 66, fmt(lay['bottom']-6), f"… continues with message {a['numbering'][nxt]} (window {k+2}/{nwin})", 11, MUTED, 'bold')
        # legend (only kinds drawn in this window, each once)
        y = lay['bottom']+40
        lg = add(root, 'g', **{'data-vp08-legend': 'display-only'})
        text(lg, 62, fmt(y), 'LEGEND · declared display conventions · not a verdict', 13, MUTED, 'bold')
        y += 24
        if k == 0:
            row = add(lg, 'g', **{'data-vp08-legend-kind': 'trigger'})
            add(row, 'circle', cx=72, cy=fmt(y-4), r=4, fill=STROKE, stroke=STROKE, stroke_width=1)
            line(row, 76, fmt(y-4), 122, fmt(y-4), STROKE)
            self._arrow_head(row, 128, y-4, 1, True)
            text(row, 142, fmt(y), '0 · declared trigger (entry point); numbers give declared order only', 12, '#334155')
            y += 22
        for kind in [x for x in ('call', 'return', 'async', 'self') if x in kinds]:
            row = add(lg, 'g', **{'data-vp08-legend-kind': kind})
            if kind == 'self':
                for a1, b1, c1, d1 in ((72, y-10, 104, y-10), (104, y-10, 104, y+2), (104, y+2, 80, y+2)):
                    line(row, a1, fmt(b1), c1, fmt(d1), STROKE)
                self._arrow_head(row, 73, y+2, -1, True)
            else:
                s = line(row, 70, fmt(y-4), 122, fmt(y-4), STROKE)
                if kind == 'return':
                    s.set('stroke-dasharray', DASH_RETURN)
                self._arrow_head(row, 128, y-4, 1, kind == 'call')
            text(row, 142, fmt(y), LEGEND[kind], 12, '#334155')
            y += 22
        if has_frames:
            row = add(lg, 'g', **{'data-vp08-legend-kind': 'fragment'})
            rect(row, 70, fmt(y-14), 58, 16, '#64748B', 'none', 3)
            text(row, 142, fmt(y), 'alt / opt / loop · declared fragment; [guards] and [bounds] are declared text, never evaluated', 12, '#334155')
            y += 22
        # declaration ledger
        y += 18
        text(root, 62, fmt(y), 'DECLARATION LEDGER · each arrow is a declared, unverified message', 13, MUTED, 'bold')
        msgs = {m['id']: m for m in a['messages']}
        for mid in win_msgs:
            m = msgs[mid]
            y += 19
            text(root, 68, fmt(y), excerpt(f"{a['numbering'][mid]} · {mid} · {m['kind']} · {m['from']} → {m['to']}"
                                           + (f" · method {m['method_id']}" if m.get('method_id') else ''), 82), 11, '#334155')
            text(root, 640, fmt(y), excerpt(m['declaration_ref'], 82), 10, MUTED)
        omitted = [p for p in parts if p not in lay['cols']]
        text(root, 62, fmt(y+30), f"Window {k+1}/{nwin} · messages {a['numbering'][win_msgs[0]]}–{a['numbering'][win_msgs[-1]]} of "
             f"{len(a['messages'])} · {len(lay['cols'])} participants · {pr['granularity'].upper()} budget", 12, MUTED)
        if omitted:
            text(root, 62, fmt(y+50), excerpt('Participants not involved in this window (SP-2): '+', '.join(omitted), 150), 12, MUTED)
        meta = add(root, 'metadata', id='vp08-sequence-ledger')
        meta.text = cjson(self.ledger(pr, k, lay))
        svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        return svg, lay

    @staticmethod
    def ledger(pr, k, lay):
        a = pr['analysis']
        ids = [m['id'] for it in lay['items'] for m in _msgs(it)]
        return {'profile': PROFILE, 'trigger_id': pr['trigger']['id'], 'window': k+1, 'windows': len(pr['windows']),
                'granularity': pr['granularity'], 'overflow': pr['overflow'], 'participants': lay['cols'],
                'omitted_participants': [p for p in pr['v']['participants'] if p not in lay['cols']],
                'message_ids': ids, 'numbers': [a['numbering'][i] for i in ids],
                'frames': [op[1]['id'] for op in lay['ops'] if op[0] == 'frame'], 'status': 'declared_unverified',
                'nonimplications': ['truth', 'causality', 'authority', 'admission', 'completeness', 'time', 'success']}

    def render(self, src, trigger_id, granularity='standard', overflow='summarize'):
        pr = self.project(src, trigger_id, granularity, overflow)
        out = [self.render_window(pr, k) for k in range(len(pr['windows']))]
        return self.report(src, pr, out), [svg for svg, _ in out]

    def report(self, src, pr, out):
        a = pr['analysis']
        inv = []

        def verify(ok, name):
            need(ok, 'VP08_AUDIT', 'VP-08 audit invariant failed: '+name, 'audit')
            if name not in inv:
                inv.append(name)
        seen = []
        wins = []
        for k, (svg, lay) in enumerate(out):
            root = ET.fromstring(svg)
            verify(no_active_content(root), 'NO_ACTIVE_SVG_CONTENT')
            blocks = [x for x in root.iter() if x.get('id') == 'vp08-sequence-ledger']
            verify(len(blocks) == 1, 'ONE_EMBEDDED_LEDGER')
            verify(blocks[0].text == cjson(self.ledger(pr, k, lay)), 'EMBEDDED_REPORT_MATCH')
            ids = [m['id'] for it in lay['items'] for m in _msgs(it)]
            drawn = [g.get('data-vp08-message') for g in root.iter(f'{{{NS}}}g') if g.get('data-vp08-message')]
            verify(sorted(drawn) == sorted(ids), 'DRAWN_MESSAGES_MATCH')
            seen += ids
            wins.append({'window': k+1, 'message_ids': ids, 'participants': lay['cols'], 'svg_sha256': sha_bytes(svg)})
        verify(sorted(seen) == sorted(m['id'] for m in a['messages']) and len(seen) == len(set(seen)), 'EXACT_MESSAGE_PARTITION')
        t = pr['trigger']
        return {'format': REPORT_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'render_status': 'PASS',
                'view': 'cube.sequence', 'lens': 'neutral', 'trigger_id': t['id'], 'trigger_kind': t['kind'],
                'use_case': t.get('use_case'), 'granularity': pr['granularity'], 'overflow': pr['overflow'],
                'source_sha256': sha_json(src), 'numbering': a['numbering'], 'windows': wins,
                'counts': {'messages': len(a['messages']), 'windows': len(wins),
                           'fragments': sum(1 for x in a['flat'] if x[0] == 'frag')},
                'completeness': 'COMPLETE_INPUT_VIEW', 'warnings': pr['warnings'], 'invariants_passed': inv,
                'content_status': 'declared_unverified', 'source_status': 'declared_unverified', **NOT_EVALUATED,
                'notices': ['Message numbers give the declared order only; they are not a time axis.',
                            'Returns are drawn only when declared; guards are declared text and never evaluated.',
                            'An arrow never asserts causation, success, permission or authority.']}


def render_sequence(src, trigger_id, granularity='standard', overflow='summarize'):
    return SequencePrinter().render(src, trigger_id, granularity, overflow)
