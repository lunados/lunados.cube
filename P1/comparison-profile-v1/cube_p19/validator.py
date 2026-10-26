"""Additive P1.9 validator. Frozen P1.1-P1.6 and P1.8 executable files are NOT edited.

/1, /2 and /3 delegate unconditionally to P1.8.
/4 runs P1.8 on a lossless /3 projection and then adds only:
  * comparison checks (arms, pairing, confounding, parity, outcomes, splits),
  * replay-against-record checks.
No statistic is computed, no unit list opened, no parity, digest or witness verified.
"""
from __future__ import annotations
from cube_semantic.validator import SemanticValidator as FrozenValidator, join
from cube_resolver.resolver import validate_context as validate_context_v1
from cube_p16.instantiation import validate_context_v2
from cube_p18.simulation import JUDGMENTS
from cube_p18.validator import P18Validator
from cube_p19.comparison import FORMAT4, project_v3, validate_context_v4 as _validate_v4

PROFILE = 'P1.9/comparison-profile-v1'
ANNOTATION = 'Y:identified-object:annotation'
CODES = {
    'P1_COMPARISON_REFERENCE_MISSING': ('referent_binding', 'Morphology v9.4 §5.16 / P1.9: protocol, arm, metric or annotation not declared'),
    'P1_COMPARISON_ARMS': ('scope_consistency', 'Morphology v9.4 §7.32(4) / P1.9 AR-1: >= 2 arms incl. a control'),
    'P1_COMPARISON_PAIRING': ('scope_consistency', 'P1.9 AR-2, AR-4: shared paired units and one scenario mode'),
    'P1_COMPARISON_CONFOUNDED': ('scope_consistency', 'Morphology v9.4 §7.32(4) / P1.9 AR-3: only declared parameters may differ'),
    'P1_COMPARISON_PARITY_MISSING': ('referent_binding', 'P1.9 AR-5, CP-5: required parity witness per treatment arm'),
    'P1_COMPARISON_OUTCOME_INVALID': ('scope_consistency', 'Morphology v9.4 §5.16 / P1.9 OC-1, OC-3, CP-1, CP-3'),
    'P1_COMPARISON_OUTCOME_INCONSISTENT': ('scope_consistency', 'P1.9 OC-4: declared value contradicts outcome under metric direction'),
    'P1_COMPARISON_AGGREGATION_UNDECLARED': ('scope_consistency', 'Morphology v9.4 §5.16 / P1.9 OC-2, CP-2: no implicit total order'),
    'P1_COMPARISON_SPLIT_MIXED': ('scope_consistency', 'Morphology v9.4 Annex E.2 / P1.9 OC-6'),
    'P1_COMPARISON_OUTCOME_CONFLICT': ('scope_consistency', 'P1.9 OC-3: one outcome per (arms, metric, scope, split)'),
    'P1_COMPARISON_OUTCOME_TYPE': ('referent_binding', 'Morphology v9.4 D.4, §5.18 / P1.9 OC-5: outcome is a Y Annotation, never a judgment'),
    'P1_EVALUATION_WITNESS_MISSING': ('referent_binding', 'P1.8 EV-4 / P1.9: declared witness pointer required'),
    'P1_REPLAY_RECORD_MISMATCH': ('referent_binding', 'P1.9 RR-1, RR-2: replay must match method, evaluator and input'),
    'P1_REPLAY_DIVERGENT': ('referent_binding', 'P1.9 RR-3: declared output digests differ'),
    'P1_SCENARIO_MODE': ('scope_consistency', 'Morphology v9.4 §3.1 M / P1.8 SC-2 / P1.9 RR'),
}
_MIRROR = {'a_preferred': 'b_preferred', 'b_preferred': 'a_preferred'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


def _side(value, margin, direction):
    """-1: a better, +1: b better, 0: inside margin. For a delta a-b."""
    if direction == 'higher_better':
        value = -value
    if value < -margin:
        return -1
    if value > margin:
        return 1
    return 0


class P19Validator:
    def __init__(self):
        self.p18 = P18Validator()
        self.concepts = self.p18.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT4:
            return _validate_v4(ctx, validate_context_v2, validate_context_v1, self.concepts)
        return self.p18.validate_context(ctx)

    # -- comparisons ----------------------------------------------------
    def _comparisons(self, ctx, out):
        refs = {r['ref']: r for r in ctx['referents']}
        scen = {s['scenario_id']: s for s in ctx.get('scenarios', [])}
        protos = {p['protocol_id']: p for p in ctx.get('comparison_protocols', [])}
        for i, c in enumerate(ctx.get('comparisons', [])):
            base = f'/comparisons/{i}'
            proto = protos.get(c['protocol_ref'])
            if proto is None:
                out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', base + '/protocol_ref', 'No declared comparison protocol.'))
            arms = {a['arm_id']: a for a in c['arms']}
            # AR-1
            if len(c['arms']) < 2 or not any(a['role'] == 'control' for a in c['arms']):
                out.append(_d('P1_COMPARISON_ARMS', 'FAIL', base + '/arms', 'A comparison needs at least two arms including a control.'))
            arm_sc = {}
            for j, a in enumerate(c['arms']):
                sc = scen.get(a['scenario_ref'])
                if sc is None:
                    out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', f'{base}/arms/{j}/scenario_ref', 'Arm names an undeclared scenario.'))
                else:
                    arm_sc[a['arm_id']] = sc
            if len({a['scenario_ref'] for a in c['arms']}) != len(c['arms']):
                out.append(_d('P1_COMPARISON_PAIRING', 'FAIL', base + '/arms', 'Two arms reference the same scenario.'))
            # AR-2, AR-4
            pr = c['pairing']
            for j, a in enumerate(c['arms']):
                sc = arm_sc.get(a['arm_id'])
                if sc is not None and pr['units_ref'] not in sc['world_refs']:
                    out.append(_d('P1_COMPARISON_PAIRING', 'FAIL', f'{base}/arms/{j}',
                                  'Paired units ' + repr(pr['units_ref']) + ' are not a member of the arm scenario world.'))
            if len({sc['mode'] for sc in arm_sc.values()}) > 1:
                out.append(_d('P1_COMPARISON_PAIRING', 'FAIL', base + '/arms', 'All arms must share one scenario mode.'))
            # AR-3 (equality only; parameters stay uninterpreted)
            if len(arm_sc) >= 2:
                params = [sc.get('parameters', {}) for sc in arm_sc.values()]
                missing = object()
                for k in pr['shared_parameters']:
                    vals = [p.get(k, missing) for p in params]
                    if any(v is missing for v in vals) or any(v != vals[0] or type(v) is not type(vals[0]) for v in vals):
                        out.append(_d('P1_COMPARISON_CONFOUNDED', 'FAIL', base + '/pairing/shared_parameters',
                                      'Shared parameter ' + repr(k) + ' is missing or differs between arms.'))
                keys = set().union(*params) - set(pr['shared_parameters']) - set(pr['varied_parameters'])
                for k in sorted(keys):
                    vals = [p.get(k, missing) for p in params]
                    if any(v is missing for v in vals) or any(v != vals[0] or type(v) is not type(vals[0]) for v in vals):
                        out.append(_d('P1_COMPARISON_CONFOUNDED', 'FAIL', base + '/pairing',
                                      'Parameter ' + repr(k) + ' differs between arms but is not declared varied.'))
            # AR-5, CP-5
            treat = [a['arm_id'] for a in c['arms'] if a['role'] == 'treatment']
            for j, q in enumerate(c.get('parity', [])):
                for x in q.get('arm_refs', []):
                    if x not in arms:
                        out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', f'{base}/parity/{j}/arm_refs', 'Unknown arm ' + repr(x) + '.'))
                if not q.get('witness_ref'):
                    out.append(_d('P1_COMPARISON_PARITY_MISSING', 'UNRESOLVED', f'{base}/parity/{j}', 'Parity declaration without witness.'))
            for kind in (proto or {}).get('required_parity', []):
                for t in treat:
                    if not any(q['kind'] == kind and q.get('witness_ref') and t in q.get('arm_refs', treat) for q in c.get('parity', [])):
                        out.append(_d('P1_COMPARISON_PARITY_MISSING', 'UNRESOLVED', base + '/parity',
                                      'Treatment arm ' + repr(t) + ' has no ' + repr(kind) + ' parity witness.'))
            # Outcomes
            crit = {m['metric_id']: m for m in (proto or {}).get('criteria', [])}
            margin = (proto or {}).get('equivalence_margin', {})
            factors = c.get('design', {}).get('factors', {})
            splits = c.get('splits')
            seen = {}
            for j, o in enumerate(c.get('outcomes', [])):
                op = f'{base}/outcomes/{j}'
                for side in ('a', 'b'):
                    if o[side] not in arms:
                        out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', f'{op}/{side}', 'Unknown arm ' + repr(o[side]) + '.'))
                mids = [o['metric_id']] if 'metric_id' in o else o['metric_ids']
                if proto is not None:
                    for m in mids:
                        if m not in crit:
                            out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', op, 'Metric ' + repr(m) + ' is not a protocol criterion.'))
                if len(mids) > 1 and (proto or {}).get('aggregation', 'none') == 'none':
                    out.append(_d('P1_COMPARISON_AGGREGATION_UNDECLARED', 'FAIL', op,
                                  'An outcome over several metrics needs a declared aggregation method.'))
                val = o['outcome']
                if val not in ('a_preferred', 'b_preferred', 'equivalent_under_criteria',
                               'incomparable_under_criteria', 'undetermined_with_available_evidence'):
                    out.append(_d('P1_COMPARISON_OUTCOME_INVALID', 'FAIL', op + '/outcome', 'Outcome ' + repr(val) + ' is outside the §5.16 vocabulary.'))
                single = mids[0] if len(mids) == 1 else None
                cr = crit.get(single) if single else None
                if cr is not None:
                    if cr['direction'] == 'none' and val in _MIRROR:
                        out.append(_d('P1_COMPARISON_OUTCOME_INVALID', 'FAIL', op + '/outcome', 'A metric without direction cannot express a preference.'))
                    if val == 'equivalent_under_criteria' and single not in margin:
                        out.append(_d('P1_COMPARISON_OUTCOME_INVALID', 'FAIL', op + '/outcome', 'Equivalence needs a declared margin for ' + repr(single) + '.'))
                for k, v in o.get('scope', {}).items():
                    if k not in factors or not any(type(v) is type(x) and v == x for x in factors[k]):
                        out.append(_d('P1_COMPARISON_OUTCOME_INVALID', 'FAIL', op + '/scope', 'Scope ' + repr(k) + '=' + repr(v) + ' is not a declared design level.'))
                # OC-6
                if splits is not None or 'split' in o:
                    if splits is None or o.get('split') not in splits:
                        out.append(_d('P1_COMPARISON_SPLIT_MIXED', 'FAIL', op + '/split', 'Outcome must name exactly one declared split.'))
                # OC-4 sign check
                st = o.get('statistic')
                if st and cr is not None and cr['direction'] != 'none' and st['kind'] != 'declared_other' and val in OUTCOMES_SIGNED:
                    mg = margin.get(single, 0.0)
                    v = st['declared_value']
                    if st['kind'] == 'delta_a_minus_b':
                        sides = {_side(v, mg, cr['direction'])}
                    elif st['kind'] == 'ratio_a_over_b':
                        sides = {_side(v - 1.0, mg, cr['direction'])}
                    else:
                        sides = {_side(v[0], mg, cr['direction']), _side(v[1], mg, cr['direction'])}
                    if val == 'a_preferred':
                        ok = sides == {-1}
                    elif val == 'b_preferred':
                        ok = sides == {1}
                    elif val == 'equivalent_under_criteria':
                        ok = sides == {0}
                    else:                                   # undetermined: not entirely on one side
                        ok = sides not in ({-1}, {1})
                    if not ok:
                        out.append(_d('P1_COMPARISON_OUTCOME_INCONSISTENT', 'FAIL', op + '/statistic',
                                      'Declared value does not support ' + repr(val) + ' under ' + repr(cr['direction']) + '.'))
                # OC-5
                t = refs.get(o['annotation_ref'])
                if t is None:
                    out.append(_d('P1_COMPARISON_REFERENCE_MISSING', 'UNRESOLVED', op + '/annotation_ref', 'Outcome annotation is not a declared referent.'))
                elif t['concept_id'] != ANNOTATION:
                    out.append(_d('P1_COMPARISON_OUTCOME_TYPE', 'FAIL', op + '/annotation_ref',
                                  'An outcome is a Y Annotation claim' + (', never an X judgment.' if t['concept_id'] in JUDGMENTS else '.')))
                if not o.get('witness_ref'):
                    out.append(_d('P1_EVALUATION_WITNESS_MISSING', 'UNRESOLVED', op + '/witness_ref', 'Outcome requires a declared witness pointer.'))
                # OC-3 conflict (mirrored pairs are the same comparison)
                if o['a'] <= o['b']:
                    key, norm = (o['a'], o['b']), val
                else:
                    key, norm = (o['b'], o['a']), _MIRROR.get(val, val)
                key = key + (tuple(sorted(mids)), tuple(sorted((k, repr(v)) for k, v in o.get('scope', {}).items())), o.get('split'))
                if key in seen and seen[key] != norm:
                    out.append(_d('P1_COMPARISON_OUTCOME_CONFLICT', 'FAIL', op, 'Conflicts with an earlier outcome for the same arms, metric, scope and split.'))
                seen.setdefault(key, norm)

    # -- replay against record -------------------------------------------
    def _replays(self, ctx, out):
        recs = {r['record_id']: r for r in ctx.get('evaluation_records', [])}
        scen = {s['scenario_id']: s for s in ctx.get('scenarios', [])}
        for i, r in enumerate(ctx.get('evaluation_records', [])):
            if 'replay_of' not in r:
                continue
            base = f'/evaluation_records/{i}'
            sc = scen.get(r['scenario_ref'])
            if sc is not None and sc['mode'] != 'replay':
                out.append(_d('P1_SCENARIO_MODE', 'FAIL', base + '/replay_of', 'replay_of requires a scenario in replay mode.'))
            orig = recs.get(r['replay_of'])
            if orig is None:
                out.append(_d('P1_REPLAY_RECORD_MISMATCH', 'FAIL', base + '/replay_of', 'Replayed record is not declared.'))
                continue
            for k in ('method_id', 'evaluator_ref', 'input_digest'):
                if r[k] != orig[k]:
                    out.append(_d('P1_REPLAY_RECORD_MISMATCH', 'FAIL', f'{base}/{k}', 'Differs from the replayed record (string comparison only).'))
            if 'output_digest' in r and 'output_digest' in orig and r['output_digest'] != orig['output_digest']:
                st = 'FAIL' if r['status'] == 'declared' else 'UNRESOLVED'
                out.append(_d('P1_REPLAY_DIVERGENT', st, base + '/output_digest',
                              'Declared output digest differs from the replayed record; equal digests would not mean verified.'))

    # -- main -------------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT4:
            return self.p18.validate_bytes(raw, input_format=input_format, context=context,
                                           qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p18.validate_bytes(raw, input_format=input_format, context=project_v3(context),
                                         qualification_profiles=qualification_profiles)
        add = []
        self._comparisons(context, add)
        self._replays(context, add)
        if not add:
            return report
        checks = report['checks']; diags = report['diagnostics']
        by = {}
        for stage, status, d in add:
            by.setdefault(stage, []).append(status); diags.append(d)
        for stage, sts in by.items():
            cur = [checks[stage]['status']] if checks[stage]['status'] != 'NOT_EVALUATED' else []
            label = {'scope_consistency': 'scope', 'referent_binding': 'referent'}[stage]
            checks[stage] = FrozenValidator._stage(cur + sts, label)
        order = list(checks)
        diags.sort(key=lambda d: (d.get('byte_start', 10**12), d['code'],
                                  order.index(d['stage']) if d['stage'] in order else 99, d['message']))
        report['overall_status'] = join([x['status'] for x in checks.values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


OUTCOMES_SIGNED = ('a_preferred', 'b_preferred', 'equivalent_under_criteria', 'undetermined_with_available_evidence')


def validate_context(ctx):
    return P19Validator().validate_context(ctx)
