#!/usr/bin/env python3
"""Run M-01..M-12 (VP-07.3) against vpmigration through its Python API.

Exit 0 only if every case matches the independent oracle (oracles/independent_m01_m12.json).
"""
import copy, json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/m01_m12_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_m01_m12.json').read_text('utf-8'))['cases']}
G = f'{{{NS}}}g'
T = f'{{{NS}}}text'


def panels(src, t, tmp):
    report, files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))
    check_panels(publish_dir(files, Path(tmp)/'panels'))
    return report, files


def fp(inp, ctx=None):
    kw = {k: inp[k] for k in ('tracks', 'layers', 'labels', 'subjects') if k in inp}
    return from_plan(ctx or inp['context'], inp['plan_id'], **kw)


def run(c, tmp):
    inp = c['input']
    if c['op'] == 'panels':
        rep, files = panels(inp['source'], inp, tmp)
        return {'warnings': rep['warnings'], 'report': rep, 'files': files}
    src, mapping = fp(inp)
    out = {'source': src, 'mapping': mapping, 'warnings': list(mapping.get('warnings', []))}
    if 'then' in inp:
        rep, files = panels(src, inp['then'], tmp+'/a')
        out.update(report=rep, files=files, warnings=out['warnings']+rep['warnings'])
    return out


def strip7(ctx):
    """The same plan without P1.11 (a /6 context): what the panel looked like before 0.7.3."""
    c = copy.deepcopy(ctx)
    c['format'] = 'aiaeao.cube.binding-context/6'
    c.pop('method_profile_refs', None); c.pop('method_contracts', None)
    for mp in c['migration_plans']:
        for t in mp['transitions']:
            t.pop('methods', None)
        for d in mp['dependencies']:
            d.pop('method', None)
    return c


def svgs(out):
    return [ET.fromstring(b) for n, b in sorted(out['files'].items()) if n.startswith('panel-') and n.endswith('.svg')]


def legend_lines(out):
    res = {}
    for root in svgs(out):
        for g in root.iter(G):
            if g.get('data-vp07-legend-code'):
                res.setdefault(g.get('data-vp07-legend-code'), []).append(' '.join(t.text or '' for t in g.iter(T)))
    return res


def bar(out, cell):
    for root in svgs(out):
        for g in root.iter(G):
            if g.get('data-cell-id') == cell:
                return g
    return None


def check(c, out, tmp):
    x, ok = c['expect'], True
    src = out.get('source')
    if 'source_profile' in x:
        ok = ok and src['profile'] == x['source_profile']
    if 'transition_methods' in x:
        got = {t['id']: [b['method_id'] for b in t['methods']] for t in src['transitions'] if 'methods' in t}
        ok = ok and got == x['transition_methods']
    if 'cell_method' in x:
        ok = ok and {c_['id']: c_['method']['method_id'] for c_ in src['cells'] if 'method' in c_} == x['cell_method']
    if 'method_ref' in x:
        w = x['method_ref']
        b = next(t for t in src['transitions'] if t['id'] == w['owner'])['methods'][w['index']]
        ok = ok and b['declaration_ref'] == w['declaration_ref'] and b['arguments'] == w['arguments']
    if x.get('no_methods'):
        ok = ok and not any('methods' in t for t in src['transitions']) and not any('method' in c_ for c_ in src['cells'])
    for want in x.get('legend_contains', []):
        ok = ok and any(want['text'] in s for s in legend_lines(out).get(want['code'], []))
    if 'bar_label_endswith' in x:
        g = bar(out, x['bar_label_endswith']['cell'])
        ok = ok and g is not None and [t.text for t in g.iter(T)][1].endswith(x['bar_label_endswith']['suffix'])
    if 'bar_label_shortened' in x:
        g = bar(out, x['bar_label_shortened']['cell'])
        ok = ok and x['bar_label_shortened']['full'] not in [t.text for t in g.iter(T)][1]
    if 'bar_title_contains' in x:
        g = bar(out, x['bar_title_contains']['cell'])
        ok = ok and all(s in g.find(f'{{{NS}}}title').text for s in x['bar_title_contains']['texts'])
    if 'marker_methods' in x:
        got = {}
        for root in svgs(out):
            for g in root.iter(G):
                if g.get('data-vp07-code') and g.get('data-vp07-methods'):
                    got[g.get('data-vp07-code')] = g.get('data-vp07-methods')
        ok = ok and all(got.get(k) == v for k, v in x['marker_methods'].items())
    if x.get('fills_as_without_methods'):
        inp = c['input']
        s6, _ = fp(inp, strip7(inp['context']))
        _, f6 = panels(s6, inp['then'], tmp+'/b')
        fills = lambda roots: {e.get('fill') for r in roots for e in r.iter() if e.get('fill')}  # noqa: E731
        ok = ok and fills(svgs(out)) == fills(svgs({'files': f6}))
    if x.get('layer_bands'):
        ok = ok and any(g.get('data-vp07-layer') for r in svgs(out) for g in r.iter(G))
    if x.get('coverage_complete'):
        ok = ok and out['report']['coverage']['status'] == 'COMPLETE'
    if x.get('panel_methods_complete'):
        want = {(t['id'], b['declaration_ref']) for t in src['transitions'] for b in t.get('methods', [])}
        want |= {(c_['id'], c_['method']['declaration_ref']) for c_ in src['cells'] if 'method' in c_}
        got = set()
        for e in out['report']['panel_ledger']:
            m = e['panel_report'].get('methods', {})
            got |= {(o, b['declaration_ref']) for o, bs in m.get('transitions', {}).items() for b in bs}
            got |= {(o, b['declaration_ref']) for o, b in m.get('cells', {}).items()}
        ok = ok and bool(want) and got == want
    for want in x.get('hidden_includes', []):
        ok = ok and any(w['code'] == 'VP07_METHOD_ARGUMENT_HIDDEN' and w['owner'] == want['owner'] and w['role'] == want['role']
                        for w in out['warnings'])
    for tid in x.get('transitions_absent', []):
        ok = ok and all(t['id'] != tid for t in src['transitions'])
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['forbidden_codes'], c['expect']) == \
            (o['expected_status'], o['required_codes'], o['forbidden_codes'], o['expect']), c['id']+': vector differs from oracle'
        msg = ''
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP07Error as e:
                out, status, codes, msg = None, 'FAIL', [e.code], str(e)
            ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) \
                and not any(k in codes for k in c['forbidden_codes'])
            if ok and status == 'PASS':
                ok = check(c, out, tmp)
            if ok and status == 'FAIL':
                ok = all(s in msg for s in c['expect'].get('message_contains', []))
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg[:110])
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
