#!/usr/bin/env python3
"""TASK-036: MILE-002 cases ARC-03, DSM-03, BPMN-03 (plus BPMN-02 as control) again, now as binding-context/8.

Contexts come from the P1.12 vectors (K-01, K-02, K-04, K-05, K-17, K-18, K-19); provenance (matrix case, model,
source register, rule refs) from the original MILE-002 case files. Expectations are fixed here, before the
adapter accepts /8 and before any run, from the independent P1.12 oracle (8297b82). Synthetic; no client data.
Writes cases/*.json in the runner's research-case/2 format.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[3]
ORIG = REPO/'docs/09-Research/grammar-sampling/cases'
VEC = {c['id']: c for c in json.loads((REPO/'P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases']}
SPEC_REF = 'cube:P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md'


def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


RUNS = [
    ('ARC-03-absence-claim-v8', 'ARC-03-absence-claim', 'K-01', 'UNRESOLVED', ['P1_COVERAGE_UNDECLARED'],
     'Service-Sicht ohne Abdeckungserklärung für eingehende realizes von Transaction Processing: Die Abwesenheitsregel ist erklärt, aber nicht abgedeckt. Abwesenheit bleibt unbekannt, nicht null (CV-3, D-3). Früher nicht ausführbar.'),
    ('ARC-03-ctrl-full-view-v8', 'ARC-03-ctrl-full-view', 'K-02', 'PASS', [],
     'Vollsicht mit Erklärung „eingehende realizes von TP vollständig erhoben“; die Regel Billing → TP ist abgedeckt. P1 prüft Erklärung und Abdeckung, nicht den Inhalt der Regel (PR-2): PASS.'),
    ('DSM-03-empty-known-v8', 'DSM-03-empty-known', 'K-04', 'PASS', [],
     'Paar (printer, parser) als erhoben erklärt; die Abwesenheitsregel für genau dieses Paar ist abgedeckt: PASS. Die Auswertung „geprüft leer“ liefert der LIB-Eintrag. Früher nicht ausführbar.'),
    ('DSM-03-unknown-v8', 'DSM-03-hidden', 'K-05', 'UNRESOLVED', ['P1_COVERAGE_UNDECLARED'],
     'Nur das Paar (printer, parser) ist erklärt; die Regel validator → printer liegt außerhalb: unbekannt, nicht geprüft leer (CV-2).'),
    ('BPMN-03-join-cross-instance-shared-v8', 'BPMN-03-join-cross-instance-shared', 'K-17', 'FAIL', ['P1_INSTANCE_MISMATCH'],
     'Gemeinsamer Scope, aber jetzt typisierte Instanzbindung (i1, i2) und joins verlangt gleiche Instanz: FAIL. Die Baseline (TASK-030) gab PASS, weil die Instanz nur im Namen steckte (G-08).'),
    ('BPMN-03-join-cross-instance-scoped-v8', 'BPMN-03-join-cross-instance-scoped', 'K-18', 'FAIL', ['P1_REFERENT_MISMATCH', 'P1_SCOPE_CONFLICT'],
     'Instanz als Scope, unverändert als /8: dieselben Befunde wie in der Baseline (IN-5).'),
    ('BPMN-02-join-same-instance-v8', 'BPMN-02-join-same-instance', 'K-19', 'PASS', [],
     'Kontrolle: joins innerhalb von i1, beide Endpunkte mit instance_ref i1: PASS.'),
]

(HERE/'cases').mkdir(exist_ok=True)
for cid, orig_id, kid, status, codes, why in RUNS:
    o = json.loads((ORIG/f'{orig_id}.json').read_text('utf-8'))
    v = VEC[kid]
    assert (v['expected_overall'], sorted(v['required_codes'])) == (status, sorted(codes)), cid
    origin = copy.deepcopy(o['origin'])
    origin['authored_at'] = '2026-11-02'
    origin['profile_revision'] = 'P1.12/coverage-instance-profile-v1 (binding-context/8), vector ' + kid
    origin['rule_refs'] = list(origin['rule_refs']) + [SPEC_REF]
    args = {'input_text': v['input_text'], 'context': copy.deepcopy(v['context'])}
    case = {'format': 'aiaeao.cube.research-case/2', 'case_id': cid, 'origin': origin, 'operation': 'cube_validate',
            'invocation_kind': 'local_mcp_stdio', 'arguments': args, 'arguments_sha256': digest(args),
            'bindings': {'context_format': args['context']['format'], 'context_sha256': digest(args['context']),
                         'qualification_profiles_sha256': digest(None)},
            'expected': {'domain_status': status, 'diagnostic_codes': codes, 'fixed_before_execution': True, 'rationale': why},
            'rerun_of': orig_id}
    (HERE/'cases'/f'{cid}.json').write_text(json.dumps(case, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(cid, status, codes)
