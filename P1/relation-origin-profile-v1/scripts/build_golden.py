#!/usr/bin/env python3
"""Materialize a synthetic P1.14 golden from fixed HO inputs."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
vectors = json.loads((HERE / 'fixtures/ho01_ho12_materialized.json').read_text('utf-8'))['cases']
cases = {c['id']: c for c in vectors}
golden = {
    'format': 'aiaeao.cube.p1.14-golden/1',
    'source': 'synthetic MILE-007 C4 declarations; no client data',
    'context': copy.deepcopy(cases['HO-02']['context']),
    'relations': [
        {'id': c['id'], 'origin': origin, 'basis_kind': kind, 'input_text': c['input_text'],
         'expected_status': 'PASS'}
        for c, origin, kind in ((cases['HO-08'], 'declared', None),
                                (cases['HO-02'], 'derived', 'statements'),
                                (cases['HO-03'], 'derived', 'projection_record'),
                                (cases['HO-07'], 'unknown', None))],
}
(HERE / 'fixtures/golden_relation_origin.json').write_text(json.dumps(golden, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('wrote golden_relation_origin.json')
