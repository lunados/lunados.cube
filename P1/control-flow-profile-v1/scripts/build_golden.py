#!/usr/bin/env python3
"""Build one synthetic golden with model, token binding and P1.12 coverage."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
source = json.loads((HERE / 'fixtures/kf01_kf09_materialized.json').read_text('utf-8'))['cases'][0]
case = copy.deepcopy(source)
case['id'] = 'GOLDEN-CONTROL-FLOW'
case['context']['context_id'] = 'p113-golden-control-flow'
case['context']['coverage_declarations'] = [{
    'declaration_id': 'golden-route-coverage', 'scope': 'referent_relation_direction',
    'referent': 'bpmn:i1/tok-route', 'predicate_id': 'routedTo', 'direction': 'outgoing',
    'instance_ref': 'bpmn:i1', 'witness_ref': 'synthetic:golden#survey'}]
out = {'format': 'aiaeao.cube.p1.13-golden/1', 'reference_version': 'v9.4', 'cases': [case]}
(HERE / 'fixtures/golden_control_flow.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('wrote golden_control_flow.json')
