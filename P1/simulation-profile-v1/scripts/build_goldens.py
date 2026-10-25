#!/usr/bin/env python3
"""Build / verify the P1.8-15 golden reference cases from EXP-010 and EXP-024.

  build_goldens.py --space <lunados.space repo>            # (re)build, pinning source hashes
  build_goldens.py --space <lunados.space repo> --verify   # re-hash sources, compare pins

The Cube never runs these experiments. A golden case only declares method,
scenario, evaluator and evaluation record, pinned to archived source files.
"""
import argparse, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
A = 'α'

SOURCES = {
 'exp010': {
  'preregistration': 'web/docs/experiment/experiment013/reference/PREREGISTRATION_010.json',
  'simulator':       'web/docs/experiment/experiment013/reference/sim010.py',
  'metrics':         'web/docs/experiment/AIAEAO_Seven_Ways_to_Verify_Experiment_010/metrics.json',
  'readme':          'web/docs/experiment/AIAEAO_Seven_Ways_to_Verify_Experiment_010/README.md'},
 'exp024': {
  'scenario':     'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/scenarios/dominates.json',
  'evaluator':    'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/evaluators/decision_pareto.py',
  'oracle':       'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/oracle/decision_oracle.py',
  'expected':     'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/results/dominates.expected.json',
  'alternatives': 'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/data/dominates.alternatives.json',
  'criteria':     'web/docs/cube/AIAEAO_EXP024_Charge3_Five_Envelopes_v0.1/data/criteria.json'},
}
ORIGIN = 'external_declaration_unverified'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ref(r, cid, home, scope, **kw):
    return {'ref': r, 'concept_id': cid, 'home': home, 'layers': [A],
            'provenance_status': 'declared_unverified', 'scope_ref': scope, **kw}


def pin(name, key, h):
    return f'lunados.space:{SOURCES[name][key]}#sha256={h}'


def sources(name, h):
    return {k: {'path': 'lunados.space:' + v, 'sha256': h[k]} for k, v in SOURCES[name].items()}


def exp010(h):
    S = 'exp010'; M = 'verify.composite-certificate/v1'
    world = ['exp010:eval-worlds', 'exp010:metrics', 'exp010:claim-ac-saving', 'exp010:assumption-known-generator']
    ctx = {
        'format': 'aiaeao.cube.binding-context/3', 'reference_version': 'v9.4',
        'context_id': 'golden-exp010', 'source_kind': ORIGIN, 'scope_ref': S,
        'referents': [ref('exp010:eval-worlds', 'Y:resource-object:artifact', 'Y', S),
                      ref('exp010:metrics', 'Y:resource-object:evidence', 'Y', S),
                      ref('exp010:claim-ac-saving', 'Y:identified-object:annotation', 'Y', S),
                      ref('exp010:assumption-known-generator', 'Y:identified-object:annotation', 'Y', S)],
        'predicate_contracts': [{
            'predicate_id': 'supports', 'revision': 'golden:v1', 'scope': S, 'origin': ORIGIN,
            'subject_concept_ids': ['Y:resource-object:evidence'],
            'object_concept_ids': ['Y:identified-object:annotation'], 'direction': 'subject_to_object',
            'additional_constraints': ['Support is declared by the archived run; the Cube does not verify it.']}],
        'method_contracts': [{
            'method_id': M, 'revision': 'exp010:010AC_batch', 'scope': S, 'origin': ORIGIN,
            'argument_min': 1, 'argument_max': 1, 'argument_concept_ids': ['Y:resource-object:artifact'],
            'effect_class': 'pure_declarative',
            'return_concept_ids': ['Y:resource-object:evidence'], 'return_cardinality': 'one'}],
        'evaluation_frame': {'scenario_ref': 'exp010-eval-central'},
        'scenarios': [{
            'scenario_id': 'exp010-eval-central', 'revision': 'prereg-0.1', 'scope': S, 'origin': ORIGIN,
            'mode': 'simulation', 'world_refs': world,
            'parameters': {'cost_profile': 'central', 'evaluation_seeds': '8-11', 'worlds': 64,
                           'events_per_world': 25, 'control': '009-D Fixed Certified', 'policy': '010AC_batch'},
            'assumption_refs': ['exp010:assumption-known-generator'], 'method_ids': [M]}],
        'evaluators': [{
            'evaluator_id': 'eval:exp010-sim010', 'revision': 'sim010.py@sha256:' + h['simulator'],
            'scope': S, 'origin': ORIGIN, 'kind': 'local_script', 'method_ids': [M],
            'output_concept_ids': ['Y:resource-object:evidence']}],
        'evaluation_records': [{
            'record_id': 'exp010-central-eval', 'scenario_ref': 'exp010-eval-central',
            'evaluator_ref': 'eval:exp010-sim010', 'method_id': M,
            'input_digest': 'sha256:' + h['preregistration'], 'output_refs': ['exp010:metrics'],
            'witness_ref': pin('exp010', 'metrics', h['metrics']), 'status': 'declared'}],
        'profile_limitations': [
            'Synthetic simulation; generator known; not a blinded or real-world holdout (PREREGISTRATION_010 validation_warning).',
            'Cube validates the declaration only; numbers are archived, never recomputed or verified.'],
    }
    return {
        'id': 'GOLDEN-EXP010', 'title': 'EXP-010 composite certificate (010-AC) as declared simulation',
        'input_text': f'rel("supports",{M}(Y:{A}:Artifact["exp010:eval-worlds"]),Y:{A}:Annotation["exp010:claim-ac-saving"])',
        'input_format': 'acg_text', 'context': ctx, 'expected_overall': 'PASS', 'required_codes': [],
        'reference': {
            'experiment': 'EXP-010 Qualification-Aware Incremental Verification',
            'declared_finding': ('Central profile, seeds 8-11, 64 worlds x 25 events: 010-AC composite 31.864306 vs '
                                 '009-D Fixed Certified 32.722279 modeled work/event (saving 2.622 %), coverage 100 % '
                                 'of fixed-reachable synthetic findings.'),
            'claim_ref': 'exp010:claim-ac-saving', 'assumption_ref': 'exp010:assumption-known-generator',
            'library_ref': 'omitted: no Functions Library entry exists for this method (P1.8 D-3 optional)',
            'not_claimed': ['universal correctness', 'measured runtime', 'real-world holdout'],
            'sources': sources('exp010', h)}}


def exp024(h):
    S = 'exp024'; E = 'exp024-event'; M = 'decision.compare/v1'
    world = ['exp024:alternatives', 'exp024:criteria', 'exp024:expected-result', 'exp024-event',
             'exp024:evaluator-actor', 'exp024:run-dominates', 'exp024:result-dominates']
    ctx = {
        'format': 'aiaeao.cube.binding-context/3', 'reference_version': 'v9.4',
        'context_id': 'golden-exp024-dominates', 'source_kind': ORIGIN, 'scope_ref': S,
        'referents': [
            ref('exp024:alternatives', 'Y:resource-object:artifact', 'Y', S),
            ref('exp024:criteria', 'Y:resource-object:artifact', 'Y', S),
            ref('exp024:expected-result', 'Y:resource-object:evidence', 'Y', E),
            ref('exp024-event', 'X:scope:event', 'X', E),
            ref('exp024:evaluator-actor', 'Y:identity-anchor:actor', 'Y', E),
            ref('exp024:run-dominates', 'X:endpoint:action', 'X', E,
                instantiation_profile_ref='p16-X:endpoint:action',
                slots={'pair_scope_ref': E, 'performed_by_ref': 'exp024:evaluator-actor'}),
            ref('exp024:result-dominates', 'X:endpoint:result', 'X', E,
                instantiation_profile_ref='p16-X:endpoint:result',
                slots={'pair_scope_ref': E, 'action_ref': 'exp024:run-dominates',
                       'artifact_refs': ['exp024:expected-result']})],
        'predicate_contracts': [{
            'predicate_id': 'assesses', 'revision': 'golden:v1', 'scope': S, 'origin': ORIGIN,
            'subject_concept_ids': ['Y:identified-object:annotation'],
            'object_concept_ids': ['Y:resource-object:artifact'], 'direction': 'subject_to_object',
            'additional_constraints': ['A dominance assessment is neither preference, selection nor authority.']}],
        'method_contracts': [{
            'method_id': M, 'revision': 'exp024:decision.compare/v0.1', 'scope': S, 'origin': ORIGIN,
            'argument_min': 2, 'argument_max': 2,
            'argument_concept_ids': ['Y:resource-object:artifact', 'Y:resource-object:artifact'],
            'effect_class': 'pure_declarative',
            'return_concept_ids': ['Y:identified-object:annotation'], 'return_cardinality': 'one'}],
        'instantiation_profiles': [
            {'profile_ref': 'p16-X:endpoint:result', 'concept_id': 'X:endpoint:result', 'revision': 'golden/v1',
             'scope': E, 'origin': ORIGIN,
             'slots': [{'name': 'pair_scope_ref', 'kind': 'ref', 'required': True, 'cardinality': 'one',
                        'concept_ids': ['X:scope:event']},
                       {'name': 'action_ref', 'kind': 'ref', 'required': True, 'cardinality': 'one',
                        'concept_ids': ['X:endpoint:action']},
                       {'name': 'artifact_refs', 'kind': 'ref', 'required': False, 'cardinality': 'many',
                        'concept_ids': ['Y:resource-object:artifact', 'Y:resource-object:evidence']}]},
            {'profile_ref': 'p16-X:endpoint:action', 'concept_id': 'X:endpoint:action', 'revision': 'golden/v1',
             'scope': E, 'origin': ORIGIN,
             'slots': [{'name': 'pair_scope_ref', 'kind': 'ref', 'required': True, 'cardinality': 'one',
                        'concept_ids': ['X:scope:event']},
                       {'name': 'performed_by_ref', 'kind': 'ref', 'required': True, 'cardinality': 'one',
                        'concept_ids': ['Y:identity-anchor:actor']}]}],
        'evaluation_frame': {'scenario_ref': 'exp024-dominates-replay'},
        'scenarios': [{
            'scenario_id': 'exp024-dominates-replay', 'revision': 'charge3-v0.1', 'scope': S, 'origin': ORIGIN,
            'mode': 'replay', 'world_refs': world,
            'parameters': {'methods': 'pareto-dominance-exact', 'tradeoff_policy': 'retain-noncomparability',
                           'a_cost': 100, 'a_duration': 5, 'b_cost': 120, 'b_duration': 7},
            'method_ids': [M]}],
        'evaluators': [{
            'evaluator_id': 'eval:decision.pareto/v0.1', 'revision': 'decision_pareto.py@sha256:' + h['evaluator'],
            'scope': S, 'origin': ORIGIN, 'kind': 'local_script', 'method_ids': [M],
            'output_concept_ids': ['X:endpoint:result', 'Y:resource-object:evidence']}],
        'evaluation_records': [{
            'record_id': 'exp024-charge3-dominates', 'scenario_ref': 'exp024-dominates-replay',
            'evaluator_ref': 'eval:decision.pareto/v0.1', 'method_id': M,
            'input_digest': 'sha256:' + h['scenario'], 'output_refs': ['exp024:result-dominates'],
            'witness_ref': pin('exp024', 'expected', h['expected']), 'status': 'declared'}],
        'profile_limitations': [
            'Authored domain fixture, not an empirical decision; evaluator and oracle share project mathematics.',
            'Replay of an archived result; the Cube does not dispatch the evaluator, select an alternative or grant authority.'],
    }
    return {
        'id': 'GOLDEN-EXP024', 'title': 'EXP-024 Charge 3 decision "dominates" as declared replay with P1.6 Result',
        'input_text': (f'rel("assesses",{M}(Y:{A}:Artifact["exp024:alternatives"],Y:{A}:Artifact["exp024:criteria"]),'
                       f'Y:{A}:Artifact["exp024:alternatives"])'),
        'input_format': 'acg_text', 'context': ctx, 'expected_overall': 'PASS', 'required_codes': [],
        'reference': {
            'experiment': 'EXP-024 Charge 3 Five Envelopes - Decision',
            'declared_finding': ('A (cost 100, duration 5) Pareto-dominates B (120, 7): relation a_dominates_b, '
                                 'selected_alternative null, runtime_authority not-evaluated.'),
            'method_id_mapping': {'golden': M, 'original': 'decision.compare/v0.1',
                                  'reason': 'P1 method IDs require /v[1-9]...'},
            'not_claimed': ['human preference', 'selection', 'authority', 'external ground truth'],
            'sources': sources('exp024', h)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--space', required=True, help='path to the lunados.space repository')
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args(); space = Path(a.space)
    hashes = {n: {k: sha(space / p) for k, p in d.items()} for n, d in SOURCES.items()}
    built = {'exp010': exp010(hashes['exp010']), 'exp024': exp024(hashes['exp024'])}
    bad = 0
    for n, case in built.items():
        f = HERE / f'fixtures/golden_{n}.json'
        text = json.dumps(case, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
        if a.verify:
            ok = f.exists() and f.read_text('utf-8') == text
            print(('PASS' if ok else 'FAIL'), f.name, 'source pins match' if ok else 'differs from sources')
            bad += not ok
        else:
            f.write_text(text, 'utf-8'); print('wrote', f.name)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
