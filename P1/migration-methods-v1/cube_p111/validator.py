"""Additive P1.11 validator. Frozen P1.1…P1.10.1 executable files are NOT edited.

/1 … /6 delegate unconditionally to P1.10.1.
/7 runs P1.10.1 on a /6 projection (bindings removed, imported catalog methods added as scoped
contracts, so `@F(method=…)` resolves through the unchanged P1.4 check) and then adds only the
method-binding rules MB/MP/MV. Nothing is executed, scheduled, ranked or admitted.
"""
from __future__ import annotations
from cube_semantic.validator import SemanticValidator as FrozenValidator, join
from cube_resolver.resolver import validate_context as validate_context_v1
from cube_p16.instantiation import validate_context_v2
from cube_p110.validator import CODES as P110_CODES
from cube_p1101.validator import P1101Validator
from cube_p111.methods import FORMAT7, catalog_methods, project_v6, validate_context_v7 as _validate_v7

PROFILE = 'P1.11/migration-methods-v1'
CODES = {
    'P1_MIGRATION_METHOD_UNKNOWN': ('method_typing', 'P1.11 MB-1…MB-3: bound method is neither imported from a pinned catalog nor declared locally'),
    'P1_MIGRATION_METHOD_SIGNATURE': ('method_typing', 'P1.11 MC-3, MB-3, MV-5: binding roles, arity or argument concept types do not match the method'),
    'P1_MIGRATION_METHOD_PLAN': ('scope_consistency', 'P1.11 MP-1…MP-4, MV-2…MV-4: binding contradicts the declared plan'),
    'P1_MIGRATION_REFERENCE_MISSING': P110_CODES['P1_MIGRATION_REFERENCE_MISSING'],
}
_LABEL = {'scope_consistency': 'scope', 'method_typing': 'method typing', 'referent_binding': 'referent'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


class P111Validator:
    def __init__(self):
        self.p1101 = P1101Validator()
        self.concepts = self.p1101.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT7:
            return _validate_v7(ctx, validate_context_v2, validate_context_v1, self.concepts)
        return self.p1101.validate_context(ctx)

    # -- MB / MP / MV ----------------------------------------------------------
    def _bindings(self, ctx, out):
        catalog = catalog_methods(ctx)
        scope = ctx.get('scope_ref')
        local = {m['method_id']: m for m in ctx.get('method_contracts', []) if isinstance(m, dict) and m.get('scope') == scope}
        refs = {r['ref']: r.get('concept_id') for r in ctx.get('referents', []) if isinstance(r, dict) and 'ref' in r}
        for i, mp in enumerate(ctx.get('migration_plans', [])):
            pids = [p['phase_id'] for p in mp['phases']]
            idx = {p: k for k, p in enumerate(pids)}
            intro = {}
            for t in mp['transitions']:
                k = idx.get(t['at_phase'])
                for r in t['introduces']:
                    if k is not None:
                        intro[r] = min(k, intro.get(r, k))
            deps = {d['dependency_id']: d for d in mp['dependencies']}
            for j, t in enumerate(mp['transitions']):
                for n, b in enumerate(t.get('methods', [])):
                    self._one(f'/migration_plans/{i}/transitions/{j}/methods/{n}', b, 'transition', t, None, idx, intro, deps,
                              catalog, local, refs, out)
            for j, d in enumerate(mp['dependencies']):
                if 'method' in d:
                    self._one(f'/migration_plans/{i}/dependencies/{j}/method', d['method'], 'dependency', None, d, idx, intro, deps,
                              catalog, local, refs, out)

    def _one(self, path, b, point, t, d, idx, intro, deps, catalog, local, refs, out):
        mid, args = b['method_id'], b['arguments']
        m = catalog.get(mid)
        if m is None and mid not in local:
            out.append(_d('P1_MIGRATION_METHOD_UNKNOWN', 'UNRESOLVED', path + '/method_id', f'Method {mid!r} is not imported or declared.'))
            return
        missing = [r for r in args.values() if r not in refs]
        for r in missing:
            out.append(_d('P1_MIGRATION_REFERENCE_MISSING', 'UNRESOLVED', path + '/arguments', 'Undeclared referent ' + repr(r) + '.'))
        if m is None:                                          # MV-5: local method, positional roles, typing only
            lm = local[mid]
            n = len(args)
            names = [f'arg{k}' for k in range(1, n+1)]
            if sorted(args) != sorted(names) or not lm['argument_min'] <= n <= lm['argument_max']:
                out.append(_d('P1_MIGRATION_METHOD_SIGNATURE', 'FAIL', path + '/arguments',
                              f'Local method {mid!r} takes arg1…argN with {lm["argument_min"]}…{lm["argument_max"]} arguments (MV-5).'))
                return
            ids = lm.get('argument_concept_ids')
            if ids is not None and len(ids) == n:
                for k, want in enumerate(ids):
                    r = args[f'arg{k+1}']
                    if r in refs and refs[r] != want:
                        out.append(_d('P1_MIGRATION_METHOD_SIGNATURE', 'FAIL', f'{path}/arguments/arg{k+1}',
                                      f'{r!r} is {refs[r]}, method expects {want}.'))
            return
        roles = {x['role']: x['concept_ids'] for x in m['roles']}
        if set(args) != set(roles):
            out.append(_d('P1_MIGRATION_METHOD_SIGNATURE', 'FAIL', path + '/arguments',
                          f'{mid} takes roles {sorted(roles)}, got {sorted(args)} (MB-3).'))
            return
        bad = False
        for role, r in args.items():
            if r in refs and refs[r] not in roles[role]:
                out.append(_d('P1_MIGRATION_METHOD_SIGNATURE', 'FAIL', f'{path}/arguments/{role}',
                              f'{r!r} is {refs[r]}, not admissible for role {role} of {mid} (MC-3).'))
                bad = True
        if bad or missing:
            return
        if point not in m['binding_points']:
            out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path, f'{mid} binds to a {m["binding_points"][0]}, not a {point} (MV-2).'))
            return
        name = mid.split('/')[0]
        if point == 'transition':
            k = idx.get(t['at_phase'])
            if k is None:
                return                                         # P1.10 reports the undeclared phase
            if name == 'migrate.retire' and args['retired'] not in t['retires']:
                out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path + '/arguments/retired',
                              f'{args["retired"]!r} is not retired by transition {t["transition_id"]!r} (MP-1).'))
            if name in ('migrate.import', 'migrate.rebuild'):
                tg = args['target']
                if tg in intro and intro[tg] > k:
                    out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path + '/arguments/target',
                                  f'{tg!r} is introduced only after {t["at_phase"]!r} (MP-2).'))
            if name == 'migrate.reconfigure' and (args['target'] in t['retires'] or args['target'] in t['introduces']):
                out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path + '/arguments/target',
                              f'{args["target"]!r} is retired or introduced by this transition; reconfigure keeps a referent (MP-4).'))
            return
        if name == 'migrate.rewrite':
            succ = d.get('successor_ref')
            if succ is None or succ not in deps:
                out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path, f'rewrite on {d["dependency_id"]!r} needs a declared successor_ref (MP-3).'))
                return
            if args['dependant'] != d['subject']:
                out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path + '/arguments/dependant',
                              f'dependant must be the dependency subject {d["subject"]!r} (MV-3).'))
            if args['new_object'] != deps[succ]['object']:
                out.append(_d('P1_MIGRATION_METHOD_PLAN', 'FAIL', path + '/arguments/new_object',
                              f'new_object must be the successor object {deps[succ]["object"]!r} (MP-3).'))

    # -- main ----------------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT7:
            return self.p1101.validate_bytes(raw, input_format=input_format, context=context,
                                             qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p1101.validate_bytes(raw, input_format=input_format, context=project_v6(context),
                                           qualification_profiles=qualification_profiles)
        add = []
        self._bindings(context, add)
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
    return P111Validator().validate_context(ctx)
