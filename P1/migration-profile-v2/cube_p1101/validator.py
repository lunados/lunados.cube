"""Additive P1.10.1 validator. Frozen P1.1…P1.10 executable files are NOT edited.

/1 … /5 delegate unconditionally to P1.10.
/6 runs P1.10 on a lossless /5 projection and then adds only the dependency-gap rule
(DG-1…DG-8): a dependency that ends before the target phase must be explained by a
declaration. No live system is checked; no reason is inferred.
"""
from __future__ import annotations
from cube_semantic.validator import SemanticValidator as FrozenValidator, join
from cube_resolver.resolver import validate_context as validate_context_v1
from cube_p16.instantiation import validate_context_v2
from cube_p110.validator import P110Validator, CODES as P110_CODES
from cube_p1101.migration import FORMAT6, END_REASONS, project_v5, validate_context_v6 as _validate_v6

PROFILE = 'P1.10.1/migration-profile-v2'
CODES = {
    'P1_MIGRATION_DEPENDENCY_GAP': ('scope_consistency', 'Morphology v9.4 §5.10 / P1.10.1 DG-1…DG-6: dependency ends before the target '
                                    'phase without retirement of its object or subject, successor_ref, dropped or a declared ends_reason'),
    'P1_MIGRATION_SUCCESSOR_INVALID': (P110_CODES['P1_MIGRATION_SUCCESSOR_INVALID'][0],
                                       'P1.10 DP-4 / P1.10.1 D-5: successor of a gap end must share subject and predicate and start at the next phase'),
}
_LABEL = {'scope_consistency': 'scope'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


class P1101Validator:
    def __init__(self):
        self.p110 = P110Validator()
        self.concepts = self.p110.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT6:
            return _validate_v6(ctx, validate_context_v2, validate_context_v1, self.concepts)
        return self.p110.validate_context(ctx)

    # -- DG ------------------------------------------------------------------
    def _gaps(self, i, mp, out):
        base = f'/migration_plans/{i}'
        phases = mp['phases']
        pids = [p['phase_id'] for p in phases]
        roles = [p['role'] for p in phases]
        if not (roles.count('current') == 1 and roles.count('target') == 1 and roles[0] == 'current'
                and roles[-1] == 'target' and len(set(pids)) == len(pids)):
            return                                            # DG-1: P1.10 PH-1 already reports the plan
        idx = {p: k for k, p in enumerate(pids)}
        target = len(pids)-1
        retire, intro = {}, {}
        for t in mp['transitions']:
            k = idx.get(t['at_phase'])
            if k is None:
                continue
            for r in t['retires']:
                retire.setdefault(r, []).append(k)
            for r in t['introduces']:
                intro.setdefault(r, []).append(k)
        conflict = {r for r in set(retire) | set(intro)
                    if len(retire.get(r, [])) > 1 or len(intro.get(r, [])) > 1
                    or (r in retire and r in intro and min(retire[r]) <= min(intro[r]))}
        R = {r: min(v) for r, v in retire.items()}
        deps = {d['dependency_id']: d for d in mp['dependencies']}

        def span(d):
            ks = [idx.get(p) for p in d['holds_in']]
            if any(k is None for k in ks):
                return None
            ks = sorted(ks)
            return ks if ks == list(range(ks[0], ks[-1]+1)) else None

        for j, d in enumerate(mp['dependencies']):
            dp = f'{base}/dependencies/{j}'
            sp = span(d)
            if sp is None:
                continue                                      # DG-1: DP-1 reported by P1.10
            k = sp[-1]
            if k >= target:
                continue                                      # DG-4
            o, s = d['object'], d['subject']
            if o in conflict or s in conflict:
                continue                                      # DG-7
            if o in R and R[o] <= k+1:
                continue                                      # DG-4/DG-7: DP-3 or DP-4 territory
            if s in R and R[s] <= k+1:
                continue                                      # D-3: subject retired
            if d.get('dropped'):
                continue
            succ = d.get('successor_ref')
            if succ is not None:
                if succ not in deps:
                    continue                                  # DG-8: REFERENCE_MISSING by P1.10
                n = deps[succ]
                ns = span(n)
                if n['subject'] != s or n['predicate_id'] != d['predicate_id'] or ns is None or ns[0] != k+1:
                    out.append(_d('P1_MIGRATION_SUCCESSOR_INVALID', 'FAIL', dp+'/successor_ref',
                                  'Successor ' + repr(succ) + ' must share subject and predicate and start at ' + repr(pids[k+1]) + ' (D-5).'))
                continue
            reason = d.get('ends_reason')
            if reason is not None:
                if reason in END_REASONS and d.get('witness_ref'):
                    continue
                out.append(_d('P1_MIGRATION_DEPENDENCY_GAP', 'UNRESOLVED', dp+'/ends_reason',
                              'ends_reason ' + repr(reason) + ' does not explain the end: use scope_end, replaced_outside_plan or other '
                              'with a witness_ref (DG-6).'))
                continue
            later = f'; {o!r} is retired only at {pids[R[o]]!r}' if o in R else f'; {o!r} is never retired'
            out.append(_d('P1_MIGRATION_DEPENDENCY_GAP', 'UNRESOLVED', dp,
                          f'Ends at {pids[k]!r} before target {pids[target]!r}{later}; no successor_ref, dropped or ends_reason.'))

    # -- main ----------------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT6:
            return self.p110.validate_bytes(raw, input_format=input_format, context=context,
                                            qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p110.validate_bytes(raw, input_format=input_format, context=project_v5(context),
                                          qualification_profiles=qualification_profiles)
        add = []
        for i, mp in enumerate(context.get('migration_plans', [])):
            self._gaps(i, mp, add)
        if not add:
            return report
        checks = report['checks']; diags = report['diagnostics']
        by = {}
        for stage, status, d in add:
            by.setdefault(stage, []).append(status); diags.append(d)
        for stage, sts in by.items():
            cur = [checks[stage]['status']] if checks[stage]['status'] != 'NOT_EVALUATED' else []
            checks[stage] = FrozenValidator._stage(cur + sts, _LABEL[stage])
        report['overall_status'] = join([x['status'] for x in checks.values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


def validate_context(ctx):
    return P1101Validator().validate_context(ctx)
