#!/usr/bin/env python3
"""Generate context-v7.schema.json as a strict superset of context-v6.schema.json (P1.11 D-1, MB-1…MB-3)."""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
v6 = json.loads((HERE.parent/'migration-profile-v2/context-v6.schema.json').read_text('utf-8'))
s = copy.deepcopy(v6)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:7'
s['title'] = 'AIAEAO Cube binding context /7 (P1.11 migration method catalog and method bindings)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/7'}
s['properties']['method_profile_refs'] = {
    'type': 'array', 'uniqueItems': True, 'maxItems': 8,
    'items': {'oneOf': [{'type': 'string', 'minLength': 1},
                        {'type': 'object', 'additionalProperties': False, 'required': ['profile_id'],
                         'properties': {'profile_id': {'type': 'string', 'minLength': 1}}}]},
    'description': 'Pinned method catalogs imported by reference (MC-1, MI-1); contracts are scoped to scope_ref on import'}
s['$defs']['method_binding'] = {
    'type': 'object', 'additionalProperties': False, 'required': ['method_id', 'arguments'],
    'properties': {'method_id': {'type': 'string', 'minLength': 1, 'maxLength': 120},
                   'arguments': {'type': 'object', 'minProperties': 1, 'additionalProperties': {'type': 'string', 'minLength': 1}},
                   'witness_ref': {'type': 'string', 'minLength': 1}},
    'description': 'Declared method binding: role -> referent ref (MB-1…MB-3); never executed by the Cube'}
s['$defs']['transition']['properties']['methods'] = {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/method_binding'}}
s['$defs']['dependency']['properties']['method'] = {'$ref': '#/$defs/method_binding'}
(HERE/'context-v7.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('wrote context-v7.schema.json')
