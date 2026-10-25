#!/usr/bin/env python3
"""Materialise C-01..C-20 from P1_9_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are NOT computed here: they are copied from the independent
oracle (oracles/independent_c01_c20.json), which was transcribed before code.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_c01_c20.json').read_text('utf-8'))

A = 'α'
METHOD = 'compare.fixture-run/v1'
def ref(r, cid, home, scope='cmp', **kw):
    return {'ref': r, 'concept_id': cid, 'home': home, 'layers': [A],
            'provenance_status': 'declared_unverified', 'scope_ref': scope, **kw}
def digest(s): return 'sha256:' + hashlib.sha256(s.encode()).hexdigest()

TEXT = f'rel("supports",Y:{A}:Evidence["ev-trt"],Y:{A}:Annotation["claim"])'

def scenario(sid, out, strategy, mode='simulation'):
    return {'scenario_id': sid, 'revision': 'cmp:v1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
            'mode': mode, 'world_refs': ['units', out], 'method_ids': [METHOD],
            'parameters': {'seed_set': 's-20', 'split': 'holdout', 'strategy': strategy}}

def base():
    return {
        'format': 'aiaeao.cube.binding-context/4', 'reference_version': 'v9.4',
        'context_id': 'p19-cmp', 'source_kind': 'illustrative_fixture', 'scope_ref': 'cmp',
        'referents': [ref('units', 'Y:resource-object:artifact', 'Y'),
                      ref('ev-ctl', 'Y:resource-object:evidence', 'Y'),
                      ref('ev-trt', 'Y:resource-object:evidence', 'Y'),
                      ref('claim', 'Y:identified-object:annotation', 'Y')],
        'predicate_contracts': [{'predicate_id': 'supports', 'revision': 'p19:v1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
                                 'subject_concept_ids': ['Y:resource-object:evidence'],
                                 'object_concept_ids': ['Y:identified-object:annotation'], 'direction': 'subject_to_object'}],
        'method_contracts': [{'method_id': METHOD, 'revision': 'v1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
                              'argument_min': 1, 'argument_max': 1, 'argument_concept_ids': ['Y:resource-object:artifact'],
                              'effect_class': 'pure_declarative',
                              'return_concept_ids': ['Y:resource-object:evidence'], 'return_cardinality': 'one'}],
        'scenarios': [scenario('sc-ctl', 'ev-ctl', 'fixed'), scenario('sc-trt', 'ev-trt', 'dynamic')],
        'comparison_protocols': [{'protocol_id': 'cp-1', 'revision': 'v1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
                                  'criteria': [{'metric_id': 'cost', 'direction': 'lower_better', 'unit': 'work/event'},
                                               {'metric_id': 'time', 'direction': 'lower_better', 'unit': 'ms'}],
                                  'non_comparability': 'report_incomparable', 'aggregation': 'none'}],
        'comparisons': [{'comparison_id': 'cmp-1', 'protocol_ref': 'cp-1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
                         'arms': [{'arm_id': 'ctl', 'scenario_ref': 'sc-ctl', 'role': 'control'},
                                  {'arm_id': 'trt', 'scenario_ref': 'sc-trt', 'role': 'treatment'}],
                         'pairing': {'unit': 'world', 'units_ref': 'units',
                                     'shared_parameters': ['seed_set', 'split'], 'varied_parameters': ['strategy']},
                         'outcomes': [outcome('o-1', 'a_preferred', -1.5)]}],
    }

def outcome(oid, val, value, **kw):
    o = {'outcome_id': oid, 'a': 'trt', 'b': 'ctl', 'metric_id': 'cost', 'outcome': val,
         'statistic': {'kind': 'delta_a_minus_b', 'declared_value': value},
         'annotation_ref': 'claim', 'witness_ref': 'witness:cmp/summary.json'}
    o.update(kw); return o

def cmp(c): return c['comparisons'][0]

def replay(c, input_same=True, output_same=True, status='declared'):
    for s in c['scenarios']: s['mode'] = 'replay'
    c['evaluators'] = [{'evaluator_id': 'eval:fixture', 'revision': 'v1', 'scope': 'cmp', 'origin': 'illustrative_fixture',
                        'kind': 'local_script', 'method_ids': [METHOD], 'output_concept_ids': ['Y:resource-object:evidence']}]
    c['evaluation_records'] = [
        {'record_id': 'orig', 'scenario_ref': 'sc-trt', 'evaluator_ref': 'eval:fixture', 'method_id': METHOD,
         'input_digest': digest('inputs'), 'output_refs': ['ev-trt'], 'witness_ref': 'witness:cmp/orig.json',
         'status': 'declared', 'output_digest': digest('outputs')},
        {'record_id': 'rep', 'scenario_ref': 'sc-trt', 'evaluator_ref': 'eval:fixture', 'method_id': METHOD,
         'input_digest': digest('inputs' if input_same else 'other inputs'), 'output_refs': ['ev-trt'],
         'witness_ref': 'witness:cmp/rep.json', 'status': status,
         'output_digest': digest('outputs' if output_same else 'other outputs'), 'replay_of': 'orig'}]
    return c

def build():
    v = {}
    v['C-01'] = base()
    c = base(); cmp(c)['arms'] = cmp(c)['arms'][:1]; v['C-02'] = c
    c = base(); cmp(c)['arms'][0]['role'] = 'treatment'; v['C-03'] = c
    c = base(); c['scenarios'][1]['world_refs'] = ['ev-trt']; v['C-04'] = c
    c = base(); c['scenarios'][1]['parameters']['seed_set'] = 's-21'; v['C-05'] = c
    c = base(); c['scenarios'][0]['parameters']['horizon'] = 1; c['scenarios'][1]['parameters']['horizon'] = 8; v['C-06'] = c
    c = copy.deepcopy(v['C-06']); cmp(c)['pairing']['varied_parameters'].append('horizon'); v['C-07'] = c
    c = base(); cmp(c)['outcomes'][0]['outcome'] = 'winner'; v['C-08'] = c
    c = base(); cmp(c)['outcomes'] = [outcome('o-1', 'equivalent_under_criteria', 0.0)]; v['C-09'] = c
    c = base(); cmp(c)['outcomes'][0]['statistic']['declared_value'] = 2.0; v['C-10'] = c
    c = base(); o = outcome('o-1', 'a_preferred', -1.5); del o['metric_id']; del o['statistic']
    o['metric_ids'] = ['cost', 'time']; cmp(c)['outcomes'] = [o]; v['C-11'] = c
    c = base(); cmp(c)['design'] = {'factors': {'depth': [4, 20]}}
    cmp(c)['outcomes'] = [outcome('o-4', 'a_preferred', -1.0, scope={'depth': 4}),
                          outcome('o-20', 'b_preferred', 3.0, scope={'depth': 20})]
    v['C-12'] = c
    c = copy.deepcopy(v['C-12']); cmp(c)['outcomes'][1]['scope'] = {'depth': 4}; v['C-13'] = c
    c = base(); cmp(c)['splits'] = ['calibration', 'holdout']; v['C-14'] = c
    c = base(); c['referents'].append(ref('concl', 'X:endpoint:conclusion', 'X'))
    cmp(c)['outcomes'][0]['annotation_ref'] = 'concl'; v['C-15'] = c
    v['C-16'] = replay(base())
    v['C-17'] = replay(base(), input_same=False)
    v['C-18'] = replay(base(), output_same=False)
    v['C-19'] = replay(base(), output_same=False, status='unresolved')
    c = base(); c['format'] = 'aiaeao.cube.binding-context/3'; v['C-20'] = c
    return v

def main():
    vecs = build(); exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'input_text': TEXT, 'input_format': 'acg_text', 'context': vecs[k],
              'expected_overall': exp[k]['expected_overall'], 'required_codes': exp[k]['required_codes']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.p1.9-vectors/1', 'reference_version': 'v9.4',
           'source': 'P1_9_ACCEPTANCE_SPEC.md §5 + oracles/independent_c01_c20.json', 'cases': cases}
    (HERE/'fixtures/c01_c20_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')

if __name__ == '__main__': main()
