#!/usr/bin/env python3
"""Generate context-v6.schema.json as a strict superset of context-v5.schema.json (P1.10.1 D-1, DG-6)."""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
v5 = json.loads((HERE.parent/'migration-profile-v1/context-v5.schema.json').read_text('utf-8'))
s = copy.deepcopy(v5)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:6'
s['title'] = 'AIAEAO Cube binding context /6 (P1.10.1 migration profile revision: dependency gap)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/6'}
s['$defs']['dependency']['properties']['ends_reason'] = {
    'type': 'string', 'minLength': 1, 'maxLength': 40,
    'description': 'Declared reason why the dependency ends before the target phase; explains a gap only for scope_end | replaced_outside_plan | other with witness_ref (DG-6)'}
(HERE/'context-v6.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('wrote context-v6.schema.json')
