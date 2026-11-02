"""MILE-008 TASK-048: erzeugt CHECK-CASES.json und CHECK-CASES.md (formatneutrale Prüffälle für Kontrollfluss und
Spurkonformität, Erwartung heute und mit Profil) deterministisch.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/09-Research/control-flow/build_check_cases.py
Alle Erwartungen sind hier von Hand geschrieben, vor Spezifikation und Code. Diagnosecodes und value-Bezeichner sind
Arbeitstitel; TASK-049 darf sie umbenennen, Status und Schicht nicht. Synthetisch, keine Kundendaten.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path('docs/09-Research/control-flow')
GS = Path('docs/09-Research/grammar-sampling')
MODEL = {'path': str(GS/'models/bpmn-order.json'), 'sha256': hashlib.sha256((GS/'models/bpmn-order.json').read_bytes()).hexdigest()}

# --- Kontrollfluss nach bpmn-order.json; Flussnamen für den Weg check → xor und approve → split ergänzt (model_completion) ------
XOR = {'id': 'bpmn:xor', 'type': 'exclusive', 'incoming': ['bpmn:f-checked'],
       'outgoing': [{'flow': 'bpmn:f-manual', 'to': 'bpmn:approve-manual', 'order': 1, 'condition': 'amount > 1000'},
                    {'flow': 'bpmn:f-auto', 'to': 'bpmn:approve-auto', 'default': True}]}
MERGE = {'id': 'bpmn:merge', 'type': 'exclusive', 'incoming': ['bpmn:f-manual-done', 'bpmn:f-auto-done'],
         'outgoing': [{'flow': 'bpmn:f-approved', 'to': 'bpmn:split'}]}
SPLIT = {'id': 'bpmn:split', 'type': 'parallel', 'incoming': ['bpmn:f-approved'],
         'outgoing': [{'flow': 'bpmn:f-stock', 'to': 'bpmn:check-stock'}, {'flow': 'bpmn:f-credit', 'to': 'bpmn:check-credit'}]}
JOIN = {'id': 'bpmn:join', 'type': 'parallel', 'incoming': ['bpmn:f-stock-done', 'bpmn:f-credit-done'],
        'outgoing': [{'flow': 'bpmn:f-ship', 'to': 'bpmn:ship'}]}
BASE = [XOR, MERGE, SPLIT, JOIN]
COMPLETION = 'Flüsse bpmn:f-checked, bpmn:f-manual-done, bpmn:f-auto-done, bpmn:f-approved, bpmn:f-ship und das Merge-Gateway ergänzen die Modellnotiz („both lead to split“, „join leads to ship“) um Namen'


def cf(*mods):
    m = copy.deepcopy(BASE)
    for f in mods:
        f(m)
    return m


def g(m, gid):
    return next(x for x in m if x['id'] == gid)


def route(tok, inst, to, conditions=None):
    t = {'token': tok, 'instance': inst, 'at': 'bpmn:xor', 'routed_to': to}
    if conditions is not None:
        t['conditions'] = conditions
    return t


def on(tok, inst, flow):
    return {'token': tok, 'instance': inst, 'on_flow': flow}


def cov_route(tok):
    return {'scope': 'referent_relation_direction', 'referent': tok, 'predicate': 'routedTo', 'direction': 'outgoing',
            'source': 'Leitentscheidungen dieses Tokens vollständig aufgezeichnet'}


def cov_flow(flow, inst):
    return {'scope': 'referent_relation_direction', 'referent': flow, 'predicate': 'onFlow', 'direction': 'incoming', 'instance_ref': inst,
            'source': f'Token auf {flow} für {inst} vollständig aufgezeichnet'}


def case(cid, story, matrix, question, control_flow, trace, coverage, claim, today, profile, why, variant=None):
    c = {'case_id': cid, 'story': story, 'matrix_case': matrix, 'model': MODEL, 'question': question, 'control_flow': control_flow,
         'trace': trace, 'coverage': coverage, 'claim': claim, 'expected_today': today, 'expected_with_profile': profile, 'rationale': why}
    if variant:
        c['variant_of_model'] = variant
    return c


NE = lambda ref, extra='': {'kind': 'NE', 'reason': 'kein Gateway-Typ, keine Flussbindung, keine Bedingungsreihenfolge im Kontext' + extra,  # noqa: E731
                            'mile002_case': ref}
T_RUN = lambda ref, st: {'kind': 'P1', 'status': st, 'diagnostic_codes': [], 'mile002_case': ref, 'verified_by': 'Baseline-Lauf TASK-048'}  # noqa: E731
T_PROBE = lambda st: {'kind': 'P1', 'status': st, 'diagnostic_codes': [], 'verified_by': 'Probe heute (P1.12, /8) in TASK-048'}  # noqa: E731
P1 = lambda st, codes=(): {'layer': 'P1', 'status': st, 'diagnostic_codes': list(codes)}  # noqa: E731
LIB = lambda st, val, **kw: {'layer': 'LIB', 'status': st, 'value': val, **kw}  # noqa: E731

I1, I2 = 'bpmn:i1', 'bpmn:i2'
TOK = 'bpmn:i1/tok-route'
R_MANUAL = route(TOK, I1, 'bpmn:approve-manual')
STOCK1, CREDIT1, SHIP1 = on('bpmn:i1/tok-stock', I1, 'bpmn:f-stock-done'), on('bpmn:i1/tok-credit', I1, 'bpmn:f-credit-done'), on('bpmn:i1/tok-ship', I1, 'bpmn:f-ship')
CREDIT2, SHIP2 = on('bpmn:i2/tok-credit', I2, 'bpmn:f-credit-done'), on('bpmn:i2/tok-ship', I2, 'bpmn:f-ship')
JOIN_COV = lambda inst: [cov_flow(f, inst) for f in ('bpmn:f-stock-done', 'bpmn:f-credit-done', 'bpmn:f-ship')]  # noqa: E731
SPLIT_COV = [cov_flow(f, I1) for f in ('bpmn:f-approved', 'bpmn:f-stock', 'bpmn:f-credit')]

CASES = [
    # --- P1: Deklaration und Flussbindung ---------------------------------------------------------------------------
    case('CF-01', 'US-026', 'BPMN-01', 'Ist das deklarierte Modell wohlgeformt, und leitet i1/tok-route an ein Ziel eines ausgehenden Flusses?',
         cf(), [R_MANUAL], [], {'check': 'declaration', 'statement': 'routedTo(bpmn:i1/tok-route, bpmn:approve-manual)'},
         T_RUN('BPMN-01-routed', 'PASS'), P1('PASS'), 'Gültiges XOR (Reihenfolge 1 + Default), AND-Split und -Join; Ziel approve-manual ist Ziel von f-manual.'),
    case('CF-02', 'US-026', 'BPMN-01', 'Ein exklusives Gateway mit zwei Default-Flüssen?',
         cf(lambda m: g(m, 'bpmn:xor')['outgoing'][0].update(default=True)), [], [], {'check': 'declaration'},
         NE('BPMN-01-exclusivity'), P1('FAIL', ['P1_CONTROL_FLOW_INVALID']), 'Höchstens ein Default je exklusivem Gateway (§10.6.2).', variant='zwei Defaults'),
    case('CF-03', 'US-026', 'BPMN-01', 'Zwei bedingte Flüsse mit derselben Reihenfolge?',
         cf(lambda m: g(m, 'bpmn:xor')['outgoing'].insert(1, {'flow': 'bpmn:f-review', 'to': 'bpmn:approve-review', 'order': 1, 'condition': 'amount > 500'})),
         [], [], {'check': 'declaration'}, NE('BPMN-01-exclusivity'), P1('FAIL', ['P1_CONTROL_FLOW_INVALID']),
         'Die Bedingungsreihenfolge muss eindeutig sein (§13.4.2: erste wahre entscheidet).', variant='doppelte Reihenfolge'),
    case('CF-04', 'US-026', 'BPMN-02', 'Ein paralleles Gateway mit Default-Fluss?',
         cf(lambda m: g(m, 'bpmn:split')['outgoing'][0].update(default=True)), [], [], {'check': 'declaration'},
         NE('BPMN-02-sync-condition'), P1('FAIL', ['P1_CONTROL_FLOW_INVALID']), 'Default und Bedingungen gibt es nur am exklusiven Gateway.', variant='Default am AND'),
    case('CF-05', 'US-026', 'BPMN-01', 'Ein inklusives Gateway?',
         cf(lambda m: g(m, 'bpmn:xor').update(type='inclusive')), [], [], {'check': 'declaration'},
         NE('BPMN-01-exclusivity'), P1('UNRESOLVED', ['P1_CONTROL_FLOW_UNSUPPORTED']),
         'Außerhalb des Profilumfangs (D-2): nicht beurteilt, nicht FAIL.', variant='inklusives Gateway'),
    case('CF-06', 'US-026', 'BPMN-01', 'Leitet i1/tok-route an Ship, das kein Ziel des XOR ist?',
         cf(), [route(TOK, I1, 'bpmn:ship')], [], {'check': 'declaration', 'statement': 'routedTo(bpmn:i1/tok-route, bpmn:ship)'},
         T_PROBE('PASS'), P1('FAIL', ['P1_FLOW_UNDECLARED']), 'Heute besteht jede typgerechte routedTo-Aussage; mit Profil nur an Ziele ausgehender Flüsse.',
         variant='Leitung an Ship'),
    case('CF-07', 'US-026', 'BPMN-02', 'Liegt i1/tok-stock auf einem nicht deklarierten Fluss?',
         cf(), [on('bpmn:i1/tok-stock', I1, 'bpmn:f-ghost')], [], {'check': 'declaration', 'statement': 'onFlow(bpmn:i1/tok-stock, bpmn:f-ghost)'},
         T_PROBE('PASS'), P1('FAIL', ['P1_FLOW_UNDECLARED']), 'f-ghost ist Referent, aber kein deklarierter Fluss.', variant='unbekannter Fluss'),
    case('CF-08', 'US-026', 'BPMN-02', 'Bleibt binding-context/8 ohne Kontrollfluss unverändert?',
         None, [STOCK1, CREDIT1], [], {'check': 'regression', 'statement': 'joins(bpmn:i1/tok-stock, bpmn:i1/tok-credit), /8'},
         T_RUN('BPMN-02-join-same-instance', 'PASS'), P1('PASS'), 'Regressionsschutz: /8 wird von P1.12 unverändert geprüft (CI-03).'),
    case('CF-09', 'US-026', 'BPMN-01', 'routedTo von einem Token ohne deklarierte Position am Gateway?',
         cf(), [{'token': TOK, 'instance': I1, 'routed_to': 'bpmn:approve-manual'}], [],
         {'check': 'declaration', 'statement': 'routedTo(bpmn:i1/tok-route, bpmn:approve-manual), Token ohne at'},
         T_RUN('BPMN-01-routed', 'PASS'), P1('UNRESOLVED', ['P1_TOKEN_POSITION_UNDECLARED']),
         'Ohne Position ist die Flussbindung nicht prüfbar: unentschieden wie P1_INSTANCE_UNDECLARED, nicht FAIL.', variant='Token ohne Position'),
    # --- LIB: exklusives Gateway ------------------------------------------------------------------------------------
    case('CF-11', 'US-027', 'BPMN-01', 'Nahm i1 am XOR genau einen Pfad?', cf(), [R_MANUAL], [cov_route(TOK)],
         {'check': 'exclusive', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-exclusivity', '; Teilersatz über P1.12-Zählregel CC-11'),
         LIB('PASS', 'exclusive_one_path', paths=['bpmn:approve-manual']), 'Eine Aktivierung, eine Leitentscheidung (§13.4.2).'),
    case('CF-12', 'US-027', 'BPMN-01', 'Nahm i1 am XOR zwei Pfade?', cf(), [R_MANUAL, route(TOK, I1, 'bpmn:approve-auto')], [cov_route(TOK)],
         {'check': 'exclusive', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-ctrl-other-branch', '; Teilersatz CC-12'),
         LIB('FAIL', 'exclusive_two_paths', paths=['bpmn:approve-auto', 'bpmn:approve-manual']), 'Zwei Pfade für eine Aktivierung (§10.6.2).',
         variant='zweite Leitentscheidung'),
    case('CF-13', 'US-027', 'BPMN-01', 'Erreichte i1/tok-route das XOR, ohne geleitet zu werden?', cf(),
         [{'token': TOK, 'instance': I1, 'at': 'bpmn:xor'}], [cov_route(TOK)], {'check': 'exclusive', 'gateway': 'bpmn:xor', 'instance': I1},
         NE('BPMN-01-exclusivity'), LIB('FAIL', 'exclusive_no_path', paths=[]), 'Aktivierung ohne Leitung bei vollständiger Spur (§13.4.2: Exception).',
         variant='keine Leitung'),
    case('CF-14', 'US-027', 'BPMN-01', 'Nahm i1 genau einen Pfad, wenn die Spur nicht als vollständig erklärt ist?', cf(), [R_MANUAL], [],
         {'check': 'exclusive', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-exclusivity', '; Teilersatz CC-13'),
         LIB('UNRESOLVED', 'coverage_undeclared'), 'Ohne Abdeckung keine Aussage über weitere Leitungen (P1.12 D-3).'),
    case('CF-15', 'US-027', 'BPMN-01', 'Nahm i1 die erste wahre Bedingung?', cf(), [route(TOK, I1, 'bpmn:approve-manual', {'bpmn:f-manual': True})],
         [cov_route(TOK)], {'check': 'condition_order', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-exclusivity'),
         LIB('PASS', 'condition_first_true', taken='bpmn:f-manual'), 'amount 1500 > 1000: f-manual wahr und genommen.'),
    case('CF-16', 'US-027', 'BPMN-01', 'Nahm i1 den Default, als keine Bedingung wahr war?', cf(),
         [route(TOK, I1, 'bpmn:approve-auto', {'bpmn:f-manual': False})], [cov_route(TOK)], {'check': 'condition_order', 'gateway': 'bpmn:xor', 'instance': I1},
         NE('BPMN-01-exclusivity'), LIB('PASS', 'default_without_true', taken='bpmn:f-auto'), 'Default genau dann, wenn keine Bedingung wahr ist.',
         variant='Betrag unter Schwelle'),
    case('CF-17', 'US-027', 'BPMN-01', 'Nahm i1 den Default, obwohl f-manual wahr war?', cf(),
         [route(TOK, I1, 'bpmn:approve-auto', {'bpmn:f-manual': True})], [cov_route(TOK)], {'check': 'condition_order', 'gateway': 'bpmn:xor', 'instance': I1},
         NE('BPMN-01-exclusivity'), LIB('FAIL', 'default_with_true_condition', taken='bpmn:f-auto', first_true='bpmn:f-manual'),
         'Default trotz wahrer Bedingung (§13.4.2).', variant='Default trotz wahrer Bedingung'),
    case('CF-18', 'US-027', 'BPMN-01', 'Nahm i1 die richtige Bedingung, wenn keine Bedingungsergebnisse aufgezeichnet sind?', cf(), [R_MANUAL],
         [cov_route(TOK)], {'check': 'condition_order', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-exclusivity'),
         LIB('UNRESOLVED', 'conditions_unrecorded'), 'Der Cube wertet keine Bedingungen aus (D-5).'),
    case('CF-19', 'US-027', 'BPMN-01', 'Nahm i1 die zweite wahre Bedingung statt der ersten?',
         cf(lambda m: g(m, 'bpmn:xor')['outgoing'].insert(1, {'flow': 'bpmn:f-review', 'to': 'bpmn:approve-review', 'order': 2, 'condition': 'amount > 500'})),
         [route(TOK, I1, 'bpmn:approve-review', {'bpmn:f-manual': True, 'bpmn:f-review': True})], [cov_route(TOK)],
         {'check': 'condition_order', 'gateway': 'bpmn:xor', 'instance': I1}, NE('BPMN-01-exclusivity'),
         LIB('FAIL', 'not_first_true', taken='bpmn:f-review', first_true='bpmn:f-manual'), 'Bedingungen in Reihenfolge, die erste wahre entscheidet.',
         variant='dritter Fluss f-review'),
    # --- LIB: paralleler Join ----------------------------------------------------------------------------------------
    case('CF-21', 'US-027', 'BPMN-02', 'Durfte Ship für i1 starten?', cf(), [STOCK1, CREDIT1, SHIP1], JOIN_COV(I1),
         {'check': 'join', 'gateway': 'bpmn:join', 'instance': I1}, NE('BPMN-02-sync-condition', '; Teilersatz CC-14'),
         LIB('PASS', 'join_complete', activations=1, missing=[], foreign=[], excess={}), 'Ein Token je Eingang derselben Instanz (§13.4.1).'),
    case('CF-22', 'US-027', 'BPMN-02', 'Startete Ship für i2 ohne Lagerprüfung?', cf(), [CREDIT2, SHIP2], JOIN_COV(I2),
         {'check': 'join', 'gateway': 'bpmn:join', 'instance': I2}, NE('BPMN-02-sync-condition', '; Teilersatz CC-15'),
         LIB('FAIL', 'join_incomplete', activations=1, missing=['bpmn:f-stock-done'], foreign=[], excess={}), 'Aktivierung ohne Token auf f-stock-done.',
         variant='Ship in i2 gestartet'),
    case('CF-23', 'US-027', 'BPMN-02', 'Warum wartet i2?', cf(), [CREDIT2], JOIN_COV(I2), {'check': 'join', 'gateway': 'bpmn:join', 'instance': I2},
         NE('BPMN-02-sync-condition'), LIB('PASS', 'join_waiting', activations=0, missing=['bpmn:f-stock-done'], foreign=[], excess={}),
         'Nicht aktiviert, fehlender Eingang benannt: kein Verstoß, sondern die Antwort auf „warum wartet sie?“.'),
    case('CF-24', 'US-027', 'BPMN-02', 'Wartet i2, wenn die Spur nicht als vollständig erklärt ist?', cf(), [CREDIT2], [],
         {'check': 'join', 'gateway': 'bpmn:join', 'instance': I2}, NE('BPMN-02-sync-condition', '; Teilersatz CC-16'),
         LIB('UNRESOLVED', 'coverage_undeclared'), 'Ohne Abdeckung von Ein- und Ausgängen keine Aussage.'),
    case('CF-25', 'US-027', 'BPMN-03', 'Startete Ship für i1 mit dem Kreditergebnis von i2?', cf(), [STOCK1, CREDIT2, SHIP1], JOIN_COV(I1),
         {'check': 'join', 'gateway': 'bpmn:join', 'instance': I1}, NE('BPMN-03-join-cross-instance-shared'),
         LIB('FAIL', 'join_incomplete', activations=1, missing=['bpmn:f-credit-done'], foreign=['bpmn:i2/tok-credit'], excess={}),
         'Ein Token einer fremden Instanz zählt nicht (G-08).', variant='fremder Token'),
    case('CF-26', 'US-027', 'BPMN-02', 'Bleibt in i1 ein überzähliger Lager-Token liegen?', cf(),
         [STOCK1, on('bpmn:i1/tok-stock-2', I1, 'bpmn:f-stock-done'), CREDIT1, SHIP1], JOIN_COV(I1),
         {'check': 'join', 'gateway': 'bpmn:join', 'instance': I1}, NE('BPMN-02-sync-condition'),
         LIB('PASS', 'join_complete', activations=1, missing=[], foreign=[], excess={'bpmn:f-stock-done': 1}),
         'Überschuss bleibt liegen (§13.4.1) und wird gezählt, nicht als FAIL gewertet (D-6).', variant='zweiter Lager-Token'),
    # --- LIB: paralleler Split, exklusives Merge -------------------------------------------------------------------
    case('CF-27', 'US-027', 'BPMN-02', 'Erzeugte der Split für i1 je Ausgang einen Token?', cf(),
         [on('bpmn:i1/tok-approved', I1, 'bpmn:f-approved'), on('bpmn:i1/tok-s', I1, 'bpmn:f-stock'), on('bpmn:i1/tok-c', I1, 'bpmn:f-credit')], SPLIT_COV,
         {'check': 'split', 'gateway': 'bpmn:split', 'instance': I1}, NE('BPMN-02-sync-condition'),
         LIB('PASS', 'split_complete', activations=1, missing=[]), 'Ein Token je Ausgang je Aktivierung (§13.4.1).'),
    case('CF-28', 'US-027', 'BPMN-02', 'Fehlt nach dem Split für i1 der Kredit-Zweig?', cf(),
         [on('bpmn:i1/tok-approved', I1, 'bpmn:f-approved'), on('bpmn:i1/tok-s', I1, 'bpmn:f-stock')], SPLIT_COV,
         {'check': 'split', 'gateway': 'bpmn:split', 'instance': I1}, NE('BPMN-02-sync-condition'),
         LIB('FAIL', 'split_incomplete', activations=1, missing=['bpmn:f-credit']), 'Kein Token auf f-credit bei vollständiger Spur.',
         variant='Kredit-Zweig fehlt'),
    case('CF-29', 'US-027', 'BPMN-01', 'Reicht das Merge den Token von approve-manual einmal weiter?', cf(),
         [on('bpmn:i1/tok-md', I1, 'bpmn:f-manual-done'), on('bpmn:i1/tok-approved', I1, 'bpmn:f-approved')],
         [cov_flow(f, I1) for f in ('bpmn:f-manual-done', 'bpmn:f-auto-done', 'bpmn:f-approved')],
         {'check': 'merge', 'gateway': 'bpmn:merge', 'instance': I1}, NE('BPMN-01-exclusivity'),
         LIB('PASS', 'merge_pass_through', incoming=1, outgoing=1), 'Exklusives Merge synchronisiert nicht: ein Token hinein, einer hinaus (WCP-5).'),
]

doc = {'format': 'mile008.check-cases/1', 'task': 'TASK-048', 'fixed_at': '2026-11-02', 'fixed_before_spec': True,
       'decisions': 'MILE-008 D-1–D-8 (460592a)', 'model_completion': COMPLETION,
       'layers': {'P1': 'Deklaration (P1.13, binding-context/9): Wohlgeformtheit des Kontrollflusses, Flussbindung der Spur-Aussagen',
                  'LIB': 'analyze.trace-conformance/v1: Spur je Instanz gegen das Modell (exklusiv, Bedingungsreihenfolge, Join, Split, Merge)'},
       'status_rule': {'violation_proven': 'FAIL', 'coverage_or_conditions_missing': 'UNRESOLVED (nie FAIL)', 'excess_tokens': 'gezählt, kein FAIL',
                       'outside_profile': 'UNRESOLVED P1_CONTROL_FLOW_UNSUPPORTED'},
       'naming': 'Diagnosecodes und value-Bezeichner sind Arbeitstitel; TASK-049 darf sie umbenennen, Status und Schicht nicht.',
       'baseline_cases': ['BPMN-01-routed', 'BPMN-01-ctrl-other-branch', 'BPMN-01-exclusivity', 'BPMN-02-join-same-instance', 'BPMN-02-sync-condition',
                          'BPMN-03-join-cross-instance-shared'],
       'cases': CASES}
(HERE/'CHECK-CASES.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1)+'\n', 'utf-8')


def fmt_today(t):
    if t['kind'] == 'NE':
        return 'NE'
    return f"P1 {t['status']}"


def fmt_prof(p):
    if p['layer'] == 'P1':
        return f"**P1 {p['status']}" + (' · '+', '.join(p['diagnostic_codes']) if p['diagnostic_codes'] else '') + '**'
    return f"**LIB {p['status']} · {p['value']}**"


rows = '\n'.join(f"| {c['case_id']} | {c['matrix_case']} | {c['question']} | {fmt_today(c['expected_today'])} | {fmt_prof(c['expected_with_profile'])} |" for c in CASES)
RUN = [c['case_id'] for c in CASES if c['expected_today']['kind'] != 'NE']
n_p1 = sum(c['expected_with_profile']['layer'] == 'P1' for c in CASES)
md = f'''# MILE-008-A — Prüffälle (TASK-048)

Stand: 2026-11-02 · Maschinenlesbar: [CHECK-CASES.json](CHECK-CASES.json), erzeugt mit [build_check_cases.py](build_check_cases.py) (deterministisch) · **festgelegt vor Spezifikation und Code** · Entscheidungen: [MILE-008 D-1–D-8](../../02-Milestones/MILE-008-control-flow.md)

{len(CASES)} formatneutrale Prüffälle aus BPMN-01, BPMN-02 und BPMN-03 ([Modell](../grammar-sampling/models/bpmn-order.json)). Jeder Fall nennt den deklarierten Kontrollfluss, die Spur (Token mit Instanz, Position, Leitung, Fluss, aufgezeichnete Bedingungsergebnisse), die Abdeckung der Spur (P1.12), die Erwartung **heute** und die Erwartung **mit Profil**. Sie sind die Orakel-Grundlage für TASK-049, TASK-050 und TASK-051.

**Schichten (D-3, D-4):** *P1* ({n_p1} Fälle) prüft die Deklaration und die Flussbindung einzelner Spur-Aussagen. *LIB* ({len(CASES)-n_p1} Fälle) prüft die Spur je Instanz gegen das Modell. **Statusregel (D-5, D-6):** belegter Verstoß → FAIL; fehlende Abdeckung oder fehlende Bedingungsergebnisse → UNRESOLVED, nie FAIL; Überschuss wird gezählt. Diagnosecodes und value-Bezeichner sind Arbeitstitel.

**Modellergänzung:** {COMPLETION}. Varianten weichen bewusst vom Modell ab und sind im JSON als `variant_of_model` gekennzeichnet.

| Fall | Matrix | Frage | Heute | Mit Profil |
|---|---|---|---|---|
{rows}

**Abdeckung:** Deklaration 9 (davon 1 Regressionsschutz), exklusiv 4, Bedingungsreihenfolge 5, Join 6, Split 2, Merge 1; je Prüfart mindestens ein PASS und ein FAIL, bei exklusiv, Bedingung und Join zusätzlich UNRESOLVED.

**Heute:** {sum(c['expected_today']['kind'] == 'NE' for c in CASES)} Fälle sind nicht ausführbar (NE). Teilersatz gibt es über die P1.12-Zählregeln aus MILE-005 (CC-11–CC-16), aber ohne Gateway-Typ, Flussbindung und Bedingungen. Die {len(RUN)} heute ausführbaren Fälle ({', '.join(RUN)}) bestehen als Einzelaussagen mit PASS, auch die falsche Leitung an Ship und der unbekannte Fluss — das ist die Lücke. Bestätigt durch den Baseline-Lauf und eine Probe mit dem unveränderten P1.12-Adapter.
'''
(HERE/'CHECK-CASES.md').write_text(md, 'utf-8')
print(len(CASES), 'cases')
