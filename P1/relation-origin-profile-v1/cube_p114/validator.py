"""P1.14: declared origin checks layered on the unchanged P1.13 validator."""
from __future__ import annotations

from cube_parser.parser import parse_result
from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_p113.validator import P113Validator
from cube_p114.origin import FORMAT10, project_v9, validate_context_v10

PROFILE = 'P1.14/relation-origin-profile-v1'
CODES = {
    'P1_ORIGIN_UNDECLARED': ('predicate_typing', 'P1.14 OR-2, OR-6: opted-in relation origin is required'),
    'P1_ORIGIN_BASIS_MISSING': ('predicate_typing', 'P1.14 OR-3: derived relation requires a basis'),
    'P1_ORIGIN_INVALID': ('predicate_typing', 'P1.14 OR-2…OR-3: invalid origin or forbidden basis'),
    'P1_BINDING_CONTEXT_REQUIRED': ('referent_binding', 'P1.14 OR-4: basis has no declared origin_bases entry'),
}


def _d(code, status, path, message, *, stage=None):
    code_stage, rule = CODES[code]
    stage = stage or code_stage
    return stage, status, {'code': code, 'stage': stage,
                           'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


def _origin_checks(params, path, bases, add, *, stage='predicate_typing'):
    origin = params.get('origin')
    if origin is None and 'origin' not in params:
        add.append(_d('P1_ORIGIN_UNDECLARED', 'UNRESOLVED', path, 'Origin is not declared.', stage=stage))
        return
    if not isinstance(origin, str) or origin not in ('declared', 'derived', 'unknown'):
        add.append(_d('P1_ORIGIN_INVALID', 'FAIL', path, 'Origin must be declared, derived or unknown.', stage=stage))
        return
    if origin != 'derived':
        if 'basis' in params:
            add.append(_d('P1_ORIGIN_INVALID', 'FAIL', path, 'Basis is forbidden for declared or unknown origin.', stage=stage))
        return
    if 'basis' not in params:
        add.append(_d('P1_ORIGIN_BASIS_MISSING', 'UNRESOLVED', path, 'Derived origin needs a basis.', stage=stage))
    elif not isinstance(params['basis'], str) or not params['basis']:
        add.append(_d('P1_ORIGIN_INVALID', 'FAIL', path, 'Basis must name a nonempty basis_id.', stage=stage))
    elif params['basis'] not in bases:
        add.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', path, 'Basis is not declared in origin_bases.'))


class P114Validator:
    def __init__(self):
        self.p113 = P113Validator()
        self.concepts = self.p113.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT10:
            return validate_context_v10(ctx, self.p113.validate_context)
        return self.p113.validate_context(ctx)

    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT10:
            return self.p113.validate_bytes(raw, input_format=input_format, context=context,
                                            qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p113.validate_bytes(raw, input_format=input_format, context=project_v9(context),
                                          qualification_profiles=qualification_profiles)
        parsed = parse_result(raw, input_format=input_format)
        scope = context.get('scope_ref')
        opted = {p['predicate_id'] for p in context['predicate_contracts']
                 if p.get('scope') == scope and p.get('origin_binding') == 'required'}
        bases = {b['basis_id'] for b in context.get('origin_bases', [])}
        add = []
        removed = set()
        if parsed['structure_status'] == 'PASS':
            for path, node, _ in nodes(parsed['ast']):
                if node['kind'] != 'relation' or node['predicate_id'] not in opted:
                    continue
                params = node['parameters']
                # P1.4 has already checked the signature. Only its parameter-contract
                # diagnostic is superseded, and only when no other parameter occurs.
                if params and not set(params) - {'origin', 'basis'}:
                    removed.add(path)
                _origin_checks(params, path, bases, add)
        for i, plan in enumerate(context.get('migration_plans', [])):
            for j, dep in enumerate(plan['dependencies']):
                if dep['predicate_id'] in opted:
                    path = f'/migration_plans/{i}/dependencies/{j}'
                    _origin_checks(dep, path, bases, add, stage='scope_consistency')
        if removed:
            report['diagnostics'] = [d for d in report['diagnostics'] if not (
                d['code'] == 'P1_PREDICATE_PROFILE_MISSING' and
                d['message'].endswith('This P1.1 signature has no typed predicate-parameter contract.') and
                d['message'].split(':', 1)[0] in removed)]
            statuses = [('FAIL' if d['severity'] == 'error' else 'UNRESOLVED')
                        for d in report['diagnostics'] if d['stage'] == 'predicate_typing']
            report['checks']['predicate_typing'] = FrozenValidator._stage(statuses or ['PASS'], 'predicate typing')
        if add:
            by_stage = {}
            for stage, status, diag in add:
                by_stage.setdefault(stage, []).append(status)
                report['diagnostics'].append(diag)
            for stage, statuses in by_stage.items():
                current = report['checks'][stage]['status']
                report['checks'][stage] = FrozenValidator._stage(([] if current == 'NOT_EVALUATED' else [current]) + statuses,
                    {'predicate_typing': 'predicate typing', 'referent_binding': 'referent', 'scope_consistency': 'scope'}[stage])
            report['diagnostics'].sort(key=lambda d: (d.get('byte_start', 10**12), d['code'], d['stage'], d['message']))
        report['overall_status'] = join([c['status'] for c in report['checks'].values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


def validate_context(ctx):
    return P114Validator().validate_context(ctx)
