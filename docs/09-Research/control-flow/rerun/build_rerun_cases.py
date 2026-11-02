#!/usr/bin/env python3
"""MILE-008 TASK-052: MILE-002 cases BPMN-01, BPMN-02, BPMN-03 again, now as binding-context/9 through the local MCP adapter.

Contexts come from the P1.13 vectors (KF-01, KF-06, KF-07, KF-08, KF-09) and, for the cross-instance regression, from
the P1.12 vector K-17 lifted to /9 without control flow (Q-10: /9 is a strict superset of /8). Provenance from the original
MILE-002 case files. Expectations are fixed here, before the adapter accepts /9 and before any run: from the independent
P1.13 oracle (d33f22c), the P1.12 oracle (8297b82), or — for the other-branch control — by hand from TB-1. Synthetic.
The LIB part (exclusivity, synchronisation) is not a cube_validate call; its expectations are the preregistered CF cases.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[3]
ORIG = REPO/'docs/09-Research/grammar-sampling/cases'
KF = {c['id']: c for c in json.loads((REPO/'P1/control-flow-profile-v1/fixtures/kf01_kf09_materialized.json').read_text('utf-8'))['cases']}
K = {c['id']: c for c in json.loads((REPO/'P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases']}
ORACLE = {c['id']: c for c in json.loads((REPO/'P1/control-flow-profile-v1/oracles/independent_kf01_kf09.json').read_text('utf-8'))['cases']}
SPEC_REF = 'cube:P1/control-flow-profile-v1/P1_13_ACCEPTANCE_SPEC.md'


def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def from_kf(kid, text=None):
    v = KF[kid]
    o = ORACLE[kid]
    return v['input_text'] if text is None else text, copy.deepcopy(v['context']), (o['expected_overall'], o['required_codes'])


k17 = copy.deepcopy(K['K-17']['context']); k17['format'] = 'aiaeao.cube.binding-context/9'
OTHER = KF['KF-01']['input_text'].replace('bpmn:approve-manual', 'bpmn:approve-auto')
RUNS = [
    ('BPMN-01-routed-v9', 'BPMN-01-routed', 'KF-01', *from_kf('KF-01'),
     'Deklariertes XOR mit Reihenfolge und Default; i1/tok-route steht am XOR und wird an approve-manual geleitet, Ziel von f-manual: PASS (TB-1).'),
    ('BPMN-01-ctrl-other-branch-v9', 'BPMN-01-ctrl-other-branch', 'KF-01 (Aussage approve-auto)', OTHER, copy.deepcopy(KF['KF-01']['context']),
     ('PASS', []), 'Die Leitung an approve-auto ist für sich gültig (Ziel von f-auto, TB-1): PASS. Dass i1 damit zwei Pfade nahm, ist keine '
                   'Einzelaussage, sondern Sache der LIB-Spurprüfung (CF-12, D-4).'),
    ('BPMN-01-routed-to-ship-v9', 'BPMN-01-routed', 'KF-06', *from_kf('KF-06'),
     'Leitung an ship, das kein Ziel eines Ausgangs des XOR ist: FAIL (TB-1). Heute (Probe TASK-048) PASS.'),
    ('BPMN-01-token-position-v9', 'BPMN-01-routed', 'KF-09', *from_kf('KF-09'),
     'Token ohne at_gateway: Flussbindung nicht prüfbar, UNRESOLVED (TB-1), nicht FAIL.'),
    ('BPMN-02-onflow-undeclared-v9', 'BPMN-02-join-same-instance', 'KF-07', *from_kf('KF-07'),
     'Token auf f-ghost, einem Referenten, aber keinem deklarierten Fluss: FAIL (TB-2). Heute (Probe TASK-048) PASS.'),
    ('BPMN-02-join-same-instance-v8', 'BPMN-02-join-same-instance', 'KF-08', *from_kf('KF-08'),
     'Regressionsschutz: /8 ohne Kontrollfluss läuft unverändert über P1.12: PASS.'),
    ('BPMN-03-join-cross-instance-shared-v9', 'BPMN-03-join-cross-instance-shared', 'K-17 als /9', K['K-17']['input_text'], k17,
     ('FAIL', ['P1_INSTANCE_MISMATCH']), 'P1.12-Instanzprüfung gilt unter /9 unverändert (Q-10): FAIL wie K-17.'),
]

(HERE/'cases').mkdir(exist_ok=True)
for cid, orig_id, src, text, ctx, (status, codes), why in RUNS:
    o = json.loads((ORIG/f'{orig_id}.json').read_text('utf-8'))
    origin = copy.deepcopy(o['origin'])
    origin['authored_at'] = '2026-11-02'
    origin['profile_revision'] = f'P1.13/control-flow-profile-v1 ({ctx["format"].rsplit("-", 1)[-1]}), source {src}'
    origin['rule_refs'] = list(origin['rule_refs']) + [SPEC_REF]
    args = {'input_text': text, 'context': ctx}
    case = {'format': 'aiaeao.cube.research-case/2', 'case_id': cid, 'origin': origin, 'operation': 'cube_validate',
            'invocation_kind': 'local_mcp_stdio', 'arguments': args, 'arguments_sha256': digest(args),
            'bindings': {'context_format': ctx['format'], 'context_sha256': digest(ctx), 'qualification_profiles_sha256': digest(None)},
            'expected': {'domain_status': status, 'diagnostic_codes': list(codes), 'fixed_before_execution': True, 'rationale': why},
            'rerun_of': orig_id}
    (HERE/'cases'/f'{cid}.json').write_text(json.dumps(case, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(cid, status, codes)
