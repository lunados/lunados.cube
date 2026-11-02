#!/usr/bin/env python3
"""Build the /9 schema by adding P1.13 fields to the frozen /8 schema."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
v8 = json.loads((HERE.parent / 'coverage-instance-profile-v1/context-v8.schema.json').read_text('utf-8'))
s = copy.deepcopy(v8)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:9'
s['title'] = 'AIAEAO Cube binding context /9 (P1.13 declared control flow and trace binding)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/9'}
STR = {'type': 'string', 'minLength': 1, 'maxLength': 512}
s['$defs']['referent']['properties']['at_gateway'] = dict(STR, description='TB-1: gateway position of a token')
s['$defs']['predicate']['properties']['control_flow_role'] = {'enum': ['routing', 'on_flow']}
s['$defs']['control_flow_outgoing'] = {
    'type': 'object', 'additionalProperties': False, 'required': ['flow', 'target'],
    'properties': {'flow': STR, 'target': STR, 'order': {'type': 'integer', 'minimum': 1},
                   'condition_ref': STR, 'default': {'type': 'boolean'}},
}
s['$defs']['control_flow_gateway'] = {
    'type': 'object', 'additionalProperties': False, 'required': ['gateway', 'type', 'incoming', 'outgoing'],
    'properties': {'gateway': STR, 'type': STR,
                   'incoming': {'type': 'array', 'minItems': 1, 'items': STR},
                   'outgoing': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/control_flow_outgoing'}}},
}
s['properties']['control_flow'] = {
    'type': 'object', 'additionalProperties': False, 'required': ['gateways'],
    'properties': {'gateways': {'type': 'array', 'maxItems': 512,
                                'items': {'$ref': '#/$defs/control_flow_gateway'}}},
}
(HERE / 'context-v9.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('wrote context-v9.schema.json')
