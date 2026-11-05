#!/usr/bin/env python3
"""VP-12 TASK-079: materialize L-01…L-14 (spec §2a) from one synthetic binding-context/10.

Expected values come only from oracles/independent_l01_l14.json, committed before any VP-12 runtime code.
"""
import hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_l01_l14.json').read_text('utf-8'))
S = 'ctx:ls'
REF = lambda r, c: {'ref': r, 'concept_id': c, 'home': c[0], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': S}  # noqa: E731


def pred(pid, subj, obj, bound=True):
    p = {'predicate_id': pid, 'revision': 'ls:pred/1', 'scope': S, 'origin': 'illustrative_fixture', 'subject_concept_ids': subj,
         'object_concept_ids': obj, 'direction': 'subject_to_object', 'required_qualifiers': [], 'additional_constraints': []}
    if bound:
        p['origin_binding'] = 'required'
    return p


def context():
    A, C, K, R, ADM = ('Y:identity-anchor:actor', 'Z:module-body:connector', 'Z:module-body:core', 'Y:resource-object:resource',
                       'X:endpoint:admission')
    refs = [REF('act:op', A), REF('acc:admin', A), REF('mod.conn', C), REF('mod.core', K), REF('res:mail-old', R),
            REF('res:mail-new', R), REF('res:dns', R), REF('adm', ADM)]
    deps = [('d1', 'act:op', 'invoked-by', 'mod.conn', ['current', 'mvp', 'beta'], {'origin': 'declared'}),
            ('d2', 'mod.conn', 'reads', 'res:mail-old', ['current'], {'origin': 'declared'}),
            ('d3', 'mod.conn', 'reads', 'res:mail-new', ['mvp', 'beta'], {'origin': 'derived', 'basis': 'b-d3'}),
            ('d4', 'res:mail-new', 'hosted-by', 'res:dns', ['mvp', 'beta'], {'origin': 'unknown'}),
            ('d5', 'mod.core', 'gated-by', 'adm', ['beta'], {'origin': 'declared'}),
            ('d6', 'acc:admin', 'configured-by', 'res:mail-new', ['beta'], {})]
    plan = {'plan_id': 'pm-ls', 'revision': 'ls/1', 'scope': S, 'origin': 'illustrative_fixture',
            'phases': [{'phase_id': 'current', 'role': 'current'}, {'phase_id': 'mvp', 'role': 'intermediate'},
                       {'phase_id': 'beta', 'role': 'target'}],
            'transitions': [{'transition_id': 't-mvp', 'at_phase': 'mvp', 'retires': ['res:mail-old'], 'introduces': ['res:mail-new']}],
            'dependencies': [{'dependency_id': i, 'subject': a, 'predicate_id': p, 'object': o, 'kind': 'other', 'holds_in': h, **x}
                             for i, a, p, o, h, x in deps]}
    return {'format': 'aiaeao.cube.binding-context/10', 'reference_version': 'v9.4', 'context_id': 'vp12-ls', 'source_kind': 'illustrative_fixture',
            'scope_ref': S, 'referents': refs,
            'predicate_contracts': [pred('invoked-by', [A], [C]), pred('reads', [C], [R]), pred('hosted-by', [R], [R]),
                                    pred('gated-by', [K], [ADM]), pred('configured-by', [A], [R], bound=False)],
            'origin_bases': [{'basis_id': 'b-d3', 'kind': 'statements', 'statement_ids': ['d2']}],
            'predicate_profile_refs': [], 'method_profile_refs': ['P1.11/migration-methods-v1'], 'migration_plans': [plan]}


def layer_map(kind):
    lo = ['actor', 'module', 'data', 'platform']
    layers = {'actor': ['act:op', 'acc:admin'], 'module': ['mod.conn', 'mod.core'], 'data': ['res:mail-old', 'res:mail-new'], 'platform': ['res:dns']}
    if kind == 'without res:dns':
        layers['platform'] = []
    if kind == 'seven layers':
        lo += ['edge', 'cloud', 'vendor']
    return {'format': 'aiaeao.cube.vp07-layer-map/1', 'layer_order': lo, 'layers': layers}


def case(o):
    out = {'id': o['id'], 'context': context(), 'plan_id': 'pm-ls', 'layers': layer_map(o['layers']) if o['layers'] else None,
           'steps': o['steps'], 'placement_predicates': o.get('placement_predicates'), 'granularity': ORACLE['granularity']}
    return out


out = {'format': 'aiaeao.cube.vp12-vectors/1', 'oracle_sha256': hashlib.sha256((HERE/'oracles/independent_l01_l14.json').read_bytes()).hexdigest(),
       'cases': [case(o) for o in ORACLE['cases']]}
(HERE/'fixtures/l01_l14_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print(len(out['cases']), 'cases')
