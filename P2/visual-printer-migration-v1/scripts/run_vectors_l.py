#!/usr/bin/env python3
"""Run L-01..L-13 (VP-07.2) against vpmigration through its Python API.

Exit 0 only if every case matches the independent oracle (oracles/independent_l01_l13.json).
"""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, encode, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/l01_l13_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_l01_l13.json').read_text('utf-8'))['cases']}
G = f'{{{NS}}}g'
P071 = 'P2-VP-MIGRATION/0.7.1'


def panels(src, t, tmp):
    report, files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))
    check_panels(publish_dir(files, Path(tmp)/'panels'))
    return report, files


def run(c, tmp):
    inp = c['input']
    if c['op'] == 'panels':
        rep, files = panels(inp['source'], inp, tmp)
        return {'warnings': rep['warnings'], 'report': rep, 'files': files}
    src, mapping = from_plan(inp['context'], inp['plan_id'], tracks=inp.get('tracks'), layers=inp.get('layers'))
    out = {'source': src, 'mapping': mapping, 'warnings': list(mapping.get('warnings', []))}
    if 'then' in inp:
        rep, files = panels(src, inp['then'], tmp)
        out.update(report=rep, files=files, warnings=out['warnings']+rep['warnings'])
    return out


def phases_rows(out):
    """Row order of the first phases panel as drawn (data-item-id groups in document order)."""
    svg = out['files']['panel-01.svg']
    return [g.get('data-item-id') for g in ET.fromstring(svg).iter(G) if g.get('data-item-id')]


def check(c, out, tmp):
    x, ok = c['expect'], True
    src = out.get('source')
    if 'source_profile' in x:
        ok = ok and src['profile'] == x['source_profile']
    if 'layer_order' in x:
        ok = ok and src['layer_order'] == x['layer_order']
    if x.get('unassigned_last'):
        ok = ok and src['layer_order'][-1] == 'unassigned' and any(r['layer'] == 'unassigned' for r in src['rows'])
    if 'row_order' in x:
        ok = ok and phases_rows(out) == x['row_order']
        ok = ok and out['report']['panel_ledger'][0]['shown_row_ids'] == x['row_order']
    if x.get('matches_071_from_plan'):
        inp = c['input']
        ref, refmap = from_plan(inp['context'], inp['plan_id'], profile=P071)
        ok = ok and encode(src) == encode(ref) and encode(out['mapping']) == encode(refmap)
        t = inp['then']
        ok = ok and print_panels(ref, t['view'], t['partition'], t['granularity'])[1] == out['files']
    if 'flow_order' in x:
        want = x['flow_panel']
        hit = None
        for e in out['report']['panel_ledger']:
            if e['step'] == want['step'] and e['key_values'] == [want['key']]:
                hit = e
        inp = json.loads(out['files'][hit['panel']+'.input.json'])
        ok = ok and inp['job']['source_bundle']['view_plan']['order'] == x['flow_order']
        cap = [g for g in ET.fromstring(out['files'][hit['panel']+'.svg']).iter(G) if g.get('data-vp07-layers')]
        ok = ok and len(cap) == 1 and cap[0].get('data-vp07-layers').split() == x['caption_layers']
    if 'layer_bands' in x:
        bands = [g for g in ET.fromstring(out['files']['panel-01.svg']).iter(G) if g.get('data-vp07-layer')]
        ok = ok and [b.get('data-vp07-layer') for b in bands] == x['layer_bands']
        ok = ok and all(r.get('fill') == x['band_fill'] for b in bands for r in b.iter(f'{{{NS}}}rect'))
    if x.get('no_panel_mixes_layers'):
        lay = {r['id']: r['layer'] for r in src['rows']}
        ok = ok and all(len({lay[r] for r in e['shown_row_ids']}) == 1 for e in out['report']['panel_ledger'])
    if x.get('coverage_complete'):
        ok = ok and out['report']['coverage']['status'] == 'COMPLETE'
    if x.get('outer_ledger_complete'):
        ok = ok and all(o['status'] == 'COMPLETE' for o in out['report']['outer_ledger'])
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
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)), msg)
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
