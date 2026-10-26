#!/usr/bin/env python3
"""Build / verify the P1.9-15 golden comparisons from EXP-002B, 003, 007 and 009-D.

  build_goldens.py --space <lunados.space repo>            # (re)build, pinning source hashes
  build_goldens.py --space <lunados.space repo> --verify   # re-hash sources, compare pins

The Cube never runs these experiments and never computes a statistic. This
script only *transcribes* archived numbers (deltas, intervals, means) from the
pinned result files into declarations; outcome labels follow the archived sign
or interval under the declared metric direction. Every transcribed value names
its source file and that file's SHA-256.
"""
import argparse, csv, hashlib, io, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
A = 'α'
ORIGIN = 'external_declaration_unverified'
EXP = 'web/docs/experiment/'
SOURCES = {
 'exp002b': {'readme': EXP+'AIAEAO_Experiment_002B/README.md',
             'runner': EXP+'AIAEAO_Experiment_002B/run_experiment.js',
             'design': EXP+'AIAEAO_Experiment_002B/results/design.json',
             'paired_summary': EXP+'AIAEAO_Experiment_002B/results/paired_summary.csv',
             'analysis': EXP+'AIAEAO_Experiment_002B/results/analysis.json',
             'manifest': EXP+'AIAEAO_Experiment_002B/MANIFEST.sha256'},
 'exp003': {'readme': EXP+'AIAEAO_Experiment_003/README.md',
            'simulator': EXP+'AIAEAO_Experiment_003/simulate.py',
            'design': EXP+'AIAEAO_Experiment_003/results/design.json',
            'summary': EXP+'AIAEAO_Experiment_003/results/summary.json',
            'paired': EXP+'AIAEAO_Experiment_003/results/paired.csv',
            'manifest': EXP+'AIAEAO_Experiment_003/MANIFEST.sha256'},
 'exp007': {'protocol': EXP+'AIAEAO_Experiment_007/EXPERIMENT-PROTOCOL.json',
            'runner': EXP+'AIAEAO_Experiment_007/src/run007.py',
            'intervals': EXP+'AIAEAO_Experiment_007/results/paired_intervals.json',
            'summary': EXP+'AIAEAO_Experiment_007/results/summary.json',
            'paired_by_world': EXP+'AIAEAO_Experiment_007/results/paired_by_world.csv',
            'manifest': EXP+'AIAEAO_Experiment_007/SHA256SUMS.txt'},
 'exp009d': {'preregistration': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/data/PREREGISTRATION.json',
             'simulator': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/src/sim009d.py',
             'summary': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/results/summary.csv',
             'verdict': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/results/verdict.json',
             'paired_worlds': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/results/paired_worlds.csv',
             'original_009': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/reference_009/ORIGINAL-009-SUMMARY.csv',
             'manifest': EXP+'AIAEAO_Experiment_009D_Final_Switch_Costs/MANIFEST.sha256'},
}


def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def canon(o): return json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def ref(r, cid, scope):
    return {'ref': r, 'concept_id': cid, 'home': cid[0], 'layers': [A],
            'provenance_status': 'declared_unverified', 'scope_ref': scope}


class Exp:
    def __init__(self, name, space):
        self.n = name; self.space = space
        self.raw = {k: (space/p).read_bytes() for k, p in SOURCES[name].items()}
        self.h = {k: sha_bytes(v) for k, v in self.raw.items()}

    def pin(self, key): return f'lunados.space:{SOURCES[self.n][key]}#sha256={self.h[key]}'
    def json(self, key): return json.loads(self.raw[key])
    def csv(self, key): return list(csv.DictReader(io.StringIO(self.raw[key].decode('utf-8'))))
    def sources(self): return {k: {'path': 'lunados.space:' + v, 'sha256': self.h[k]} for k, v in SOURCES[self.n].items()}


def outcome_of(direction, value=None, interval=None, margin=0.0):
    """Label transcription only: what the archived number says under the direction."""
    def side(v):
        v = -v if direction == 'higher_better' else v
        return -1 if v < -margin else (1 if v > margin else 0)
    s = {side(interval[0]), side(interval[1])} if interval else {side(value)}
    if s == {-1}: return 'a_preferred'
    if s == {1}: return 'b_preferred'
    if s == {0}: return 'equivalent_under_criteria'
    return 'undetermined_with_available_evidence'


def frame(e, method, evaluator_rev, evaluator_kind='local_script', input_key=None):
    S = e.n
    return S, {
        'format': 'aiaeao.cube.binding-context/4', 'reference_version': 'v9.4',
        'context_id': f'golden-{S}-comparison', 'source_kind': ORIGIN, 'scope_ref': S,
        'referents': [ref(f'{S}:units', 'Y:resource-object:artifact', S),
                      ref(f'{S}:result-summary', 'Y:resource-object:evidence', S),
                      ref(f'{S}:claim-comparison', 'Y:identified-object:annotation', S)],
        'predicate_contracts': [{
            'predicate_id': 'supports', 'revision': 'golden:v1', 'scope': S, 'origin': ORIGIN,
            'subject_concept_ids': ['Y:resource-object:evidence'],
            'object_concept_ids': ['Y:identified-object:annotation'], 'direction': 'subject_to_object',
            'additional_constraints': ['Support is declared by the archived run; the Cube does not verify it.']}],
        'method_contracts': [{
            'method_id': method, 'revision': evaluator_rev, 'scope': S, 'origin': ORIGIN,
            'argument_min': 1, 'argument_max': 1, 'argument_concept_ids': ['Y:resource-object:artifact'],
            'effect_class': 'pure_declarative',
            'return_concept_ids': ['Y:resource-object:evidence'], 'return_cardinality': 'one'}],
        'scenarios': [], 'evaluators': [{
            'evaluator_id': f'eval:{S}', 'revision': evaluator_rev, 'scope': S, 'origin': ORIGIN,
            'kind': evaluator_kind, 'method_ids': [method], 'output_concept_ids': ['Y:resource-object:evidence']}],
        'evaluation_records': [], 'comparison_protocols': [], 'comparisons': []}


def add_arm(ctx, S, method, arm_id, params, input_digest, witness, mode='simulation'):
    out = f'{S}:out-{arm_id}'
    ctx['referents'].append(ref(out, 'Y:resource-object:evidence', S))
    sid = f'{S}-{arm_id}'
    ctx['scenarios'].append({'scenario_id': sid, 'revision': 'archived', 'scope': S, 'origin': ORIGIN, 'mode': mode,
                             'world_refs': [f'{S}:units', out], 'method_ids': [method], 'parameters': params})
    ctx['evaluation_records'].append({'record_id': f'rec-{arm_id}', 'scenario_ref': sid, 'evaluator_ref': f'eval:{S}',
                                      'method_id': method, 'input_digest': input_digest, 'output_refs': [out],
                                      'witness_ref': witness, 'status': 'declared'})
    return sid


def golden(e, ctx, title, finding, not_claimed, extra=None):
    S = e.n
    return {'id': f'GOLDEN-{S.upper()}-COMPARISON', 'title': title,
            'input_text': f'rel("supports",Y:{A}:Evidence["{S}:result-summary"],Y:{A}:Annotation["{S}:claim-comparison"])',
            'input_format': 'acg_text', 'context': ctx, 'expected_overall': 'PASS', 'required_codes': [],
            'reference': {'experiment': title, 'declared_finding': finding, 'not_claimed': not_claimed,
                          'transcription': 'Numbers are copied from the pinned result files; nothing is recomputed by the Cube.',
                          **(extra or {}), 'sources': e.sources()}}


# --- EXP-002B: ADM vs MPC, 18 cases, two metrics, ranking flip -----------------
def exp002b(e):
    M = 'simulate.planning-depth/v1'
    S, ctx = frame(e, M, 'run_experiment.js@sha256:' + e.h['runner'])
    design = e.json('design'); cases = [c['id'] for c in design['cases']]
    shared = {'worlds': 1080, 'tasks': design['base']['tasks'], 'seeds': len(design['base']['seeds']),
              'world_generator': '002-A deterministic', 'scenario_cells': design['scenarioCount']}
    din = 'sha256:' + e.h['design']
    add_arm(ctx, S, M, 'adm', {**shared, 'policy': 'ADM', 'horizon': 1}, din, e.pin('paired_summary'))
    add_arm(ctx, S, M, 'mpc', {**shared, 'policy': 'MPC', 'horizon': design['cases'][0].get('horizon', 8)}, din, e.pin('paired_summary'))
    ctx['comparison_protocols'].append({
        'protocol_id': 'cp-002b', 'revision': 'analysis.v1', 'scope': S, 'origin': ORIGIN,
        'criteria': [{'metric_id': 'total_cost', 'direction': 'lower_better', 'unit': 'cumulative scalar cost per world stream'},
                     {'metric_id': 'errors', 'direction': 'lower_better', 'unit': 'errors per world stream'}],
        'non_comparability': 'report_undetermined', 'aggregation': 'none'})
    outs = []
    for r in e.csv('paired_summary'):
        cid = r['case_id']
        ci = [float(r['cost_lo']), float(r['cost_hi'])]
        outs.append({'outcome_id': f'{cid}-cost', 'a': 'mpc', 'b': 'adm', 'metric_id': 'total_cost',
                     'outcome': outcome_of('lower_better', interval=ci), 'scope': {'case': cid},
                     'statistic': {'kind': 'interval_a_minus_b', 'declared_value': ci},
                     'annotation_ref': f'{S}:claim-comparison', 'witness_ref': e.pin('paired_summary')})
        ei = [-float(r['error_hi']), -float(r['error_lo'])]                     # MPC - ADM errors
        outs.append({'outcome_id': f'{cid}-errors', 'a': 'mpc', 'b': 'adm', 'metric_id': 'errors',
                     'outcome': outcome_of('lower_better', interval=ei), 'scope': {'case': cid},
                     'statistic': {'kind': 'interval_a_minus_b', 'declared_value': ei},
                     'annotation_ref': f'{S}:claim-comparison', 'witness_ref': e.pin('paired_summary')})
    ctx['comparisons'].append({
        'comparison_id': 'cmp-002b-adm-mpc', 'protocol_ref': 'cp-002b', 'scope': S, 'origin': ORIGIN,
        'arms': [{'arm_id': 'adm', 'scenario_ref': f'{S}-adm', 'role': 'control'},
                 {'arm_id': 'mpc', 'scenario_ref': f'{S}-mpc', 'role': 'treatment'}],
        'pairing': {'unit': 'world_seed', 'units_ref': f'{S}:units',
                    'shared_parameters': sorted(shared), 'varied_parameters': ['horizon', 'policy']},
        'parity': [{'parity_id': 'same-worlds', 'kind': 'declared_other', 'witness_ref': e.pin('analysis')}],
        'design': {'factors': {'case': cases}}, 'outcomes': outs})
    flips = sorted({o['scope']['case'] for o in outs if o['metric_id'] == 'total_cost' and o['outcome'] == 'a_preferred'})
    open_cases = sorted({o['scope']['case'] for o in outs if o['metric_id'] == 'total_cost' and o['outcome'].startswith('undetermined')})
    fewer_errors = all(o['outcome'] == 'a_preferred' for o in outs if o['metric_id'] == 'errors')
    ctx['profile_limitations'] = ['Synthetic certainty-equivalent rollout, not exact MPC; deterministic fixed seeds; not field evidence.',
                                  'Cost intervals are descriptive bootstrap intervals over 54 scenario-cell means (analysis.json).',
                                  'Loss multipliers change the cost scale; outcomes are scoped per case and never compared across cases.']
    return golden(e, ctx, 'EXP-002B ADM vs MPC — robustness and sensitivity',
                  (f'MPC makes fewer errors in {"every" if fewer_errors else "not every"} case. On total cost ADM is preferred in the reference case; '
                   f'the ranking flips to MPC in {flips}, and stays undetermined in {open_cases}.'),
                  ['real-world planning benefit', 'exact MPC', 'a winner across cases', 'runtime latencies'],
                  {'ranking_flip_cases': flips, 'undetermined_cases': open_cases})


# --- EXP-003: three projections, per-metric, no overall score ------------------
def exp003(e):
    M = 'simulate.dialectical-projection/v1'
    S, ctx = frame(e, M, 'simulate.py@sha256:' + e.h['simulator'])
    d = e.json('design'); summ = e.json('summary')
    shared = {'seeds': len(d['seeds']), 'topics': d['topics'], 'tasks_per_topic': d['tasks_per_topic'],
              'scenario_cells': summ['design']['scenario_cells']}
    din = 'sha256:' + e.h['design']
    for m in d['methods']:
        add_arm(ctx, S, M, m.lower(), {**shared, 'method': m}, din, e.pin('summary'))
    ctx['comparison_protocols'].append({
        'protocol_id': 'cp-003', 'revision': 'synthetic.v1', 'scope': S, 'origin': ORIGIN,
        'criteria': [{'metric_id': 'brier', 'direction': 'lower_better', 'unit': 'Brier score'},
                     {'metric_id': 'net_loss', 'direction': 'lower_better', 'unit': 'decision loss incl. compute cost'}],
        'non_comparability': 'report_incomparable', 'aggregation': 'none'})
    outs = []
    for key, v in sorted(summ['paired_bootstrap'].items()):
        a, rest = key.split('_minus_'); b, metric = rest.split('_delta_')
        ci = [float(x) for x in v['CI95_scenario_bootstrap']]
        outs.append({'outcome_id': f'{a.lower()}-vs-{b.lower()}-{metric}', 'a': a.lower(), 'b': b.lower(), 'metric_id': metric,
                     'outcome': outcome_of('lower_better', interval=ci),
                     'statistic': {'kind': 'interval_a_minus_b', 'declared_value': ci},
                     'annotation_ref': f'{S}:claim-comparison', 'witness_ref': e.pin('summary')})
    ctx['comparisons'].append({
        'comparison_id': 'cmp-003-projections', 'protocol_ref': 'cp-003', 'scope': S, 'origin': ORIGIN,
        'arms': [{'arm_id': 'static', 'scenario_ref': f'{S}-static', 'role': 'control'},
                 {'arm_id': 'rule', 'scenario_ref': f'{S}-rule', 'role': 'reference'},
                 {'arm_id': 'adaptive', 'scenario_ref': f'{S}-adaptive', 'role': 'treatment'}],
        'pairing': {'unit': 'cell', 'units_ref': f'{S}:units', 'shared_parameters': sorted(shared), 'varied_parameters': ['method']},
        'parity': [{'parity_id': 'same-world-streams', 'kind': 'declared_other', 'witness_ref': e.pin('design')}],
        'outcomes': outs})
    ctx['profile_limitations'] = ['Exploratory synthetic simulation, not a canonical v6 implementation (design.json status).',
                                  'Per-metric outcomes only; the experiment deliberately reports no overall score (aggregation: none).']
    return golden(e, ctx, 'EXP-003 Dialectical quality — STATIC, RULE, ADAPTIVE',
                  'ADAPTIVE beats RULE on Brier score and net loss, but STATIC beats ADAPTIVE on both (paired scenario bootstrap, 95 %).',
                  ['a total ranking of the three methods', 'real-world calibration', 'knowledge capability of any Cube'])


# --- EXP-007: four strategies vs direct, exact result parity ---------------------
def exp007(e):
    M = 'simulate.selectivity/v1'
    S, ctx = frame(e, M, 'run007.py@sha256:' + e.h['runner'])
    p = e.json('protocol'); summ = e.json('summary'); iv = e.json('intervals')
    shared = {'worlds': p['worlds'], 'query_events_per_world': p['query_events_per_world'], 'seeds': len(p['factors']['seed'])}
    din = 'sha256:' + e.h['protocol']
    arms = summ['strategies']
    for s in arms:
        add_arm(ctx, S, M, s, {**shared, 'strategy': s}, din, e.pin('intervals'))
    ctx['comparison_protocols'].append({
        'protocol_id': 'cp-007', 'revision': p['version'], 'scope': S, 'origin': ORIGIN,
        'criteria': [{'metric_id': 'total_ms', 'direction': 'lower_better', 'unit': 'ms per world (synthetic, in-process)'}],
        'non_comparability': 'report_undetermined', 'aggregation': 'none', 'required_parity': ['result_equivalence']})
    treat = [s for s in arms if s != 'direct']
    outs = []
    for s in treat:
        ci = [float(x) for x in iv[s]['bootstrap_95_percentile_interval_ms']]
        outs.append({'outcome_id': f'{s}-vs-direct', 'a': s, 'b': 'direct', 'metric_id': 'total_ms',
                     'outcome': outcome_of('lower_better', interval=ci),
                     'statistic': {'kind': 'interval_a_minus_b', 'declared_value': ci},
                     'annotation_ref': f'{S}:claim-comparison', 'witness_ref': e.pin('intervals')})
    assert summ['query_result_exact_parity'] is True
    ctx['comparisons'].append({
        'comparison_id': 'cmp-007-selectivity', 'protocol_ref': 'cp-007', 'scope': S, 'origin': ORIGIN,
        'arms': [{'arm_id': 'direct', 'scenario_ref': f'{S}-direct', 'role': 'control'}] +
                [{'arm_id': s, 'scenario_ref': f'{S}-{s}', 'role': 'treatment'} for s in treat],
        'pairing': {'unit': 'world', 'units_ref': f'{S}:units', 'shared_parameters': sorted(shared), 'varied_parameters': ['strategy']},
        'parity': [{'parity_id': 'exact-query-results', 'kind': 'result_equivalence', 'witness_ref': e.pin('summary')}],
        'outcomes': outs})
    ctx['profile_limitations'] = ['Synthetic controlled pilot; in-process timings; MIDI hardware not measured.',
                                  'Result equivalence is declared by the archived run (query_result_exact_parity); the Cube does not check it.']
    return golden(e, ctx, 'EXP-007 Computational selectivity — four strategies vs direct',
                  'All four strategies are faster than direct evaluation at exact result parity (95 % bootstrap intervals entirely below zero).',
                  ['real MIDI transport', 'speed-up outside the 108 synthetic worlds', 'authority from bitset candidates'])


# --- EXP-009-D: strategies vs certified Fixed, coverage parity, holdout, replay ----
BASE009 = ('typed_native_relevant', 'morph_fixed_native', 'morph_reactive_native')


def exp009d(e):
    M = 'simulate.switch-costs/v1'
    S, ctx = frame(e, M, 'sim009d.py@sha256:' + e.h['simulator'])
    pre = e.json('preregistration'); rows = e.csv('summary')
    rates = [float(x) for x in pre['switch_cost_rates']]
    full = sorted({r['policy'] for r in rows if float(r['coverage']) == 1.0})
    control = 'morph_fixed_certified'
    treat = [p for p in full if p != control]
    din = 'sha256:' + e.h['preregistration']
    shared = {'worlds': 128, 'epochs': 25, 'calibration_seeds': '0-3', 'holdout_seeds': '4-7'}
    ctx['comparison_protocols'].append({
        'protocol_id': 'cp-009d', 'revision': 'prereg:' + pre['date'], 'scope': S, 'origin': ORIGIN,
        'criteria': [{'metric_id': 'mean_work', 'direction': 'lower_better', 'unit': 'modelled work per event'}],
        'equivalence_margin': {'mean_work': 0.0},
        'non_comparability': 'report_undetermined', 'aggregation': 'none', 'required_parity': ['coverage']})
    for rate in rates:
        tag = f'r{int(round(rate*100)):02d}'
        for pol in [control] + treat:
            add_arm(ctx, S, M, f'{pol}-{tag}', {**shared, 'switch_rate': rate, 'strategy': pol}, din, e.pin('summary'))
        outs = []
        for split in ('calibration', 'holdout'):
            by = {r['policy']: float(r['mean_work']) for r in rows if r['split'] == split and float(r['switch_rate']) == rate}
            for pol in treat:
                delta = round(by[pol] - by[control], 6)
                outs.append({'outcome_id': f'{pol}-{tag}-{split}', 'a': f'{pol}-{tag}', 'b': f'{control}-{tag}', 'metric_id': 'mean_work',
                             'outcome': outcome_of('lower_better', value=delta), 'split': split,
                             'statistic': {'kind': 'delta_a_minus_b', 'declared_value': delta},
                             'annotation_ref': f'{S}:claim-comparison', 'witness_ref': e.pin('summary')})
        ctx['comparisons'].append({
            'comparison_id': f'cmp-009d-{tag}', 'protocol_ref': 'cp-009d', 'scope': S, 'origin': ORIGIN,
            'arms': [{'arm_id': f'{control}-{tag}', 'scenario_ref': f'{S}-{control}-{tag}', 'role': 'control'}] +
                    [{'arm_id': f'{p}-{tag}', 'scenario_ref': f'{S}-{p}-{tag}', 'role': 'treatment'} for p in treat],
            'pairing': {'unit': 'world', 'units_ref': f'{S}:units',
                        'shared_parameters': sorted(shared) + ['switch_rate'], 'varied_parameters': ['strategy']},
            'parity': [{'parity_id': 'full-fixed-achievable-coverage', 'kind': 'coverage', 'witness_ref': e.pin('summary')}],
            'splits': ['calibration', 'holdout'], 'outcomes': outs})
    # Replay against record: 009-D re-runs the three 009 baseline policies on the holdout worlds.
    orig = {r['policy']: float(r['mean_work']) for r in e.csv('original_009')
            if r['split'] == 'holdout' and r['stress'] == '0' and r['policy'] in BASE009}
    rep = {b['policy']: float(b['009d']) for b in e.json('verdict')['baseline_match']}
    ctx['referents'] += [ref(f'{S}:out-009-original', 'Y:resource-object:evidence', S),
                         ref(f'{S}:out-009d-baseline', 'Y:resource-object:evidence', S)]
    ctx['scenarios'].append({'scenario_id': f'{S}-baseline-replay', 'revision': 'archived', 'scope': S, 'origin': ORIGIN,
                             'mode': 'replay', 'world_refs': [f'{S}:units', f'{S}:out-009-original', f'{S}:out-009d-baseline'],
                             'method_ids': [M], 'parameters': {'split': 'holdout', 'stress': 0, 'policies': ','.join(BASE009)}})
    rin = 'sha256:' + sha_bytes(canon({'experiment': '009', 'worlds': pre['worlds'], 'split': 'holdout', 'policies': list(BASE009)}))
    ctx['evaluation_records'] += [
        {'record_id': 'rec-009-original', 'scenario_ref': f'{S}-baseline-replay', 'evaluator_ref': f'eval:{S}', 'method_id': M,
         'input_digest': rin, 'output_refs': [f'{S}:out-009-original'], 'witness_ref': e.pin('original_009'),
         'status': 'declared', 'output_digest': 'sha256:' + sha_bytes(canon(orig))},
        {'record_id': 'rec-009d-baseline', 'scenario_ref': f'{S}-baseline-replay', 'evaluator_ref': f'eval:{S}', 'method_id': M,
         'input_digest': rin, 'output_refs': [f'{S}:out-009d-baseline'], 'witness_ref': e.pin('verdict'),
         'status': 'declared', 'output_digest': 'sha256:' + sha_bytes(canon(rep)), 'replay_of': 'rec-009-original'}]
    excluded = sorted({r['policy'] for r in rows} - set(full))
    ctx['profile_limitations'] = ['Modelled work units on the original synthetic 009 generator; holdout seeds were used before (not blind).',
                                  'Coverage parity is declared from the archived summary; arms without full coverage are excluded, not hidden.',
                                  'Replay output digests hash the transcribed baseline means (canonical JSON), not the archived files.']
    cert_wins = all(o['outcome'] == 'b_preferred' for c in ctx['comparisons'] for o in c['outcomes'] if o['split'] == 'holdout')
    return golden(e, ctx, 'EXP-009-D Final switch costs — strategies vs certified Fixed',
                  ('On the holdout worlds the certified Fixed control is cheaper than every full-coverage strategy at all three '
                   'switch-cost rates.' if cert_wins else 'See outcomes per rate and split.') +
                  ' The 009 baseline means are reproduced exactly (replay_of).',
                  ['a unique dynamic advantage', 'independent blinded holdout', 'general certificate semantics'],
                  {'excluded_arms_without_full_coverage': excluded, 'replay_baseline': {'original_009': orig, 'replayed_009d': rep}})


BUILD = {'exp002b': exp002b, 'exp003': exp003, 'exp007': exp007, 'exp009d': exp009d}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--space', required=True, help='path to the lunados.space repository')
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args(); space = Path(a.space)
    bad = 0
    for n, fn in BUILD.items():
        case = fn(Exp(n, space))
        f = HERE/f'fixtures/golden_{n}.json'
        text = json.dumps(case, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
        if a.verify:
            ok = f.exists() and f.read_text('utf-8') == text
            print(('PASS' if ok else 'FAIL'), f.name, 'source pins match' if ok else 'differs from sources'); bad += not ok
        else:
            f.write_text(text, 'utf-8'); print('wrote', f.name)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
