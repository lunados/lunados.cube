#!/usr/bin/env python3
"""Write the independent VP-11 oracle (TASK-054, before any printer code): oracles/independent_i01_i34.json.

The expected frames, blocks, rows, verdict lines, model lines, warnings, error codes and violation marks are written by
hand from VP11_ACCEPTANCE_SPEC.md (§3, §3.1, §6, §9) and the LIB results; the helpers below only spell the fixed
texts, the state of every row is chosen per case. Run from the lunados.cube root.
"""
import json
from pathlib import Path

OUT = Path.cwd()/'P2/visual-printer-instances-v1/oracles/independent_i01_i34.json'
T = {'en': {'act': 'activation', 'order': 'order', 'default': 'default', 'taken': 'taken', 'not_taken': 'not taken', 'arrived': 'arrived',
            'missing': 'missing', 'token': 'token', 'no_token': 'no token', 'foreign': 'token of instance {i} present · not part ({t})',
            'in': 'in', 'xs': 'exclusive split', 'xm': 'exclusive merge', 'ps': 'parallel split', 'pj': 'parallel join',
            'not_drawn': 'not drawn', 'nc': 'not checked'},
     'de': {'act': 'Aktivierung', 'order': 'Reihenfolge', 'default': 'Default', 'taken': 'genommen', 'not_taken': 'nicht genommen',
            'arrived': 'angekommen', 'missing': 'fehlt', 'token': 'Token', 'no_token': 'kein Token',
            'foreign': 'Token aus Instanz {i} vorhanden · nicht Teil ({t})', 'in': 'ein', 'xs': 'exklusiver Split', 'xm': 'exklusiver Merge',
            'ps': 'paralleler Split', 'pj': 'paralleler Join', 'not_drawn': 'nicht gezeichnet', 'nc': 'nicht geprüft'}}
B = 'bpmn:'


def mx(flow, target, how, L='en'):                # exclusive outgoing flow as in the model field
    t = T[L]
    return f"{B}{flow} → {B}{target} · {t['default'] if how == 'default' else t['order'] + ' ' + str(how)}"


def x(flow, target, how, state, L='en'):          # exclusive split row; how = order number or 'default'
    return f"{mx(flow, target, how, L)} · {T[L][state]}"


def act(tok, L='en'):
    return f"{T[L]['act']} {B}{tok}"


def jin(flow, state, toks=(), foreign=(), L='en'):  # join input row; foreign = [(instance, token)]
    t = T[L]
    s = f"{B}{flow} · {t[state]}" + (f" · {', '.join(B + k for k in toks)}" if toks else '')
    return s + ''.join(' · ' + t['foreign'].format(i=B + i, t=B + k) for i, k in foreign)


def inrow(flow, toks=(), L='en'):                  # split/merge incoming row
    t = T[L]
    return f"{B}{flow} · " + (f"{t['token']} {', '.join(B + k for k in toks)}" if toks else t['no_token'])


def out(flow, target, toks=(), L='en'):            # outgoing row of join, split, merge
    t = T[L]
    return f"{B}{flow} → {B}{target} · " + (f"{t['token']} {', '.join(B + k for k in toks)}" if toks else t['no_token'])


def model(review=False, extra=(), L='en'):
    t = T[L]
    xor = [mx('f-manual', 'approve-manual', 1, L)] + ([mx('f-review', 'approve-review', 2, L)] if review else []) + [mx('f-auto', 'approve-auto', 'default', L)]
    return ([f"{B}xor · {t['xs']}", f"{t['in']} {B}f-checked", *xor,
             f"{B}merge · {t['xm']}", f"{t['in']} {B}f-manual-done, {B}f-auto-done", f"{B}f-approved → {B}split",
             f"{B}split · {t['ps']}", f"{t['in']} {B}f-approved", f"{B}f-stock → {B}check-stock", f"{B}f-credit → {B}check-credit",
             f"{B}join · {t['pj']}", f"{t['in']} {B}f-stock-done, {B}f-credit-done", f"{B}f-ship → {B}ship"] + list(extra))


def hdr(gw, role, L='en'):
    return f"{B}{gw} · {T[L][role]}"


NC = ['not checked']
C = []


def case(iid, frames, blocks, rows, verdicts, marks=0, warnings=(), review=False, model_extra=(), locale='en'):
    C.append({'id': iid, 'status': 'ok', 'locale': locale, 'frames': frames, 'blocks': blocks, 'rows': rows, 'verdicts': verdicts,
              'model': model(review, model_extra, locale), 'warnings': sorted(warnings), 'violation_marks': marks})


def err(iid, code):
    C.append({'id': iid, 'status': 'error', 'code': code})


XS = hdr('xor', 'xs'); PJ = hdr('join', 'pj'); PS = hdr('split', 'ps'); XM = hdr('merge', 'xm')
i1, i2 = 'bpmn:i1', 'bpmn:i2'
ROUTE = 'i1/tok-route'
UNDECL_R = 'undeclared bpmn:i1/tok-route routedTo outgoing bpmn:i1'

# I-01…I-09: exclusive split (CF-11…CF-19)
for iid, man, auto, verdict, marks in (
        ('I-01', 'taken', 'not_taken', 'exclusive: checked · one path', 0),
        ('I-02', 'taken', 'taken', 'exclusive: rule violation · more than one path for one activation · paths bpmn:approve-auto, bpmn:approve-manual', 1),
        ('I-03', 'not_taken', 'not_taken', 'exclusive: rule violation · no path', 1),
        ('I-04', 'taken', 'not_taken', f'exclusive: not checkable · coverage missing · {UNDECL_R}', 0),
        ('I-05', 'taken', 'not_taken', 'condition order: checked · first true condition taken · taken bpmn:f-manual', 0),
        ('I-06', 'not_taken', 'taken', 'condition order: checked · default without true condition · taken bpmn:f-auto', 0),
        ('I-07', 'not_taken', 'taken', 'condition order: rule violation · default although a condition was true · taken bpmn:f-auto · first true bpmn:f-manual', 1),
        ('I-08', 'taken', 'not_taken', 'condition order: not checkable · condition outcomes not recorded', 0)):
    case(iid, [i1], {i1: [XS]}, {f'{i1}|bpmn:xor': [act(ROUTE), x('f-manual', 'approve-manual', 1, man), x('f-auto', 'approve-auto', 'default', auto)]},
         {f'{i1}|bpmn:xor': [verdict]}, marks)
case('I-09', [i1], {i1: [XS]}, {f'{i1}|bpmn:xor': [act(ROUTE), x('f-manual', 'approve-manual', 1, 'not_taken'), x('f-review', 'approve-review', 2, 'taken'),
                                                  x('f-auto', 'approve-auto', 'default', 'not_taken')]},
     {f'{i1}|bpmn:xor': ['condition order: rule violation · not the first true condition · taken bpmn:f-review · first true bpmn:f-manual']}, 1, review=True)

# I-10…I-15: parallel join (CF-21…CF-26)
case('I-10', [i1], {i1: [PJ]}, {f'{i1}|bpmn:join': [jin('f-stock-done', 'arrived', ['i1/tok-stock']), jin('f-credit-done', 'arrived', ['i1/tok-credit']),
                                                   out('f-ship', 'ship', ['i1/tok-ship'])]},
     {f'{i1}|bpmn:join': ['join: checked · all inputs']})
case('I-11', [i2], {i2: [PJ]}, {f'{i2}|bpmn:join': [jin('f-stock-done', 'missing'), jin('f-credit-done', 'arrived', ['i2/tok-credit']),
                                                   out('f-ship', 'ship', ['i2/tok-ship'])]},
     {f'{i2}|bpmn:join': ['join: rule violation · continued without all inputs · missing bpmn:f-stock-done']}, 1)
WAIT_ROWS = [jin('f-stock-done', 'missing'), jin('f-credit-done', 'arrived', ['i2/tok-credit']), out('f-ship', 'ship')]
case('I-12', [i2], {i2: [PJ]}, {f'{i2}|bpmn:join': WAIT_ROWS}, {f'{i2}|bpmn:join': ['join: checked · waiting · missing bpmn:f-stock-done']})
case('I-13', [i2], {i2: [PJ]}, {f'{i2}|bpmn:join': WAIT_ROWS},
     {f'{i2}|bpmn:join': ['join: not checkable · coverage missing · undeclared bpmn:f-stock-done onFlow incoming bpmn:i2, '
                          'bpmn:f-credit-done onFlow incoming bpmn:i2, bpmn:f-ship onFlow incoming bpmn:i2']})
F25 = {f'{i1}|bpmn:join': [jin('f-stock-done', 'arrived', ['i1/tok-stock']), jin('f-credit-done', 'missing', foreign=[('i2', 'i2/tok-credit')]),
                          out('f-ship', 'ship', ['i1/tok-ship'])],
       f'{i2}|bpmn:join': [jin('f-stock-done', 'missing', foreign=[('i1', 'i1/tok-stock')]), jin('f-credit-done', 'arrived', ['i2/tok-credit']),
                          out('f-ship', 'ship')]}
case('I-14', [i1, i2], {i1: [PJ], i2: [PJ]}, F25,
     {f'{i1}|bpmn:join': ['join: rule violation · continued without all inputs · missing bpmn:f-credit-done · foreign bpmn:i2/tok-credit'],
      f'{i2}|bpmn:join': NC}, 1)
case('I-15', [i1], {i1: [PJ]}, {f'{i1}|bpmn:join': [jin('f-stock-done', 'arrived', ['i1/tok-stock', 'i1/tok-stock-2']),
                                                   jin('f-credit-done', 'arrived', ['i1/tok-credit']), out('f-ship', 'ship', ['i1/tok-ship'])]},
     {f'{i1}|bpmn:join': ['join: checked · all inputs · excess bpmn:f-stock-done 1']})

# I-16…I-18: parallel split and exclusive merge (CF-27…CF-29); f-approved touches merge and split (Q-7)
MERGE_AP = [inrow('f-manual-done'), inrow('f-auto-done'), out('f-approved', 'split', ['i1/tok-approved'])]
case('I-16', [i1], {i1: [XM, PS]}, {f'{i1}|bpmn:merge': MERGE_AP, f'{i1}|bpmn:split': [inrow('f-approved', ['i1/tok-approved']),
                                   out('f-stock', 'check-stock', ['i1/tok-s']), out('f-credit', 'check-credit', ['i1/tok-c'])]},
     {f'{i1}|bpmn:merge': NC, f'{i1}|bpmn:split': ['split: checked · all outputs']})
case('I-17', [i1], {i1: [XM, PS]}, {f'{i1}|bpmn:merge': MERGE_AP, f'{i1}|bpmn:split': [inrow('f-approved', ['i1/tok-approved']),
                                   out('f-stock', 'check-stock', ['i1/tok-s']), out('f-credit', 'check-credit')]},
     {f'{i1}|bpmn:merge': NC, f'{i1}|bpmn:split': ['split: rule violation · not all outputs · missing bpmn:f-credit']}, 1)
case('I-18', [i1], {i1: [XM, PS]}, {f'{i1}|bpmn:merge': [inrow('f-manual-done', ['i1/tok-md']), inrow('f-auto-done'), out('f-approved', 'split', ['i1/tok-approved'])],
                                    f'{i1}|bpmn:split': [inrow('f-approved', ['i1/tok-approved']), out('f-stock', 'check-stock'), out('f-credit', 'check-credit')]},
     {f'{i1}|bpmn:merge': ['merge: checked · passed through'], f'{i1}|bpmn:split': NC})

# I-19…I-21: no records (D-5): rows as with records, every verdict "not checked", no mark
case('I-19', [i1], {i1: [XS]}, {f'{i1}|bpmn:xor': [act(ROUTE), x('f-manual', 'approve-manual', 1, 'taken'), x('f-auto', 'approve-auto', 'default', 'taken')]},
     {f'{i1}|bpmn:xor': NC})
case('I-20', [i2], {i2: [PJ]}, {f'{i2}|bpmn:join': WAIT_ROWS}, {f'{i2}|bpmn:join': NC})
case('I-21', [i1, i2], {i1: [PJ], i2: [PJ]}, F25, {f'{i1}|bpmn:join': NC, f'{i2}|bpmn:join': NC})


# I-22 / I-34: BPMN-02 model, i1 complete, i2 waiting, six records
def big(iid, L):
    t = T[L]
    nc = [t['nc']]
    H = {k: hdr(g, k, L) for g, k in (('xor', 'xs'), ('merge', 'xm'), ('split', 'ps'), ('join', 'pj'))}
    V = {'en': ['exclusive: checked · one path', 'condition order: checked · default without true condition · taken bpmn:f-auto',
                'merge: checked · passed through', 'split: checked · all outputs', 'join: checked · all inputs · foreign bpmn:i2/tok-cd',
                'join: checked · waiting · missing bpmn:f-stock-done · foreign bpmn:i1/tok-cd, bpmn:i1/tok-sd'],
         'de': ['Exklusivität: geprüft · ein Pfad', 'Bedingungsreihenfolge: geprüft · Default ohne wahre Bedingung · genommen bpmn:f-auto',
                'Merge: geprüft · durchgereicht', 'Split: geprüft · alle Ausgänge', 'Join: geprüft · alle Eingänge · fremd bpmn:i2/tok-cd',
                'Join: geprüft · wartet · fehlt bpmn:f-stock-done · fremd bpmn:i1/tok-cd, bpmn:i1/tok-sd']}[L]
    rows = {f'{i1}|bpmn:xor': [act('i1/tok-route', L), x('f-manual', 'approve-manual', 1, 'not_taken', L), x('f-auto', 'approve-auto', 'default', 'taken', L)],
            f'{i1}|bpmn:merge': [inrow('f-manual-done', L=L), inrow('f-auto-done', ['i1/tok-ad'], L), out('f-approved', 'split', ['i1/tok-ap'], L)],
            f'{i1}|bpmn:split': [inrow('f-approved', ['i1/tok-ap'], L), out('f-stock', 'check-stock', ['i1/tok-s'], L), out('f-credit', 'check-credit', ['i1/tok-c'], L)],
            f'{i1}|bpmn:join': [jin('f-stock-done', 'arrived', ['i1/tok-sd'], L=L), jin('f-credit-done', 'arrived', ['i1/tok-cd'], L=L),
                                out('f-ship', 'ship', ['i1/tok-ship'], L)],
            f'{i2}|bpmn:xor': [act('i2/tok-route', L), x('f-manual', 'approve-manual', 1, 'taken', L), x('f-auto', 'approve-auto', 'default', 'not_taken', L)],
            f'{i2}|bpmn:merge': [inrow('f-manual-done', ['i2/tok-md'], L), inrow('f-auto-done', L=L), out('f-approved', 'split', ['i2/tok-ap'], L)],
            f'{i2}|bpmn:split': [inrow('f-approved', ['i2/tok-ap'], L), out('f-stock', 'check-stock', ['i2/tok-s'], L), out('f-credit', 'check-credit', ['i2/tok-c'], L)],
            f'{i2}|bpmn:join': [jin('f-stock-done', 'missing', foreign=[('i1', 'i1/tok-sd')], L=L), jin('f-credit-done', 'arrived', ['i2/tok-cd'], L=L),
                                out('f-ship', 'ship', L=L)]}
    verdicts = {f'{i1}|bpmn:xor': V[0:2], f'{i1}|bpmn:merge': [V[2]], f'{i1}|bpmn:split': [V[3]], f'{i1}|bpmn:join': [V[4]],
                f'{i2}|bpmn:xor': nc, f'{i2}|bpmn:merge': nc, f'{i2}|bpmn:split': nc, f'{i2}|bpmn:join': [V[5]]}
    allb = [H['xs'], H['xm'], H['ps'], H['pj']]
    case(iid, [i1, i2], {i1: allb, i2: allb}, rows, verdicts, locale=L)


big('I-22', 'en')

# I-23…I-30: errors (§6, check order §9)
for iid, code in (('I-23', 'VP11_ADAPTER_INPUT'), ('I-24', 'VP11_TRACE_INVALID'), ('I-25', 'VP11_TRACE_REF_UNKNOWN'),
                  ('I-26', 'VP11_TRACE_PREDICATE_INVALID'), ('I-27', 'VP11_RECORD_INVALID'), ('I-28', 'VP11_RECORD_MISMATCH'),
                  ('I-29', 'VP11_RECORD_DUPLICATE'), ('I-30', 'VP11_RECORD_INVALID')):
    err(iid, code)

# I-31…I-33: warnings
case('I-31', [i1, '-'], {i1: [PJ], '-': [PJ]},
     {f'{i1}|bpmn:join': [jin('f-stock-done', 'arrived', ['i1/tok-stock']), jin('f-credit-done', 'arrived', ['i1/tok-credit']), out('f-ship', 'ship', ['i1/tok-ship'])],
      '-|bpmn:join': [jin('f-stock-done', 'missing'), jin('f-credit-done', 'missing'), out('f-ship', 'ship', ['tok-loose'])]},
     {f'{i1}|bpmn:join': NC, '-|bpmn:join': NC}, warnings=['VP11_STATEMENT_NOT_DRAWN', 'VP11_INSTANCE_UNDECLARED'])
case('I-32', [i2], {i2: [PJ]}, {f'{i2}|bpmn:join': WAIT_ROWS}, {f'{i2}|bpmn:join': NC}, warnings=['VP11_GATEWAY_NOT_DRAWN'],
     model_extra=['bpmn:or · inclusive · not drawn'])
case('I-33', [], {}, {}, {}, warnings=['VP11_TRACE_EMPTY'])
big('I-34', 'de')

C.sort(key=lambda c: c['id'])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({'format': 'aiaeao.p2.vp11-oracle/1', 'profile': 'P2-VP-INSTANCES/0.12.0',
                           'written_before': 'any VP-11 printer code (TASK-054)', 'frame_titles': {'en': 'instance <ref>', 'de': 'Instanz <ref>',
                           'undeclared_en': 'instance undeclared', 'undeclared_de': 'Instanz nicht deklariert'},
                           'model_title': {'en': 'process model · no trace', 'de': 'Prozessmodell · keine Spur'},
                           'cases': C}, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print(len(C), 'oracle cases')
