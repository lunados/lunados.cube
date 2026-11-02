#!/usr/bin/env python3
"""Generate context-v8.schema.json as a strict superset of context-v7.schema.json (P1.12 CV-1, PR-1, IN-1, IN-2)."""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
v7 = json.loads((HERE.parent/'migration-methods-v1/context-v7.schema.json').read_text('utf-8'))
s = copy.deepcopy(v7)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:8'
s['title'] = 'AIAEAO Cube binding context /8 (P1.12 declared coverage, population rules, typed instance membership)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/8'}
STR = {'type': 'string', 'minLength': 1, 'maxLength': 512}
DIR = {'enum': ['outgoing', 'incoming']}

s['$defs']['referent']['properties']['instance_ref'] = dict(
    STR, description='IN-1: declared referent of concept Y:identified-object:bounded-execution (checked by the validator)')
s['$defs']['predicate']['properties']['requires_same_instance'] = {
    'type': 'boolean', 'description': 'IN-2: both endpoints must carry the same instance_ref (default false)'}

s['$defs']['coverage_declaration'] = {'oneOf': [
    {'type': 'object', 'additionalProperties': False,
     'required': ['declaration_id', 'scope', 'referent', 'predicate_id', 'direction', 'witness_ref'],
     'properties': {'declaration_id': STR, 'scope': {'const': 'referent_relation_direction'}, 'referent': STR, 'predicate_id': STR,
                    'direction': DIR, 'instance_ref': STR, 'witness_ref': STR}},
    {'type': 'object', 'additionalProperties': False,
     'required': ['declaration_id', 'scope', 'subject', 'predicate_id', 'object', 'witness_ref'],
     'properties': {'declaration_id': STR, 'scope': {'const': 'pair'}, 'subject': STR, 'predicate_id': STR, 'object': STR,
                    'instance_ref': STR, 'witness_ref': STR}}],
    'description': 'CV-1, CV-2, CV-4: declared survey scope (no view-level declaration, D-2); a statement of scope, not proof (CV-5)'}

s['$defs']['population_rule'] = {'oneOf': [
    {'type': 'object', 'additionalProperties': False,
     'required': ['rule_id', 'kind', 'referent', 'predicate_id', 'direction', 'min', 'witness_ref'],
     'properties': {'rule_id': STR, 'kind': {'const': 'count'}, 'referent': STR, 'predicate_id': STR, 'direction': DIR,
                    'min': {'type': 'integer', 'minimum': 0}, 'max': {'type': 'integer', 'minimum': 0}, 'instance_ref': STR, 'witness_ref': STR}},
    {'type': 'object', 'additionalProperties': False, 'required': ['rule_id', 'kind', 'predicate_id', 'witness_ref'],
     'anyOf': [{'required': ['subject']}, {'required': ['object']}],
     'properties': {'rule_id': STR, 'kind': {'const': 'absence'}, 'subject': STR, 'predicate_id': STR, 'object': STR,
                    'instance_ref': STR, 'witness_ref': STR}},
    {'type': 'object', 'additionalProperties': False,
     'required': ['rule_id', 'kind', 'instance_ref', 'gateway', 'predicate_id', 'incoming_flows', 'witness_ref'],
     'properties': {'rule_id': STR, 'kind': {'const': 'join_activation'}, 'instance_ref': STR, 'gateway': STR, 'predicate_id': STR,
                    'incoming_flows': {'type': 'array', 'minItems': 1,
                                       'items': {'type': 'object', 'additionalProperties': False, 'required': ['flow'],
                                                 'properties': {'flow': STR, 'min': {'type': 'integer', 'minimum': 1}}}},
                    'witness_ref': STR}}],
    'description': 'PR-1: declared population rule; P1 checks shape, resolution and coverage only, never evaluates (PR-2, D-6). '
                   'max >= min and unique IDs/flows are checked by the validator'}

s['properties']['coverage_declarations'] = {'type': 'array', 'maxItems': 2048, 'items': {'$ref': '#/$defs/coverage_declaration'}}
s['properties']['population_rules'] = {'type': 'array', 'maxItems': 512, 'items': {'$ref': '#/$defs/population_rule'}}
(HERE/'context-v8.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('wrote context-v8.schema.json')
