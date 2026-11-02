#!/usr/bin/env python3
"""Build fixtures/golden_cells.json (VP10-08): one synthetic DSM-03-shaped /8 context, en and de.

Declarations: pair (m:validator, m:parser) and outgoing references at m:printer. With --hide-empty cols the
column m:printer has neither marked nor checked cells and is hidden by name. The context also passes P1.12
(tests/test_vp10.py). Expected counts are declared by design; no client data.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
R1 = json.loads((REPO/'docs/09-Research/visual-check/renders/R-1.json').read_text('utf-8'))


def context():
    c = copy.deepcopy(R1['context'])
    c['format'] = 'aiaeao.cube.binding-context/8'
    c['context_id'] = 'golden-vp10'
    c['coverage_declarations'] = [
        {'declaration_id': 'cv-vp', 'scope': 'pair', 'subject': 'm:validator', 'predicate_id': 'references', 'object': 'm:parser',
         'witness_ref': 'synthetic:survey#validator-parser'},
        {'declaration_id': 'cv-pr-out', 'scope': 'referent_relation_direction', 'referent': 'm:printer', 'predicate_id': 'references',
         'direction': 'outgoing', 'witness_ref': 'synthetic:survey#printer-row'}]
    return c


EXPECT = {'marked': 4, 'checked': 3, 'unknown': 2, 'element': 3, 'hidden': 4}
CASES = [{'id': f'GC-{loc}', 'locale': None if loc == 'en' else loc, 'hide_empty': 'cols', 'plan_id': R1['plan_id'], 'predicate': 'references',
          'context': context(), 'expected_state_counts': EXPECT, 'expected_hidden_cols': ['m:printer'],
          'expected_checked': {'m:validator|m:parser': 'pair', 'm:printer|m:parser': 'row', 'm:printer|m:resolver': 'row'}}
         for loc in ('en', 'de')]
(HERE/'fixtures/golden_cells.json').write_text(json.dumps({'format': 'aiaeao.p2.vp10-golden/1', 'reference_version': 'v9.4',
                                                           'source': 'synthetic (MILE-003 R-1 DSM plan as /8); no client data', 'cases': CASES},
                                                          ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('wrote', len(CASES), 'golden cases')
