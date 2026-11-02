#!/usr/bin/env python3
"""MILE-007 TASK-044: write the synthetic inputs and the hand-derived expectations (A cases for lunados.lib,
S vectors for VP-10 0.11.0). Every expected value below is written out by hand from VP110_ACCEPTANCE_SPEC.md;
only input hashes are computed. Run once from the repo root; no client data."""
import copy, hashlib, json
from pathlib import Path

ROOT = Path.cwd()
HERE = ROOT/'docs/09-Research/statement-sets'
GS = ROOT/'docs/09-Research/grammar-sampling/cases'
IN = HERE/'inputs'
IN.mkdir(parents=True, exist_ok=True)


def cjson(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(o):
    return hashlib.sha256(cjson(o).encode('utf-8')).hexdigest()


def write(name, obj):
    (IN/name).write_text(json.dumps(obj, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    return name


def ctx_from(case, cid):
    c = copy.deepcopy(json.loads((GS/case).read_text('utf-8'))['arguments']['context'])
    c['format'] = 'aiaeao.cube.binding-context/8'
    c['context_id'] = cid
    return c


# --- contexts -------------------------------------------------------------------------------------------
dsm = ctx_from('DSM-01-cell-irfad.json', 'mile007-dsm')
dsm_cov = copy.deepcopy(dsm); dsm_cov['context_id'] = 'mile007-dsm-cov'
dsm_cov['coverage_declarations'] = [{'declaration_id': 'cv-pp', 'scope': 'pair', 'subject': 'm:printer', 'predicate_id': 'dependsOn',
                                     'object': 'm:parser', 'witness_ref': 'synthetic:dsm#printer-parser analysed, no dependency'}]
c4 = ctx_from('C4-02-source-writes.json', 'mile007-c4')
mon = copy.deepcopy(next(p for p in c4['predicate_contracts'] if p['predicate_id'] == 'uses.derived')); mon['predicate_id'] = 'monitors'
c4['predicate_contracts'].append(mon)
ops = copy.deepcopy(c4['referents'][0])
ops.update(ref='c4:team/ops', concept_id='Y:identity-anchor:actor', home='Y')
c4['referents'].append(ops)
c4_cov = copy.deepcopy(c4); c4_cov['context_id'] = 'mile007-c4-cov'
c4_cov['coverage_declarations'] = [{'declaration_id': 'cv-ad', 'scope': 'pair', 'subject': 'c4:shop/api', 'predicate_id': 'uses.derived',
                                    'object': 'c4:shop/db', 'witness_ref': 'synthetic:c4#api-db surveyed'}]
for n, c in (('ctx-dsm.json', dsm), ('ctx-dsm-cov.json', dsm_cov), ('ctx-c4.json', c4), ('ctx-c4-cov.json', c4_cov)):
    write(n, c)

# --- statement sets -------------------------------------------------------------------------------------
P, R, V, PR = 'm:parser', 'm:resolver', 'm:validator', 'm:printer'
API, DB, OC, OR, OPS = 'c4:shop/api', 'c4:shop/db', 'c4:shop/api/order-controller', 'c4:shop/api/order-repository', 'c4:team/ops'


def st(i, s, p, o, label=None):
    x = {'statement_id': i, 'subject': s, 'predicate_id': p, 'object': o}
    if label:
        x['label'] = label
    return x


def sset(sid, ctx, refs, stmts):
    return {'format': 'aiaeao.cube.statement-set/1', 'set_id': sid, 'context_id': ctx['context_id'], 'referents': refs,
            'statements': stmts, 'witness_ref': 'synthetic:mile007#'+sid}


DSM_ST = [st('s-rp', R, 'dependsOn', P), st('s-vr', V, 'dependsOn', R), st('s-pv', PR, 'dependsOn', V), st('s-fb', P, 'dependsOn', V)]
C4_ST = [st('m-1', API, 'contains', OC), st('m-2', API, 'contains', OR),
         st('s-1', OC, 'uses', DB, 'Writes orders to'), st('s-2', OR, 'uses', DB, 'Reads orders from'), st('s-3', OC, 'uses', OR, 'Uses')]
C4_REFS = [API, DB, OC, OR]
SETS = {
    'set-dsm.json': sset('dsm-modules', dsm, [P, R, V, PR], DSM_ST),
    'set-c4.json': sset('c4-components', c4, C4_REFS, C4_ST),
    'set-c4-s4.json': sset('c4-components-s4', c4, C4_REFS, C4_ST+[st('s-4', API, 'uses', DB, 'Stores data in')]),
    'set-c4-s5.json': sset('c4-components-s5', c4, C4_REFS, C4_ST+[st('s-5', API, 'monitors', DB)]),
    'set-c4-two-parents.json': sset('c4-two-parents', c4, C4_REFS, C4_ST+[st('m-3', DB, 'contains', OR)]),
    'set-dsm-ref-unknown.json': sset('dsm-ref-unknown', dsm, [P, R, V, PR], DSM_ST+[st('s-lx', 'm:lexer', 'dependsOn', P)]),
    'set-dsm-pred-invalid.json': sset('dsm-pred-invalid', dsm, [P, R, V, PR, 't:core'], DSM_ST+[st('s-tc', 't:core', 'dependsOn', P)]),
    'set-dsm-dup.json': sset('dsm-dup', dsm, [P, R, V, PR], DSM_ST+[st('s-rp', PR, 'dependsOn', P)]),
    'set-dsm-outside.json': sset('dsm-outside', dsm, [P, R, V], DSM_ST[:2]+[st('s-pp', PR, 'dependsOn', P)]),
    'set-c4-mixed.json': sset('c4-mixed', c4, [API, OPS], []),
}
for n, s in SETS.items():
    write(n, s)
H = {n: sha(s) for n, s in SETS.items()}

# --- A cases: project.aggregate-relations/v1 (hand-derived, Q-4…Q-8) ---------------------------------------
PAR = {'source_predicate': 'uses', 'derived_predicate': 'uses.derived', 'membership_predicate': 'contains'}
D1 = {'statement_id': 'd-1', 'subject': API, 'predicate_id': 'uses.derived', 'object': DB, 'origin': 'derived',
      'derived_from': ['s-1', 's-2'], 'label': 'Writes orders to', 'labels_dropped': 1}
S4 = {'statement_id': 's-4', 'subject': API, 'predicate_id': 'uses', 'object': DB, 'origin': 'declared', 'label': 'Stores data in'}


def res(set_name, strategy, statements, internal, suppressed, loss, params=PAR):
    return {'schema': 'aiaeao.projection-result/v1', 'method_id': 'project.aggregate-relations/v1',
            'parameters': {**params, 'strategy': strategy}, 'input_set_sha256': H[set_name], 'referents': [API, DB],
            'statements': statements, 'internal': internal, 'suppressed': suppressed, 'loss': loss,
            'status': 'declared_unverified', 'runtime_authority': 'not-evaluated'}


def loss(sources, passed, derived, merged, internal, suppressed, dropped):
    return {'sources': sources, 'passed_through': passed, 'derived': derived, 'merged': merged, 'internal': internal,
            'suppressed': suppressed, 'labels_dropped': dropped}


L_BASE = loss(3, 0, 1, 2, 1, 0, 1)
A = [
    {'case_id': 'A-01', 'question': 'C4-02 mit all: welche Container-Beziehung, aus welchen Quellen?', 'set': 'set-c4.json', 'strategy': 'all',
     'expected': res('set-c4.json', 'all', [D1], ['s-3'], [], L_BASE)},
    {'case_id': 'A-02', 'question': 'C4-02 mit unless_same ohne deklarierte Container-Beziehung', 'set': 'set-c4.json', 'strategy': 'unless_same',
     'expected': res('set-c4.json', 'unless_same', [D1], ['s-3'], [], L_BASE)},
    {'case_id': 'A-03', 'question': 'C4-02 mit unless_any ohne deklarierte Container-Beziehung', 'set': 'set-c4.json', 'strategy': 'unless_any',
     'expected': res('set-c4.json', 'unless_any', [D1], ['s-3'], [], L_BASE)},
    {'case_id': 'A-04', 'question': 'all neben deklarierter API uses DB (s-4)', 'set': 'set-c4-s4.json', 'strategy': 'all',
     'expected': res('set-c4-s4.json', 'all', [S4, D1], ['s-3'], [], loss(4, 1, 1, 2, 1, 0, 1))},
    {'case_id': 'A-05', 'question': 'unless_same neben deklarierter API uses DB (s-4)', 'set': 'set-c4-s4.json', 'strategy': 'unless_same',
     'expected': res('set-c4-s4.json', 'unless_same', [S4], ['s-3'],
                     [{'statement_id': 's-1', 'suppressed_by': 's-4'}, {'statement_id': 's-2', 'suppressed_by': 's-4'}], loss(4, 1, 0, 0, 1, 2, 0))},
    {'case_id': 'A-06', 'question': 'unless_same neben API monitors DB (anderes Prädikat, s-5)', 'set': 'set-c4-s5.json', 'strategy': 'unless_same',
     'expected': res('set-c4-s5.json', 'unless_same', [D1], ['s-3'], [], L_BASE)},
    {'case_id': 'A-07', 'question': 'unless_any neben API monitors DB (s-5)', 'set': 'set-c4-s5.json', 'strategy': 'unless_any',
     'expected': res('set-c4-s5.json', 'unless_any', [], ['s-3'],
                     [{'statement_id': 's-1', 'suppressed_by': 's-5'}, {'statement_id': 's-2', 'suppressed_by': 's-5'}], loss(3, 0, 0, 0, 1, 2, 0))},
    {'case_id': 'A-08', 'question': 'Strategie fehlt', 'set': 'set-c4.json', 'strategy': None,
     'expected': {'error': 'PROJECTION_PARAMETER_INVALID'}},
    {'case_id': 'A-09', 'question': 'Order Repository hat zwei Eltern (m-2, m-3)', 'set': 'set-c4-two-parents.json', 'strategy': 'all',
     'expected': {'error': 'PROJECTION_PARENT_AMBIGUOUS'}},
    {'case_id': 'A-10', 'question': 'derived_predicate contains erlaubt Boundary → Boundary nicht', 'set': 'set-c4.json', 'strategy': 'all',
     'parameters': {**PAR, 'derived_predicate': 'contains'}, 'expected': {'error': 'PROJECTION_PREDICATE_INVALID'}},
]
for a in A:
    a.setdefault('parameters', PAR)
    a['context'] = 'ctx-c4.json'

# --- S vectors: VP-10 0.11.0 (hand-derived, DR-1…DR-6, §5) ---------------------------------------------------
DSM_AX = [P, R, V, PR]
DSM_MARKED = {f'{R}|{P}': 's-rp', f'{V}|{R}': 's-vr', f'{PR}|{V}': 's-pv', f'{P}|{V}': 's-fb'}
DSM_OFF = [f'{r}|{c}' for r in DSM_AX for c in DSM_AX if r != c]
NO_PLAN = ['p0', 'p1', 'phase', 'Phase', 'migration', 'Migration', 'plan ', 'Plan ', 'd-x*']


def legend(strategy, l):
    return (f"aggregation {strategy}: sources {l['sources']} → derived {l['derived']}; passed through {l['passed_through']}; "
            f"internal {l['internal']}; suppressed {l['suppressed']}; labels dropped {l['labels_dropped']}")


S = [
    {'id': 'S-01', 'context': 'ctx-dsm.json', 'set': 'set-dsm.json', 'predicate': 'dependsOn',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'title': 'dsm-modules · dependsOn', 'rows': DSM_AX, 'cols': DSM_AX,
                  'marked': DSM_MARKED, 'checked': {}, 'unknown': sorted(set(DSM_OFF)-set(DSM_MARKED)), 'warnings': ['VP10_COVERAGE_NONE'],
                  'text': {f'{R}|{P}': ['s-rp · dependsOn']}, 'svg_must_not_contain': NO_PLAN}},
    {'id': 'S-02', 'context': 'ctx-dsm-cov.json', 'set': 'set-dsm.json', 'predicate': 'dependsOn',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'rows': DSM_AX, 'cols': DSM_AX, 'marked': DSM_MARKED, 'checked': {f'{PR}|{P}': 'pair'},
                  'unknown': sorted(set(DSM_OFF)-set(DSM_MARKED)-{f'{PR}|{P}'}), 'warnings': []}},
    {'id': 'S-03', 'context': 'ctx-dsm.json', 'set': 'set-dsm.json', 'predicate': 'dependsOn', 'axis_order': DSM_AX,
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'rows': DSM_AX, 'cols': DSM_AX, 'marked': DSM_MARKED, 'feedback_cells': [f'{P}|{V}'],
                  'warnings': ['VP10_COVERAGE_NONE'], 'text': {f'{P}|{V}': ['s-fb · dependsOn', 'feedback']}}},
    {'id': 'S-04', 'context': 'ctx-c4.json', 'set': 'set-c4.json', 'projection': 'A-01',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'title': 'c4-components · uses.derived', 'rows': [API, DB], 'cols': [API, DB],
                  'marked': {f'{API}|{DB}': 'd-1'}, 'checked': {}, 'unknown': [f'{DB}|{API}'], 'warnings': ['VP10_COVERAGE_NONE'],
                  'text': {f'{API}|{DB}': ['d-1 · uses.derived · derived · 2 sources']}, 'loss': L_BASE,
                  'legend_line': legend('all', L_BASE), 'ledger_derived': {'d-1': ['s-1', 's-2']}, 'svg_must_not_contain': NO_PLAN}},
    {'id': 'S-05', 'context': 'ctx-c4.json', 'set': 'set-c4-s4.json', 'projection': 'A-04',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'rows': [API, DB], 'cols': [API, DB], 'marked': {f'{API}|{DB}': 's-4, d-1'},
                  'unknown': [f'{DB}|{API}'], 'warnings': ['VP10_COVERAGE_NONE'],
                  'text': {f'{API}|{DB}': ['s-4 · uses', 'd-1 · uses.derived · derived · 2 sources']},
                  'legend_line': legend('all', loss(4, 1, 1, 2, 1, 0, 1))}},
    {'id': 'S-06', 'context': 'ctx-c4.json', 'set': 'set-c4-s5.json', 'projection': 'A-07',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'rows': [API, DB], 'cols': [API, DB], 'marked': {}, 'unknown': [f'{API}|{DB}', f'{DB}|{API}'],
                  'warnings': ['VP10_COVERAGE_NONE', 'VP10_PREDICATE_EMPTY'], 'legend_line': legend('unless_any', loss(3, 0, 0, 0, 1, 2, 0)),
                  'ledger_suppressed': {'s-1': 's-5', 's-2': 's-5'}}},
    {'id': 'S-07', 'context': 'ctx-dsm.json', 'set': 'set-dsm-ref-unknown.json', 'predicate': 'dependsOn', 'expected': {'error': 'VP10_STATEMENT_REF_UNKNOWN'}},
    {'id': 'S-08', 'context': 'ctx-dsm.json', 'set': 'set-dsm-pred-invalid.json', 'predicate': 'dependsOn',
     'expected': {'error': 'VP10_STATEMENT_PREDICATE_INVALID'}},
    {'id': 'S-09', 'context': 'ctx-dsm.json', 'set': 'set-dsm-dup.json', 'predicate': 'dependsOn', 'expected': {'error': 'VP10_STATEMENT_SET_INVALID'}},
    {'id': 'S-10', 'context': 'ctx-dsm.json', 'set': 'set-dsm-outside.json', 'predicate': 'dependsOn', 'expected': {'error': 'VP10_STATEMENT_SET_INVALID'}},
    {'id': 'S-11', 'context': 'ctx-c4.json', 'set': 'set-c4-mixed.json', 'predicate': 'uses', 'expected': {'error': 'VP10_PAIR_INVALID'}},
    {'id': 'S-12', 'context': 'ctx-c4.json', 'set': 'set-c4-s4.json', 'projection': 'A-01', 'expected': {'error': 'VP10_PROJECTION_INVALID'}},
    {'id': 'S-13', 'context': 'ctx-c4-cov.json', 'set': 'set-c4.json', 'projection': 'A-01',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'marked': {f'{API}|{DB}': 'd-1'}, 'checked': {}, 'unknown': [f'{DB}|{API}'],
                  'warnings': ['VP10_COVERAGE_NOT_PROJECTED']}},
    {'id': 'S-14', 'context': 'ctx-dsm.json', 'set': 'set-dsm.json', 'predicate': 'related',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'marked': {}, 'checked': {}, 'unknown': sorted(DSM_OFF),
                  'warnings': ['VP10_COVERAGE_NONE', 'VP10_PREDICATE_EMPTY']}},
    {'id': 'S-15', 'context': 'ctx-c4.json', 'set': 'set-c4.json', 'projection': 'A-01', 'locale': 'de',
     'expected': {'profile': 'P2-VP-CELLS/0.11.0', 'text': {f'{API}|{DB}': ['d-1 · uses.derived · abgeleitet · 2 Quellen']},
                  'legend_line': 'Verdichtung all: Quellen 3 → abgeleitet 1; durchgereicht 0; intern 1; unterdrückt 0; Beschreibungen verworfen 1'}},
    {'id': 'S-16', 'context': 'ctx-c4.json', 'set': 'set-c4.json', 'projection': 'A-01', 'via': 'G6 cube_plan_source + cube_plan_views + cube_plan_check',
     'expected': {'svg_equals_cli_of': 'S-04', 'check': 'PASS'}},
]

common = {'fixed_at': '2026-11-02', 'fixed_before_code': True, 'spec': 'P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md (Q-1–Q-10 resolved, 594563c)',
          'canonical_json': 'json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")), UTF-8, SHA-256',
          'inputs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(IN.glob('*.json'))}}
(HERE/'CHECK-CASES.json').write_text(json.dumps({'format': 'mile007.check-cases/1', 'task': 'TASK-044', **common,
    'layer': 'LIB project.aggregate-relations/v1; error codes are working titles, TASK-045 may rename them, not the disposition',
    'cases': A}, ensure_ascii=False, indent=1)+'\n', 'utf-8')
(ROOT/'P2/visual-printer-cells-v1/oracles/independent_s01_s16.json').write_text(json.dumps({'format': 'aiaeao.p2.vp110-oracle/1', **common,
    'inputs_dir': 'docs/09-Research/statement-sets/inputs', 'projections': 'A cases in docs/09-Research/statement-sets/CHECK-CASES.json',
    'legend_line_rule': 'one line, exact; en and de as given', 'cases': S}, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('inputs', len(common['inputs']), 'A', len(A), 'S', len(S))
