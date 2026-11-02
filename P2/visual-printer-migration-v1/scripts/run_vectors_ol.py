#!/usr/bin/env python3
"""Check the fixed OL-01…OL-12 G6 vectors against their independent oracle."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'P3/adapters/mcp-local'))
sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402

VEC = json.loads((HERE / 'fixtures/ol01_ol12_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_ol01_ol12.json').read_text('utf-8'))['cases']}


def run(case):
    try:
        source = g6.plan_source(**case['plan_source'])
        result = g6.plan_views(source['source'], **case['plan_views'])
        return result['report']['status'], [w['code'] for w in result['report']['warnings']]
    except g6.PlanFailure as e:
        return 'FAIL', [e.diagnostic['code']]


def main():
    assert {c['id'] for c in VEC} == set(ORACLE)
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['edges'], c['also']) == (
            o['expected_status'], o['required_codes'], o['edges'], o['also'])
        status, codes = run(c)
        ok = status == o['expected_status'] and set(o['required_codes']) <= set(codes)
        print('PASS' if ok else 'FAIL', c['id'], status, codes)
        bad += not ok
    print(f'{len(VEC)-bad}/{len(VEC)} status/code matches')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
