"""Additive P1.12 validator. Frozen P1.1…P1.11 executable files are NOT edited.

/1 … /7 delegate unconditionally to P1.11.
/8 runs P1.11 on a /7 projection (coverage declarations, population rules, instance_ref and
requires_same_instance removed) and then adds only the P1.12 rules CV/PR (context checks) and IN
(statement check). P1 never evaluates a population rule (PR-2); that is the LIB entry's job (D-6).
"""
from __future__ import annotations
from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_parser.parser import parse_result
from cube_resolver.resolver import Resolver
from cube_p111.validator import P111Validator
from cube_p112.coverage import FORMAT8, INSTANCE_CONCEPT, covering, decl_refs, project_v7, rule_refs, validate_context_v8

PROFILE = 'P1.12/coverage-instance-profile-v1'
_FROZEN = Resolver().diag_contract
CODES = {
    'P1_COVERAGE_UNDECLARED': ('scope_consistency', 'P1.12 CV-3, PR-2, D-3: population rule not covered by any coverage declaration'),
    'P1_INSTANCE_MISMATCH': ('scope_consistency', 'P1.12 IN-3, D-4: predicate requires the same instance; endpoints belong to different instances'),
    'P1_INSTANCE_UNDECLARED': ('scope_consistency', 'P1.12 IN-3, D-4: predicate requires the same instance; instance_ref missing on an endpoint'),
    'P1_BINDING_CONTEXT_REQUIRED': (_FROZEN['P1_BINDING_CONTEXT_REQUIRED']['stage'], _FROZEN['P1_BINDING_CONTEXT_REQUIRED']['reference_rule']),
}
_LABEL = {'scope_consistency': 'scope', 'referent_binding': 'referent'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


def _unwrap(n):
    while n['kind'] == 'qualified':
        n = n['expression']
    return n


class P112Validator:
    def __init__(self):
        self.p111 = P111Validator()
        self.concepts = self.p111.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT8:
            return validate_context_v8(ctx, self.p111.validate_context)
        return self.p111.validate_context(ctx)

    # -- IN-1, CV, PR: context checks ------------------------------------------
    def _context_checks(self, ctx, out):
        refs = {r['ref']: r for r in ctx.get('referents', [])}
        scope = ctx.get('scope_ref')
        preds = {p['predicate_id'] for p in ctx.get('predicate_contracts', []) if p.get('scope') == scope}
        bad_instance = set()
        for i, r in enumerate(ctx.get('referents', [])):
            if 'instance_ref' in r:
                t = refs.get(r['instance_ref'])
                if t is None or t['concept_id'] != INSTANCE_CONCEPT:
                    bad_instance.add(r['ref'])
                    out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', f'/referents/{i}/instance_ref',
                                  f'{r["instance_ref"]!r} is not a declared referent of concept {INSTANCE_CONCEPT} (IN-1).'))

        def resolvable(items, path, pred):
            ok = True
            for field, v in items:
                if v not in refs or (field == 'instance_ref' and refs[v]['concept_id'] != INSTANCE_CONCEPT):
                    out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', f'{path}/{field}', f'Undeclared or untyped referent {v!r} (Q-4).'))
                    ok = False
            if pred not in preds:
                out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', f'{path}/predicate_id', f'No scoped predicate contract {pred!r} (Q-4).'))
                ok = False
            return ok

        decls = ctx.get('coverage_declarations', [])
        for i, d in enumerate(decls):
            resolvable(decl_refs(d), f'/coverage_declarations/{i}', d['predicate_id'])
        for i, r in enumerate(ctx.get('population_rules', [])):
            if not resolvable(rule_refs(r), f'/population_rules/{i}', r['predicate_id']):
                continue                                       # no double report (§2 precedence)
            if not covering(r, decls):
                out.append(_d('P1_COVERAGE_UNDECLARED', 'UNRESOLVED', f'/population_rules/{i}',
                              f'{r["kind"]} rule {r["rule_id"]!r} is not covered by any coverage declaration; '
                              'absence or count stays unknown, not zero (CV-3, D-3).'))
        return bad_instance

    # -- IN-3: statement check ---------------------------------------------------
    def _instance_checks(self, raw, input_format, ctx, bad_instance, out):
        parsed = parse_result(raw, input_format=input_format)
        if parsed['structure_status'] != 'PASS':
            return
        scope = ctx.get('scope_ref')
        same = {p['predicate_id'] for p in ctx.get('predicate_contracts', []) if p.get('scope') == scope and p.get('requires_same_instance') is True}
        inst = {r['ref']: r.get('instance_ref') for r in ctx.get('referents', [])}
        for path, node, _ in nodes(parsed['ast']):
            if node['kind'] != 'relation' or node['predicate_id'] not in same:
                continue
            ends = [_unwrap(node['subject']), _unwrap(node['object'])]
            if any(e['kind'] != 'reference' for e in ends):
                continue
            a, b = (e['referent_ref'] for e in ends)
            if a in bad_instance or b in bad_instance:
                continue                                       # already reported as BINDING_CONTEXT_REQUIRED
            ia, ib = inst.get(a), inst.get(b)
            where = path or '/'
            if ia is None or ib is None:
                missing = [x for x, i in ((a, ia), (b, ib)) if i is None]
                out.append(_d('P1_INSTANCE_UNDECLARED', 'UNRESOLVED', where,
                              f'{node["predicate_id"]!r} requires the same instance; no instance_ref on {missing} (IN-3).'))
            elif ia != ib:
                out.append(_d('P1_INSTANCE_MISMATCH', 'FAIL', where,
                              f'{node["predicate_id"]!r} requires the same instance; {a!r} is in {ia!r}, {b!r} is in {ib!r} (IN-3).'))

    # -- main ----------------------------------------------------------------
    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT8:
            return self.p111.validate_bytes(raw, input_format=input_format, context=context,
                                            qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p111.validate_bytes(raw, input_format=input_format, context=project_v7(context),
                                          qualification_profiles=qualification_profiles)
        add = []
        bad = self._context_checks(context, add)
        self._instance_checks(raw, input_format, context, bad, add)
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
    return P112Validator().validate_context(ctx)
