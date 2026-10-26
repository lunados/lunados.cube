"""Additive P1.10 validator. Frozen P1.1-P1.6, P1.8 and P1.9 executable files are NOT edited.

/1 ... /4 delegate unconditionally to P1.9.
/5 runs P1.9 on a /4 projection (imported predicate contracts bound to scope_ref)
and then adds only structural checks of the declared migration plans.
No dependency is discovered, no live system probed, no date compared, no order chosen.
"""
from __future__ import annotations
from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_parser.parser import parse_result
from cube_resolver.resolver import validate_context as validate_context_v1
from cube_p16.instantiation import validate_context_v2
from cube_p19.validator import P19Validator
from cube_p110.migration import FORMAT5, project_v4, imported_contracts, validate_context_v5 as _validate_v5

PROFILE = 'P1.10/migration-profile-v1'
CODES = {
    'P1_MIGRATION_PHASES': ('scope_consistency', 'Morphology v9.4 §5.10 / P1.10 PH-1, DP-1: one current first, one target last, unique phases, contiguous holds_in'),
    'P1_MIGRATION_REFERENCE_MISSING': ('referent_binding', 'Morphology v9.4 §2.9 / C011 / P1.10 TR-1, DP-2, DP-4: phase, referent or dependency not declared'),
    'P1_MIGRATION_DANGLING_DEPENDENCY': ('scope_consistency', 'P1.10 DP-3: dependency holds in or after the phase that retires its object'),
    'P1_MIGRATION_SUCCESSOR_MISSING': ('scope_consistency', 'P1.10 DP-4: dependency ends at a retiring phase without successor_ref or dropped'),
    'P1_MIGRATION_SUCCESSOR_INVALID': ('scope_consistency', 'P1.10 DP-4: successor must share subject and predicate, start at the retiring phase, point at an existing referent'),
    'P1_MIGRATION_PREMATURE_DEPENDENCY': ('scope_consistency', 'P1.10 TR-1, DP-3: dependency holds before its object is introduced'),
    'P1_MIGRATION_TRANSITION_CONFLICT': ('scope_consistency', 'P1.10 TR-2: retired or introduced at most once; introduce before retire'),
    'P1_MIGRATION_SCOPE_MISMATCH': ('scope_consistency', 'P1.10 PP-5 / D-8: plan scope must equal the context scope_ref'),
    'P1_MIGRATION_EXPRESSION_MISMATCH': ('scope_consistency', 'P1.10 D-5: a supersedes claim must match a declared transition'),
    'P1_QUALIFIER_PROFILE_MISSING': ('qualifier_typing', 'Morphology v9.4 §3.6 / P1.10 TR-3, D-4: transition needs T role scheduling and a witness'),
    'P1_PREDICATE_PROFILE_MISSING': ('predicate_typing', 'Morphology v9.4 §7.6.1 R01-AC02 / P1.10 DP-2: no single scoped contract for the dependency predicate'),
    'P1_PREDICATE_SIGNATURE': ('predicate_typing', 'Morphology v9.4 §7.6.1 R01-AC02 / P1.10 DP-2: dependency violates the declared signature'),
    'P1_EVALUATION_WITNESS_MISSING': ('referent_binding', 'P1.8 EV-4 / P1.10 DP-4: dependency requires a declared witness pointer'),
}
_LABEL = {'scope_consistency': 'scope', 'referent_binding': 'referent',
          'predicate_typing': 'predicate typing', 'qualifier_typing': 'qualifier typing'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


class P110Validator:
    def __init__(self):
        self.p19 = P19Validator()
        self.concepts = self.p19.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT5:
            return _validate_v5(ctx, validate_context_v2, validate_context_v1, self.concepts)
        return self.p19.validate_context(ctx)

    # -- plan checks -------------------------------------------------------
    def _plan(self, ctx, i, mp, contracts, out):
        base = f'/migration_plans/{i}'
        refs = {r['ref']: r for r in ctx['referents']}
        if mp['scope'] != ctx.get('scope_ref'):
            out.append(_d('P1_MIGRATION_SCOPE_MISMATCH', 'UNRESOLVED', base + '/scope', 'Plan scope differs from the context scope_ref.'))
        # PH-1
        phases = mp['phases']; pids = [p['phase_id'] for p in phases]
        idx = {}
        for k, p in enumerate(pids):
            idx.setdefault(p, k)
        roles = [p['role'] for p in phases]
        ok_phases = (roles.count('current') == 1 and roles.count('target') == 1 and roles[0] == 'current'
                     and roles[-1] == 'target' and len(set(pids)) == len(pids))
        if not ok_phases:
            out.append(_d('P1_MIGRATION_PHASES', 'FAIL', base + '/phases',
                          'Exactly one current phase first, one target phase last, unique phase_ids required.'))
        # Transitions (TR-1..TR-3)
        intro, retire = {}, {}
        for j, t in enumerate(mp['transitions']):
            tp = f'{base}/transitions/{j}'
            at = idx.get(t['at_phase'])
            if at is None:
                out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', tp + '/at_phase', 'Undeclared phase ' + repr(t['at_phase']) + '.'))
            for key, store in (('retires', retire), ('introduces', intro)):
                for r in t[key]:
                    if r not in refs:
                        out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', f'{tp}/{key}', 'Undeclared referent ' + repr(r) + '.'))
                    elif at is not None:
                        store.setdefault(r, []).append(at)
            if 'T' not in t or t['T']['role'] != 'scheduling':
                out.append(_d('P1_QUALIFIER_PROFILE_MISSING', 'UNRESOLVED', tp + '/T',
                              'Transition requires a T qualifier with role scheduling (D-4).'))
            if not t.get('witness_ref'):
                out.append(_d('P1_QUALIFIER_PROFILE_MISSING', 'UNRESOLVED', tp + '/witness_ref', 'Transition requires a witness pointer.'))
        conflict = set()
        for r in sorted(set(intro) | set(retire)):
            if len(retire.get(r, [])) > 1 or len(intro.get(r, [])) > 1 or \
               (r in intro and r in retire and min(retire[r]) <= min(intro[r])):
                conflict.add(r)
                out.append(_d('P1_MIGRATION_TRANSITION_CONFLICT', 'FAIL', base + '/transitions',
                              'Referent ' + repr(r) + ' is retired or introduced twice, or retired before it is introduced.'))
        R = {r: min(v) for r, v in retire.items()}
        I = {r: min(v) for r, v in intro.items()}

        def exists(r, k):
            return (r not in I or I[r] <= k) and (r not in R or k < R[r])

        ordering = ok_phases
        deps = {d['dependency_id']: d for d in mp['dependencies']}
        spans = {}
        for j, d in enumerate(mp['dependencies']):
            ks = [idx[p] for p in d['holds_in'] if p in idx]
            if len(ks) == len(d['holds_in']):
                spans[d['dependency_id']] = sorted(ks)
        for j, d in enumerate(mp['dependencies']):
            dp = f'{base}/dependencies/{j}'
            undeclared = [p for p in d['holds_in'] if p not in idx]
            for p in undeclared:
                out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', dp + '/holds_in', 'Undeclared phase ' + repr(p) + '.'))
            known = True
            for side in ('subject', 'object'):
                if d[side] not in refs:
                    known = False
                    out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', f'{dp}/{side}', 'Undeclared referent ' + repr(d[side]) + '.'))
            # DP-2 typing
            if known:
                cs = [c for c in contracts if c['predicate_id'] == d['predicate_id']]
                if len(cs) != 1:
                    out.append(_d('P1_PREDICATE_PROFILE_MISSING', 'UNRESOLVED', dp + '/predicate_id',
                                  ('No' if not cs else 'Ambiguous') + ' scoped contract for ' + repr(d['predicate_id']) + '.'))
                else:
                    c = cs[0]
                    if refs[d['subject']]['concept_id'] not in c['subject_concept_ids'] or \
                       refs[d['object']]['concept_id'] not in c['object_concept_ids']:
                        out.append(_d('P1_PREDICATE_SIGNATURE', 'FAIL', dp,
                                      'Predicate ' + repr(d['predicate_id']) + ' does not admit the directed (subject,object) concept IDs.'))
                    elif c.get('required_qualifiers'):
                        out.append(_d('P1_PREDICATE_SIGNATURE', 'FAIL', dp,
                                      'Required predicate-level qualifier(s) absent: ' + ','.join(sorted(c['required_qualifiers'])) + '.'))
            if not d.get('witness_ref'):
                out.append(_d('P1_EVALUATION_WITNESS_MISSING', 'UNRESOLVED', dp + '/witness_ref', 'Dependency requires a declared witness pointer.'))
            succ = d.get('successor_ref')
            if succ is not None and succ not in deps:
                out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', dp + '/successor_ref', 'Undeclared dependency ' + repr(succ) + '.'))
            span = spans.get(d['dependency_id'])
            if not ordering or span is None:
                continue
            # DP-1
            if span != list(range(span[0], span[-1] + 1)):
                out.append(_d('P1_MIGRATION_PHASES', 'FAIL', dp + '/holds_in', 'holds_in must be a contiguous run of declared phases.'))
                continue
            o = d['object']
            if o in conflict:
                continue
            if o in R and span[-1] >= R[o]:
                out.append(_d('P1_MIGRATION_DANGLING_DEPENDENCY', 'FAIL', dp + '/holds_in',
                              'Holds in ' + repr(pids[span[-1]]) + ' but its object ' + repr(o) + ' is retired at ' + repr(pids[R[o]]) + '.'))
            if o in I and span[0] < I[o]:
                out.append(_d('P1_MIGRATION_PREMATURE_DEPENDENCY', 'FAIL', dp + '/holds_in',
                              'Holds in ' + repr(pids[span[0]]) + ' before its object ' + repr(o) + ' is introduced at ' + repr(pids[I[o]]) + '.'))
            if o in R and span[-1] == R[o] - 1:
                if succ is None and not d.get('dropped'):
                    out.append(_d('P1_MIGRATION_SUCCESSOR_MISSING', 'UNRESOLVED', dp,
                                  'Ends at the retirement of ' + repr(o) + ' without successor_ref or dropped.'))
                elif succ in deps:
                    s = deps[succ]; ss = spans.get(succ)
                    bad = (s['subject'] != d['subject'] or s['predicate_id'] != d['predicate_id'] or ss is None
                           or ss[0] != R[o] or not all(exists(s['object'], k) for k in ss))
                    if bad:
                        out.append(_d('P1_MIGRATION_SUCCESSOR_INVALID', 'FAIL', dp + '/successor_ref',
                                      'Successor ' + repr(succ) + ' must share subject and predicate, start at ' + repr(pids[R[o]]) +
                                      ' and point at a referent present in every phase it holds in.'))
        return retire, intro

    def _expression(self, raw, input_format, plans_ti, out):
        """D-5: a supersedes(Y, X) claim must match a transition retiring X and introducing Y."""
        parsed = parse_result(raw, input_format=input_format)
        if parsed['structure_status'] != 'PASS':
            return
        for path, node, _ in nodes(parsed['ast']):
            if node['kind'] != 'relation' or node['predicate_id'] != 'supersedes':
                continue
            s, o = node['subject'], node['object']
            while s['kind'] == 'qualified': s = s['expression']
            while o['kind'] == 'qualified': o = o['expression']
            if s['kind'] != 'reference' or o['kind'] != 'reference':
                continue
            y, x = s.get('referent_ref'), o.get('referent_ref')
            if not any(x in t['retires'] and y in t['introduces'] for ts in plans_ti for t in ts):
                out.append(_d('P1_MIGRATION_EXPRESSION_MISMATCH', 'FAIL', '/migration_plans',
                              'Expression ' + path + ' claims ' + repr(y) + ' supersedes ' + repr(x) + ' but no declared transition retires it for it.'))

    # -- main ----------------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT5:
            return self.p19.validate_bytes(raw, input_format=input_format, context=context,
                                           qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p19.validate_bytes(raw, input_format=input_format, context=project_v4(context),
                                         qualification_profiles=qualification_profiles)
        plans = context.get('migration_plans', [])
        if not plans:
            return report
        scope = context['scope_ref'] if context.get('scope_ref') else None
        contracts = imported_contracts(context) + [p for p in context.get('predicate_contracts', []) if scope and p['scope'] == scope]
        add = []
        for i, mp in enumerate(plans):
            self._plan(context, i, mp, contracts, add)
        self._expression(raw, input_format, [mp['transitions'] for mp in plans], add)
        if not add:
            return report
        checks = report['checks']; diags = report['diagnostics']
        by = {}
        for stage, status, d in add:
            by.setdefault(stage, []).append(status); diags.append(d)   # plan order, then item index (P1.10-09)
        for stage, sts in by.items():
            cur = [checks[stage]['status']] if checks[stage]['status'] != 'NOT_EVALUATED' else []
            checks[stage] = FrozenValidator._stage(cur + sts, _LABEL[stage])
        report['overall_status'] = join([x['status'] for x in checks.values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


def validate_context(ctx):
    return P110Validator().validate_context(ctx)
