#!/usr/bin/env python3
"""Generate context-v4.schema.json as a strict superset of context-v3.schema.json."""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
v3 = json.loads((HERE.parent/'simulation-profile-v1/context-v3.schema.json').read_text('utf-8'))
s = copy.deepcopy(v3)
s['$id'] = 'urn:aiaeao:cube:p1:binding-context:4'
s['title'] = 'AIAEAO Cube binding context /4 (P1.9 declared comparison profile)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/4'}
S = {'type': 'string', 'minLength': 1}
ARR = lambda item, mn=0: {'type': 'array', 'minItems': mn, 'uniqueItems': True, 'items': item}
SCALAR = {'type': ['string', 'number', 'boolean', 'null']}
DIG = {'type': 'string', 'pattern': '^sha256:[0-9a-f]{64}$'}
d = s['$defs']
d['evaluation_record']['properties']['replay_of'] = S
d['evaluation_record']['properties']['output_digest'] = DIG
d['criterion'] = {'type': 'object', 'additionalProperties': False, 'required': ['metric_id', 'direction'],
                  'properties': {'metric_id': S, 'direction': {'enum': ['lower_better', 'higher_better', 'none']}, 'unit': S}}
d['comparison_protocol'] = {'type': 'object', 'additionalProperties': False,
    'required': ['protocol_id', 'revision', 'scope', 'origin', 'criteria', 'non_comparability', 'aggregation'],
    'properties': {'protocol_id': S, 'revision': S, 'scope': S,
                   'origin': {'enum': ['illustrative_fixture', 'external_declaration_unverified']},
                   'criteria': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/criterion'}},
                   'equivalence_margin': {'type': 'object', 'additionalProperties': {'type': 'number', 'minimum': 0}},
                   'non_comparability': {'enum': ['report_incomparable', 'report_undetermined']},
                   'aggregation': {'type': 'string', 'minLength': 1, 'description': '"none" or a declared pure_declarative method_id'},
                   'required_parity': ARR({'enum': ['result_equivalence', 'coverage', 'digest_equal', 'declared_other']}),
                   'library_ref': copy.deepcopy(d['method']['properties']['library_ref'])}}
d['arm'] = {'type': 'object', 'additionalProperties': False, 'required': ['arm_id', 'scenario_ref', 'role'],
            'properties': {'arm_id': S, 'scenario_ref': S, 'role': {'enum': ['control', 'treatment', 'reference']}}}
d['parity'] = {'type': 'object', 'additionalProperties': False, 'required': ['parity_id', 'kind'],
               'properties': {'parity_id': S, 'kind': {'enum': ['result_equivalence', 'coverage', 'digest_equal', 'declared_other']},
                              'witness_ref': S, 'arm_refs': ARR(S, 1)}}
d['statistic'] = {'type': 'object', 'additionalProperties': False, 'required': ['kind', 'declared_value'],
                  'properties': {'kind': {'enum': ['delta_a_minus_b', 'ratio_a_over_b', 'interval_a_minus_b', 'declared_other']},
                                 'declared_value': {'oneOf': [{'type': 'number'}, {'type': 'array', 'minItems': 2, 'maxItems': 2, 'items': {'type': 'number'}}]}}}
d['outcome'] = {'type': 'object', 'additionalProperties': False,
                'required': ['outcome_id', 'a', 'b', 'outcome', 'annotation_ref'],
                'oneOf': [{'required': ['metric_id']}, {'required': ['metric_ids']}],
                'properties': {'outcome_id': S, 'a': S, 'b': S, 'metric_id': S, 'metric_ids': ARR(S, 1),
                               'outcome': {'type': 'string', 'minLength': 1, 'description': 'Morphology v9.4 §5.16 vocabulary; other values FAIL semantically'},
                               'scope': {'type': 'object', 'minProperties': 1, 'additionalProperties': SCALAR},
                               'split': S, 'statistic': {'$ref': '#/$defs/statistic'}, 'annotation_ref': S, 'witness_ref': S}}
d['comparison'] = {'type': 'object', 'additionalProperties': False,
    'required': ['comparison_id', 'protocol_ref', 'scope', 'arms', 'pairing'],
    'properties': {'comparison_id': S, 'protocol_ref': S, 'scope': S,
                   'origin': {'enum': ['illustrative_fixture', 'external_declaration_unverified']},
                   'arms': {'type': 'array', 'items': {'$ref': '#/$defs/arm'}},
                   'pairing': {'type': 'object', 'additionalProperties': False,
                               'required': ['unit', 'units_ref', 'shared_parameters', 'varied_parameters'],
                               'properties': {'unit': {'enum': ['world', 'seed', 'cell', 'world_seed']}, 'units_ref': S,
                                              'shared_parameters': ARR(S), 'varied_parameters': ARR(S)}},
                   'parity': {'type': 'array', 'items': {'$ref': '#/$defs/parity'}},
                   'splits': ARR(S, 1),
                   'design': {'type': 'object', 'additionalProperties': False, 'required': ['factors'],
                              'properties': {'factors': {'type': 'object', 'minProperties': 1,
                                                         'additionalProperties': {'type': 'array', 'minItems': 1, 'items': SCALAR}}}},
                   'outcomes': {'type': 'array', 'items': {'$ref': '#/$defs/outcome'}}}}
s['properties']['comparison_protocols'] = {'type': 'array', 'maxItems': 64, 'items': {'$ref': '#/$defs/comparison_protocol'}}
s['properties']['comparisons'] = {'type': 'array', 'maxItems': 64, 'items': {'$ref': '#/$defs/comparison'}}
(HERE/'context-v4.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('wrote context-v4.schema.json')
