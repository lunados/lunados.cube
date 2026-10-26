#!/usr/bin/env python3
"""Build fixtures/golden_gap_synthetic.json (P1.10.1-10): the P1.10 golden as /6 plus one unexplained end.

Expected values are declared by design: G-pos as /6 stays PASS; the variant adds
acme:website hosted-by acme:dns holding only in p0, p1 (dns is never retired) → exactly one gap.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
src = {c['id']: c for c in json.loads((HERE.parent/'migration-profile-v1/fixtures/golden_migration_synthetic.json').read_text('utf-8'))['cases']}
pos = copy.deepcopy(src['G-pos']); pos['context']['format'] = 'aiaeao.cube.binding-context/6'
gap = copy.deepcopy(pos)
gap['context']['migration_plans'][0]['dependencies'].append(
    {'dependency_id': 'd14', 'subject': 'acme:website', 'predicate_id': 'hosted-by', 'object': 'acme:dns', 'kind': 'dns',
     'holds_in': ['p0', 'p1'], 'witness_ref': 'synthetic:inventory#d14'})
pos.update(id='GG-pos', description='P1.10 golden G-pos as /6: every end is explained', expected_overall='PASS', required_codes=[])
gap.update(id='GG-gap', description='d14 ends at p1 before target p2; acme:dns is never retired; no successor, drop or reason',
           expected_overall='UNRESOLVED', required_codes=['P1_MIGRATION_DEPENDENCY_GAP'], expected_gap_count=1)
for c in (pos, gap):
    c.pop('expected_codes', None)
out = {'format': 'aiaeao.cube.p1.10.1-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic; derived from P1.10 golden_migration_synthetic.json',
       'cases': [pos, gap]}
(HERE/'fixtures/golden_gap_synthetic.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n', 'utf-8')
print('wrote golden')
