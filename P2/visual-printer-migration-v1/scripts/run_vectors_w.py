#!/usr/bin/env python3
"""Run W-01..W-17 (VP-07.1) against vpmigration through its Python API.

Exit 0 only if every case matches the independent oracle (oracles/independent_w01_w17.json).
"""
import hashlib, json, re, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, render_plan, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/w01_w17_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_w01_w17.json').read_text('utf-8'))['cases']}
PINNED = json.loads((HERE/'fixtures/regression_070_digests.json').read_text('utf-8'))['digests']
G = f'{{{NS}}}g'


def panels(inp, tmp):
    report, files = print_panels(inp['source'], inp['view'], inp['partition'], inp['granularity'], inp.get('lens'))
    d = publish_dir(files, Path(tmp)/'panels')
    if inp.get('tamper') == 'outer_ledger':
        rep = json.loads((d/'report.json').read_text('utf-8'))
        e = next(o for o in rep['outer_ledger'] if o['panels'])
        e['panels'] = e['panels'][:-1]
        (d/'report.json').write_text(json.dumps(rep, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    check_panels(d)  # every export is re-verified (NP-4); a tampered ledger must FAIL here
    return {'warnings': report['warnings'], 'report': report, 'files': files}


def run(c, tmp):
    op, inp = c['op'], c['input']
    if op == 'phases':
        rep, svg = render_plan(inp['plan'], inp.get('overflow', 'summarize'))
        return {'warnings': rep['warnings'], 'report': rep, 'svgs': [svg]}
    if op == 'panels':
        return panels(inp, tmp)
    src, mapping = from_plan(inp['context'], inp['plan_id'], steps=inp.get('steps'))
    out = panels({'source': src, **inp['then']}, tmp)
    out['source'] = src
    return out


def svgs_of(out):
    if 'svgs' in out:
        return out['svgs']
    return [b for n, b in sorted(out['files'].items()) if n.startswith('panel-') and n.endswith('.svg')]


def boxes(svg):
    """Bounding boxes of each transition marker group (circles r=5 + stroke, code text ~6.6 px per char at 11 px)."""
    out = []
    for g in ET.fromstring(svg).iter(G):
        if not g.get('data-vp07-code'):
            continue
        xs, ys = [], []
        for e in g:
            tag = e.tag.split('}')[1]
            if tag == 'circle':
                cx, cy = float(e.get('cx')), float(e.get('cy'))
                xs += [cx-6, cx+6]; ys += [cy-6, cy+6]
            elif tag == 'text':
                x, y = float(e.get('x')), float(e.get('y'))
                xs += [x, x+6.6*len(e.text)]; ys += [y-9, y+3]
        out.append((g.get('data-transition-id'), min(xs), min(ys), max(xs), max(ys)))
    return out


def overlap(a, b):
    return not (a[3] <= b[1] or b[3] <= a[1] or a[4] <= b[2] or b[4] <= a[2])


def markers(svg):
    return {g.get('data-transition-id'): g for g in ET.fromstring(svg).iter(G) if g.get('data-vp07-code')}


def check(c, out):
    x = c['expect']
    ok = True
    rep = out['report']
    if x.get('no_panel_mixes_outer') or x.get('outer_ledger_complete') or 'outer_panel_count' in x:
        led = rep['outer_ledger']
        ok = ok and all(o['status'] == 'COMPLETE' for o in led) and rep['coverage']['status'] == 'COMPLETE'
        if x.get('no_panel_mixes_outer'):
            tracks = {r['id']: r['track'] for r in c['input']['source']['rows']}
            for e in rep['panel_ledger']:
                ok = ok and len({tracks[r] for r in e['shown_row_ids']}) == 1 and tracks[e['shown_row_ids'][0]] == e['outer_value']
        for ov, n in x.get('outer_panel_count', {}).items():
            ok = ok and len(next(o for o in led if o['outer_value'] == ov)['panels']) == n
    if 'marker_code' in x:
        m = markers(svgs_of(out)[0]).get(x['marker_code']['transition'])
        ok = ok and m is not None and m.get('data-vp07-code') == x['marker_code']['code']
        ok = ok and any(t.text == x['marker_code']['code'] for t in m.iter(f'{{{NS}}}text'))
    if 'full_id_in_legend_and_title' in x:
        tid = x['full_id_in_legend_and_title']
        root = ET.fromstring(svgs_of(out)[0])
        leg = [g for g in root.iter(G) if g.get('data-vp07-legend-code') and g.get('data-transition-id') == tid]
        ok = ok and len(leg) == 1 and any(tid in (t.text or '') for t in leg[0].iter(f'{{{NS}}}text'))
        ok = ok and tid in (leg[0].find(f'{{{NS}}}title').text or '') and tid in (markers(svgs_of(out)[0])[tid].find(f'{{{NS}}}title').text or '')
    if x.get('markers_no_overlap'):
        b = boxes(svgs_of(out)[0])
        ok = ok and len(b) >= 2 and all(not overlap(p, q) for i, p in enumerate(b) for q in b[i+1:])
    if 'both_glyphs_one_code' in x:
        m = markers(svgs_of(out)[0])[x['both_glyphs_one_code']]
        circ = list(m.iter(f'{{{NS}}}circle'))
        ok = ok and len(circ) == 2 and {e.get('fill') for e in circ} == {'#FFFFFF', '#475569'} and len({e.get('cy') for e in circ}) == 1
        ok = ok and len([t for t in m.iter(f'{{{NS}}}text')]) == 1
    if 'same_code_in_panels' in x:
        want = x['same_code_in_panels']
        got = [markers(s).get(want['transition']) for s in svgs_of(out)]
        got = [g.get('data-vp07-code') for g in got if g is not None]
        ok = ok and len(got) >= 2 and set(got) == {want['code']}
    if 'legend_rows' in x:
        root = ET.fromstring(svgs_of(out)[0])
        lg = next(g for g in root.iter(G) if g.get('data-vp07-legend'))
        texts = [t.text for t in lg.iter(f'{{{NS}}}text')]
        ok = ok and all(r in texts for r in x['legend_rows']) and not any(re.search(r'hatch [/\\] ·', t or '') for t in texts)
    if 'matches_pinned_070' in x:
        want = PINNED[x['matches_pinned_070']]
        ok = ok and {n: hashlib.sha256(b).hexdigest() for n, b in sorted(out['files'].items())} == want
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['forbidden_codes'], c['expect']) == \
            (o['expected_status'], o['required_codes'], o['forbidden_codes'], o['expect']), c['id']+': vector differs from oracle'
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP07Error as e:
                out, status, codes = None, 'FAIL', [e.code]
        ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) and not any(k in codes for k in c['forbidden_codes'])
        if ok and status == 'PASS':
            ok = check(c, out)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)))
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
