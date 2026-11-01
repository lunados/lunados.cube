#!/usr/bin/env python3
"""Build fixtures/golden_coverage_instance.json (P1.12-10): one synthetic context with all three P1.12 blocks.

The trace context of K-14 (shared scope bpmn:trace, two instances, flows, gateway) carries coverage
declarations for both flows of i1, a join activation rule for i1, typed instance membership on every token
and requires_same_instance on joins. GC-pos joins two i1 tokens -> PASS. GC-mixed adds a join rule for i2
without coverage and joins across instances -> FAIL (exactly one P1_INSTANCE_MISMATCH and one
P1_COVERAGE_UNDECLARED). Expected values are declared by design. No client data.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
K = {c['id']: c for c in json.loads((HERE/'fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases']}
SAME = 'rel("joins",Y:α:Evidence["bpmn:i1/tok-stock"],Y:α:Evidence["bpmn:i1/tok-credit"])'
CROSS = 'rel("joins",Y:α:Evidence["bpmn:i1/tok-stock"],Y:α:Evidence["bpmn:i2/tok-credit"])'


def pos():
    ctx = copy.deepcopy(K['K-14']['context'])
    ctx['context_id'] = 'golden-p112'
    for p in ctx['predicate_contracts']:
        if p['predicate_id'] == 'joins':
            p['requires_same_instance'] = True
    return ctx


def mixed():
    ctx = pos()
    r = copy.deepcopy(ctx['population_rules'][0]); r['rule_id'] = 'pr-join-i2'; r['instance_ref'] = 'bpmn:i2'
    ctx['population_rules'].append(r)
    return ctx


CASES = [
    {'id': 'GC-pos', 'description': 'coverage for both i1 flows, join rule i1, typed instances, joins within i1',
     'input_text': SAME, 'input_format': 'acg_text', 'context': pos(), 'expected_overall': 'PASS', 'required_codes': [],
     'expected_blocks': {'coverage_declarations': 2, 'population_rules': 1, 'instance_refs': 3}},
    {'id': 'GC-mixed', 'description': 'GC-pos plus an uncovered join rule for i2 and a cross-instance joins statement',
     'input_text': CROSS, 'input_format': 'acg_text', 'context': mixed(), 'expected_overall': 'FAIL',
     'required_codes': ['P1_INSTANCE_MISMATCH', 'P1_COVERAGE_UNDECLARED'],
     'expected_code_count': {'P1_INSTANCE_MISMATCH': 1, 'P1_COVERAGE_UNDECLARED': 1}},
]


def main():
    out = {'format': 'aiaeao.cube.p1.12-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (K-14 trace context); no client data',
           'cases': CASES}
    (HERE/'fixtures/golden_coverage_instance.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('wrote', len(CASES), 'golden cases')


if __name__ == '__main__':
    main()
