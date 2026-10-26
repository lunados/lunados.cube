#!/usr/bin/env python3
"""Build fixtures/golden_sequence.json (VP08-07, D-8 style): synthetic shop, no client data.

5 participants, 4 triggers (3 UI buttons, 1 schedule), one `alt` with a nested `loop`
(checkout), one sequence long enough to continue at standard (order export, 20 messages).
Expected values are declared by design, not computed here.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
MOD = 'form.module-block'


def m(i, kind, frm, to, label, **kw):
    d = {'id': i, 'kind': kind, 'from': frm, 'to': to, 'label': label, 'declaration_ref': f'fixture:vp08-golden/{i}'}
    d.update(kw)
    return d


PARTS = [{'id': 'customer', 'anchor_id': 'identity-anchors.actor', 'form_id': 'form.identity-chip', 'label': 'customer'},
         {'id': 'web', 'anchor_id': 'module-bodies.adapter', 'form_id': MOD, 'label': 'web shop UI'},
         {'id': 'orders', 'anchor_id': 'module-bodies.core', 'form_id': MOD, 'label': 'order service'},
         {'id': 'pay', 'anchor_id': 'module-bodies.third-party-dependency', 'form_id': MOD, 'label': 'payment provider'},
         {'id': 'mail', 'anchor_id': 'module-bodies.provider', 'form_id': MOD, 'label': 'mail service'}]
CHECKOUT = [
    m('c1', 'call', 'web', 'orders', 'create order from cart'),
    m('c2', 'self', 'orders', 'orders', 'reserve stock'),
    {'fragment': 'alt', 'id': 'f-pay', 'operands': [
        {'guard': 'payment accepted', 'sequence': [
            m('c3', 'call', 'orders', 'pay', 'charge card', method_id='pay.charge/v1'),
            m('c4', 'return', 'pay', 'orders', 'receipt'),
            {'fragment': 'loop', 'id': 'f-items', 'operands': [{'bound': 'for each ordered item', 'sequence': [
                m('c5', 'async', 'orders', 'mail', 'queue item confirmation')]}]}]},
        {'guard': 'payment declined', 'sequence': [
            m('c6', 'self', 'orders', 'orders', 'release stock')]}]},
    m('c7', 'return', 'orders', 'web', 'order status')]
CANCEL = [m('x1', 'call', 'web', 'orders', 'cancel order'),
          {'fragment': 'opt', 'id': 'f-refund', 'operands': [{'guard': 'already charged', 'sequence': [
              m('x2', 'call', 'orders', 'pay', 'refund', method_id='pay.refund/v1'),
              m('x3', 'return', 'pay', 'orders', 'refund receipt')]}]},
          m('x4', 'async', 'orders', 'mail', 'send cancellation'),
          m('x5', 'return', 'orders', 'web', 'cancelled')]
TRACK = [m('t1', 'call', 'web', 'orders', 'get order status'), m('t2', 'return', 'orders', 'web', 'status')]
EXPORT = []
for i in range(1, 11):
    EXPORT += [m(f'e{2*i-1:02d}', 'call', 'orders', 'mail', f'send reminder batch {i}'),
               m(f'e{2*i:02d}', 'return', 'mail', 'orders', f'batch {i} accepted')]
SOURCE = {'format': 'aiaeao.cube.vp08-sequence-source/1', 'profile': 'P2-VP-SEQUENCE/0.8.0', 'reference_version': 'v9.4',
          'source_id': 'golden-vp08', 'title': 'Acme shop · order flows', 'participants': PARTS,
          'triggers': [
              {'id': 'btn-checkout', 'kind': 'ui_button', 'label': 'Checkout', 'enters': 'web', 'use_case': 'uc-order',
               'declaration_ref': 'fixture:vp08-golden/btn-checkout', 'returns': 'expected', 'sequence': CHECKOUT},
              {'id': 'btn-cancel', 'kind': 'ui_button', 'label': 'Cancel order', 'enters': 'web', 'use_case': 'uc-order',
               'declaration_ref': 'fixture:vp08-golden/btn-cancel', 'sequence': CANCEL},
              {'id': 'btn-track', 'kind': 'ui_button', 'label': 'Track order', 'enters': 'web', 'use_case': 'uc-track',
               'declaration_ref': 'fixture:vp08-golden/btn-track', 'sequence': TRACK},
              {'id': 'sched-reminder', 'kind': 'schedule', 'label': 'Daily reminders', 'enters': 'orders', 'use_case': 'uc-remind',
               'declaration_ref': 'fixture:vp08-golden/sched-reminder', 'sequence': EXPORT}],
          'method_contracts': [{'method_id': 'pay.charge/v1'}, {'method_id': 'pay.refund/v1'}],
          'declaration_status': 'declared_unverified'}
EXPECTED = {
    'participants': 5, 'triggers': 4, 'ui_buttons': 3, 'messages': 34,
    'panels_trigger_standard': {'panels': 5, 'coverage': 'COMPLETE', 'units': 34, 'continued_trigger': 'sched-reminder', 'windows': 2},
    'checkout_numbering': {'c1': 1, 'c2': 2, 'c3': 3, 'c4': 4, 'c5': 5, 'c6': 6, 'c7': 7},
    'checkout_frames': {'f-pay': 'alt', 'f-items': 'loop'},
    'warnings': [{'code': 'VP08_SEQUENCE_CONTINUED', 'trigger_id': 'sched-reminder'}],
}


def main():
    out = {'format': 'aiaeao.cube.vp08-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic; no client data',
           'sequence_source': SOURCE, 'expected': EXPECTED}
    (HERE/'fixtures/golden_sequence.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden;', sum(1 for t in SOURCE['triggers']), 'triggers')


if __name__ == '__main__':
    main()
