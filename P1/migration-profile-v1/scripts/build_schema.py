#!/usr/bin/env python3
"""Generate context-v5.schema.json as a strict superset of context-v4.schema.json."""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
v4 = json.loads((HERE.parent/'comparison-profile-v1/context-v4.schema.json').read_text('utf-8'))
s = copy.deepcopy(v4)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:5'
s['title'] = 'AIAEAO Cube binding context /5 (P1.10 declared migration profile)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/5'}
S = {'type': 'string', 'minLength': 1}
ARR = lambda item, mn=0: {'type': 'array', 'minItems': mn, 'uniqueItems': True, 'items': item}
d = s['$defs']
LIB = copy.deepcopy(d['method']['properties']['library_ref'])
d['predicate_profile_ref'] = {'oneOf': [
    S,
    {'type': 'object', 'additionalProperties': False, 'required': ['profile_id'],
     'properties': {'profile_id': S, 'library_ref': LIB}}]}
d['phase'] = {'type': 'object', 'additionalProperties': False, 'required': ['phase_id', 'role'],
              'properties': {'phase_id': S, 'role': {'enum': ['current', 'intermediate', 'target']}}}
d['transition_t'] = {'type': 'object', 'additionalProperties': False, 'required': ['role'],
                     'properties': {'role': S, 'value': {'type': 'string', 'description': 'uninterpreted (PH-1)'}}}
d['transition'] = {'type': 'object', 'additionalProperties': False,
                   'required': ['transition_id', 'at_phase', 'retires', 'introduces'],
                   'properties': {'transition_id': S, 'at_phase': S, 'retires': ARR(S), 'introduces': ARR(S),
                                  'T': {'$ref': '#/$defs/transition_t'}, 'witness_ref': S}}
d['dependency'] = {'type': 'object', 'additionalProperties': False,
                   'required': ['dependency_id', 'subject', 'predicate_id', 'object', 'kind', 'holds_in'],
                   'not': {'required': ['successor_ref', 'dropped'], 'properties': {'dropped': {'const': True}}},
                   'properties': {'dependency_id': S, 'subject': S, 'predicate_id': S, 'object': S,
                                  'kind': {'enum': ['job', 'sync', 'dns', 'auth', 'account', 'api', 'data', 'docs', 'other']},
                                  'holds_in': ARR(S, 1), 'successor_ref': S, 'dropped': {'type': 'boolean'},
                                  'schedule': S, 'witness_ref': S}}
d['migration_plan'] = {'type': 'object', 'additionalProperties': False,
                       'required': ['plan_id', 'revision', 'scope', 'origin', 'phases', 'transitions', 'dependencies'],
                       'properties': {'plan_id': S, 'revision': S, 'scope': S,
                                      'origin': {'enum': ['illustrative_fixture', 'external_declaration_unverified']},
                                      'phases': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/phase'}},
                                      'transitions': {'type': 'array', 'maxItems': 1000, 'items': {'$ref': '#/$defs/transition'}},
                                      'dependencies': {'type': 'array', 'maxItems': 5000, 'items': {'$ref': '#/$defs/dependency'}}}}
s['properties']['predicate_profile_refs'] = {'type': 'array', 'maxItems': 8, 'uniqueItems': True,
                                             'items': {'$ref': '#/$defs/predicate_profile_ref'}}
s['properties']['migration_plans'] = {'type': 'array', 'maxItems': 64, 'items': {'$ref': '#/$defs/migration_plan'}}
(HERE/'context-v5.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('wrote context-v5.schema.json')
