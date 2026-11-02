#!/usr/bin/env python3
"""Generate /10 and statement-set/2 schemas from frozen predecessor shapes."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
v9 = json.loads((HERE.parent / 'control-flow-profile-v1/context-v9.schema.json').read_text('utf-8'))
s = copy.deepcopy(v9)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:10'
s['title'] = 'AIAEAO Cube binding context /10 (P1.14 declared relation origin)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/10'}
STRING = {'type': 'string', 'minLength': 1, 'maxLength': 512}
SHA = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
s['$defs']['predicate']['properties']['origin_binding'] = {'const': 'required'}
dep = s['$defs']['dependency']['properties']
dep['origin'] = {}  # Invalid values reach the P1.14 semantic rule.
dep['basis'] = {}
s['$defs']['origin_basis_statements'] = {
    'type': 'object', 'additionalProperties': False,
    'required': ['basis_id', 'kind', 'set_id', 'statement_ids'],
    'properties': {'basis_id': STRING, 'kind': {'const': 'statements'}, 'set_id': STRING,
                   'statement_ids': {'type': 'array', 'minItems': 1, 'maxItems': 5000,
                                     'uniqueItems': True, 'items': STRING}, 'witness_ref': STRING},
}
s['$defs']['origin_basis_projection'] = {
    'type': 'object', 'additionalProperties': False,
    'required': ['basis_id', 'kind', 'record_sha256', 'statement_id', 'library_ref'],
    'properties': {'basis_id': STRING, 'kind': {'const': 'projection_record'},
                   'record_sha256': SHA, 'statement_id': STRING,
                   'library_ref': {'type': 'object', 'additionalProperties': False,
                                   'required': ['library_id', 'entry_id', 'revision', 'sha256'],
                                   'properties': {'library_id': {'const': 'lunados.lib'},
                                                  'entry_id': {'const': 'project.aggregate-relations'},
                                                  'revision': {'const': 'v1'}, 'sha256': SHA}}},
}
s['properties']['origin_bases'] = {'type': 'array', 'maxItems': 5000,
                                   'items': {'oneOf': [{'$ref': '#/$defs/origin_basis_statements'},
                                                       {'$ref': '#/$defs/origin_basis_projection'}]}}
(HERE / 'context-v10.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n', 'utf-8')

# VP-10 0.11.0 has a frozen prose contract, not a JSON Schema file. This
# local /1 baseline transcribes SS-1…SS-3 without modifying VP-10.
base = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'urn:aiaeao:cube:p1:statement-set:1',
    'title': 'Statement set /1 shape (VP-10 0.11.0 SS-1…SS-3)',
    'type': 'object', 'additionalProperties': False,
    'required': ['format', 'set_id', 'context_id', 'referents', 'statements', 'witness_ref'],
    'properties': {'format': {'const': 'aiaeao.cube.statement-set/1'},
                   'set_id': STRING, 'context_id': STRING,
                   'referents': {'type': 'array', 'minItems': 1, 'uniqueItems': True, 'items': STRING},
                   'statements': {'type': 'array', 'items': {'$ref': '#/$defs/statement'}},
                   'witness_ref': STRING},
    '$defs': {'statement': {'type': 'object', 'additionalProperties': False,
                            'required': ['statement_id', 'subject', 'predicate_id', 'object'],
                            'properties': {'statement_id': STRING, 'subject': STRING,
                                           'predicate_id': STRING, 'object': STRING,
                                           'label': {'type': 'string'}}}},
}
(HERE / 'statement-set-v1.baseline.schema.json').write_text(json.dumps(base, ensure_ascii=False, indent=2) + '\n', 'utf-8')
v2 = copy.deepcopy(base)
v2['$id'] = 'urn:aiaeao:cube:p1:statement-set:2'
v2['title'] = 'Statement set /2 shape (P1.14 origin fields; resolution in VP-07.6)'
v2['properties']['format'] = {'const': 'aiaeao.cube.statement-set/2'}
v2['$defs']['statement']['properties']['origin'] = {'enum': ['declared', 'derived', 'unknown']}
v2['$defs']['statement']['properties']['basis'] = STRING
(HERE / 'statement-set-v2.schema.json').write_text(json.dumps(v2, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('wrote context-v10, statement-set-v1 baseline and statement-set-v2 schemas')
