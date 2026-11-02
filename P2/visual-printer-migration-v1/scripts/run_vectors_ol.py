#!/usr/bin/env python3
"""Check the fixed OL-01…OL-12 G6 vectors against their independent oracle.

Status and codes, and for every PASS case each drawn edge in every panel SVG: origin, line style and the origin text
at the end of its label (TASK-068: the oracle's per-edge expectations are checked here, not only in the unit tests).
"""
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'P3/adapters/mcp-local'))
sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402

VEC = json.loads((HERE / 'fixtures/ol01_ol12_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_ol01_ol12.json').read_text('utf-8'))['cases']}


NS = '{http://www.w3.org/2000/svg}'


def drawn_edges(result):
    """Map ledger cell ID -> set of (origin, style, label) over all panels."""
    ref2cell = {e['declaration_ref']: e['cell_id'] for e in result['report']['origin_ledger']}
    out = {}
    for p in result['panels']:
        for g in ET.fromstring(p['svg'].encode('utf-8')).iter(NS+'g'):
            if g.get('data-edge-id'):
                out.setdefault(ref2cell[g.get('data-declaration-ref')], set()).add(
                    (g.get('data-vp07-origin'), g.get('data-vp07-edge-style'), g.find(NS+'text').text))
    return out


def edge_problems(oracle_edges, drawn):
    probs, named = [], {e.get('edge') or e.get('edge_dependency') for e in oracle_edges} - {None}
    for e in oracle_edges:
        key = e.get('edge') or e.get('edge_dependency')
        cells = [key] if key else [k for k in drawn if k not in named]   # 'other_dependencies'
        if key and key not in drawn:
            probs.append(f'{key} not drawn')
        for k in cells:
            for origin, style, label in drawn.get(k, ()):
                if (origin, style) != (e['origin'] if key else 'unbound', e['style']) or not label.endswith(e['text']):
                    probs.append(f'{k}: {origin}/{style}/{label!r}')
    if any('edge' in e for e in oracle_edges) and set(drawn) != named:
        probs.append(f'drawn {sorted(drawn)} != oracle {sorted(named)}')
    return probs


def run(case):
    try:
        source = g6.plan_source(**case['plan_source'])
        result = g6.plan_views(source['source'], **case['plan_views'])
        return result['report']['status'], [w['code'] for w in result['report']['warnings']], drawn_edges(result)
    except g6.PlanFailure as e:
        return 'FAIL', [e.diagnostic['code']], {}


def main():
    assert {c['id'] for c in VEC} == set(ORACLE)
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['edges'], c['also']) == (
            o['expected_status'], o['required_codes'], o['edges'], o['also'])
        status, codes, drawn = run(c)
        probs = edge_problems(o['edges'], drawn) if o['expected_status'] == 'PASS' else []
        ok = status == o['expected_status'] and set(o['required_codes']) <= set(codes) and not probs
        print('PASS' if ok else 'FAIL', c['id'], status, codes, f'{len(drawn)} edges', *probs)
        bad += not ok
    print(f'{len(VEC)-bad}/{len(VEC)} status, code and per-edge matches')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
