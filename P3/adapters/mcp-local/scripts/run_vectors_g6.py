#!/usr/bin/env python3
"""Run K-01..K-18 (G6) through the tool layer (`plan_views`, `surface`) against the oracle.

Byte equality is judged against the unchanged CLIs (scripts/g6_cli.py). Exit 0 only if every case matches.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]; ROOT = BASE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE/'scripts'))
from aiaeao_mcp_local import plan_views as PV, surface, bridge  # noqa: E402
import g6_cli as CLI  # noqa: E402
import pin_g6_baseline as PIN  # noqa: E402
import parity_g6 as PAR  # noqa: E402
from vpmigration.api import to_files  # noqa: E402
from vpmigration.common import encode  # noqa: E402

DOC = json.loads((BASE/'tests/g6/k01_k18_materialized.json').read_text('utf-8'))
ORACLE = {c['id']: c for c in json.loads((BASE/'tests/g6/independent_k01_k18.json').read_text('utf-8'))['cases']}
VEC = {c['id']: c for c in DOC['cases']}


def fixture(key):
    f = DOC['fixtures'][key]
    raw = (ROOT/f['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == f['sha256'], 'fixture changed since materialisation: '+f['path']
    return json.loads(raw)


def source_of(sf, printer):
    fx = fixture(sf['fixture'])
    if sf['fixture'] == 'gseq':
        return fx['sequence_source']
    return PV.plan_source(fx['context'], fx['plan_id'], printer, profile=sf.get('profile'))['source']


def view_kw(v):
    return {k: v[k] for k in ('partition', 'lens', 'rows', 'cols', 'overflow') if k in v}


def cli_kw(v):
    return {k: v[k] for k in ('view', 'partition', 'granularity', 'lens', 'rows', 'cols', 'overflow') if k in v and not (k == 'view' and v[k] in ('cube.sequence', 'cube.axes'))}


def views_of(inp):
    src = source_of(inp['source_from'], inp['printer'])
    v = inp['view']
    return src, PV.plan_views(src, v['view'], v['granularity'], **view_kw(v))


def run(cid):
    """→ ('PASS', facts) or ('ERROR', diagnostic)."""
    inp = VEC[cid]['input']
    k = inp['kind']
    try:
        if k == 'views_vs_cli':
            src, res = views_of(inp)
            cli = CLI.print_panels(inp['printer'], src, **cli_kw(inp['view']))
            files = to_files(res)
            facts = {'equal_cli_files': files == cli, 'coverage': res['report']['coverage']['status']}
            facts['methods_lines'] = any('data-vp07-methods-line' in p['svg'] for p in res['panels'])
            facts['binding_coverage'] = res['report'].get('binding_coverage', {}).get('status')
            return 'PASS', facts
        if k in ('check_vs_cli', 'check', 'deterministic', 'check_tampered'):
            base = VEC[inp['like']]['input']
            src, res = views_of(base)
            if k == 'deterministic':
                _, again = views_of(base)
                return 'PASS', {'deterministic': PV.canonical(res) == PV.canonical(again)}
            if k == 'check_tampered':
                p = res['panels'][0]
                p['svg'] = p['svg'].replace('</svg>', '<!-- x --></svg>', 1)
            chk = PV.plan_check(res)
            facts = {'check_status': chk['status']}
            if k == 'check_vs_cli':
                cli = json.loads(CLI.check_panels(base['printer'], to_files(res)))
                facts['check_equals_cli'] = {x: y for x, y in chk.items() if x != 'printer'} == cli
            return 'PASS', facts
        if k == 'baseline':
            want = json.loads(PIN.OUT.read_text('utf-8'))['digests']
            return 'PASS', {'baseline_unchanged': PIN.collect() == want}
        if k == 'source_vs_cli':
            fx = fixture(inp['fixture'])
            res = PV.plan_source(fx['context'], fx['plan_id'], inp['printer'], profile=inp['profile'])
            src_b, map_b = CLI.from_plan(inp['printer'], fx['context'], fx['plan_id'], profile=inp['profile'])
            same = encode(res['source']) == src_b and (map_b is None or encode(res['mapping']) == map_b)
            return 'PASS', {'source_equals_cli': same, 'profile': res['profile']}
        if k == 'tool':
            fn = {'cube_plan_source': PV.plan_source}[inp['tool']]
            return 'PASS', fn(**inp['args'])
        if k == 'tool_views':
            base = VEC[inp['like']]['input']
            src = source_of(base['source_from'], base['printer'])
            v = {**base['view'], **inp['override']}
            return 'PASS', PV.plan_views(src, v['view'], v['granularity'], **view_kw(v))
        if k == 'tool_views_avec':
            a = {c['id']: c for c in fixture('avec')['cases']}[inp['case']]['input']
            src = PV.plan_source(a['context'], a['plan_id'], 'vpaxes')['source']
            v = inp['view']
            return 'PASS', PV.plan_views(src, v['view'], v['granularity'], **view_kw(v))
        if k == 'tool_views_context':
            src = PV.plan_source(inp['context'], inp['plan_id'], inp['printer'])['source']
            v = inp['view']
            return 'PASS', PV.plan_views(src, v['view'], v['granularity'], **view_kw(v))
        if k == 'parity':
            total, bad = PAR.sweep()
            return 'PASS', {'parity_all_equal': not bad and total > 0, 'total': total, 'bad': bad}
        if k == 'surface':
            card = surface.discover_surface_local()
            want = json.loads(PIN.OUT.read_text('utf-8'))['digests']
            return 'PASS', {'tools': card['mcp']['tools'], 'release': card['release']['version'],
                            'plan_views_section': card['domains']['P2'].get('plan_views', {}).get('tools') == list(PV.TOOLS),
                            'legacy_card_unchanged': PIN.sha(encode(bridge.get_capabilities())) == want['legacy:cube_get_capabilities'],
                            'g4_base_surface_unchanged': PIN.sha(encode(surface.discover_surface())) == want['g4:discover_surface']}
        raise AssertionError('unknown kind '+k)
    except PV.PlanFailure as e:
        return 'ERROR', e.diagnostic


def check(cid, status, out):
    o = ORACLE[cid]
    if status == 'ERROR':
        x = o['expect']
        ok = o['expected_status'] == 'ERROR' and out['code'] == o['expected_code']
        if x.get('full_diagnostic'):
            ok = ok and all(out.get(f) for f in ('code', 'stage', 'message')) and out.get('epistemic_warrant') == 'NOT_EVALUATED'
        if x.get('size_and_hint'):
            ok = ok and out['size_bytes'] > out['limit_bytes'] and 'hint' in out
        return ok
    if o['expected_status'] != 'PASS':
        return False
    return all(out.get(k) == v for k, v in o['expect'].items())


def main():
    assert set(VEC) == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for cid in sorted(VEC):
        status, out = run(cid)
        ok = check(cid, status, out)
        bad += not ok
        note = out['code'] if status == 'ERROR' else {k: v for k, v in out.items() if k in ORACLE[cid]['expect'] or k == 'total'}
        print('PASS' if ok else 'FAIL', cid, ORACLE[cid]['expected_status'], ORACLE[cid]['expected_code'] or '', '| got', status, note)
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
