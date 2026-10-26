#!/usr/bin/env python3
"""Materialise S-01..S-20 from VP08_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_s01_s20.json (transcribed before code).
All names are synthetic.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_s01_s20.json').read_text('utf-8'))
PROFILE = 'P2-VP-SEQUENCE/0.8.0'
MOD = 'form.module-block'


def part(i, anchor, label, form=MOD):
    return {'id': i, 'anchor_id': anchor, 'form_id': form, 'label': label}


PARTS = [part('a', 'identity-anchors.actor', 'customer', 'form.identity-chip'), part('b', 'module-bodies.adapter', 'web UI'),
         part('c', 'module-bodies.core', 'order service'), part('d', 'module-bodies.provider', 'mail service')]


def msg(i, kind, frm, to, label=None, **kw):
    m = {'id': i, 'kind': kind, 'from': frm, 'to': to, 'label': label or f'{kind} {i}', 'declaration_ref': f'fixture:vp08/{i}'}
    m.update(kw)
    return m


def frag(kind, i, *operands):
    return {'fragment': kind, 'id': i, 'operands': list(operands)}


def op(seq, guard=None, bound=None):
    o = {'sequence': seq}
    if guard is not None:
        o['guard'] = guard
    if bound is not None:
        o['bound'] = bound
    return o


def trig(i, seq, kind='ui_button', enters='a', **kw):
    t = {'id': i, 'kind': kind, 'label': i.replace('-', ' '), 'enters': enters, 'declaration_ref': f'fixture:vp08/{i}', 'sequence': seq}
    t.update(kw)
    return t


def source(triggers, participants=None, **kw):
    s = {'format': 'aiaeao.cube.vp08-sequence-source/1', 'profile': PROFILE, 'reference_version': 'v9.4', 'source_id': 'fixture-seq',
         'title': 'Fixture sequences', 'participants': copy.deepcopy(participants or PARTS), 'triggers': triggers,
         'declaration_status': 'declared_unverified'}
    s.update(kw)
    return s


def seq_case(src, trigger, granularity='standard', overflow='reject'):
    return ('sequence', {'source': src, 'trigger': trigger, 'granularity': granularity, 'overflow': overflow})


def pingpong(n):
    return [msg(f'm{i}', 'call' if i % 2 else 'return', 'a' if i % 2 else 'b', 'b' if i % 2 else 'a') for i in range(1, n+1)]


def build():
    v = {}
    v['S-01'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b'), msg('m2', 'return', 'b', 'a')])]), 'btn-1')
    p = copy.deepcopy(PARTS); p[1]['anchor_id'] = 'module-bodies.unknown'
    v['S-02'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b')])], p), 'btn-1')
    v['S-03'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'zz')])]), 'btn-1')
    v['S-04'] = seq_case(source([trig('btn-1', [msg('m1', 'self', 'a', 'b')])]), 'btn-1')
    v['S-05'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b')], kind='cron')]), 'btn-1')
    many = [part(f'p{i:02d}', 'module-bodies.core', f'module {i}') for i in range(1, 42)]
    v['S-06'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'p01', 'p02')], enters='p01')], many), 'btn-1')
    v['S-07'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b'), msg('m2', 'self', 'b', 'b'), msg('m3', 'async', 'b', 'c'),
                                                msg('m4', 'return', 'b', 'a')])]), 'btn-1')
    v['S-08'] = seq_case(source([trig('btn-1', [
        msg('m1', 'call', 'a', 'b'),
        frag('alt', 'f1', op([msg('m2', 'call', 'b', 'c'), msg('m3', 'return', 'c', 'b')], guard='accepted'),
             op([msg('m4', 'return', 'b', 'a')], guard='declined')),
        msg('m5', 'return', 'b', 'a')])]), 'btn-1')
    long_label = 'submit the completed order form together with the selected delivery option and voucher'
    long_label = (long_label+' code now')[:90]
    v['S-09'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b', long_label), msg('m2', 'return', 'b', 'a')])]), 'btn-1')
    v['S-10'] = seq_case(source([trig('btn-1', [msg('m1', 'return', 'b', 'a')])]), 'btn-1')
    v['S-11'] = seq_case(source([trig('btn-1', [msg('m1', 'call', 'a', 'b', method_id='x.unknown/v1')])],
                                method_contracts=[{'method_id': 'x.known/v1'}]), 'btn-1')
    v['S-12'] = seq_case(source([trig('btn-1', [frag('alt', 'f1', op([msg('m1', 'call', 'a', 'b')], guard='only'))])]), 'btn-1')
    v['S-13'] = seq_case(source([trig('btn-1', [
        msg('m1', 'call', 'a', 'b'),
        frag('loop', 'f1', op([msg('m2', 'call', 'b', 'c'), msg('m3', 'return', 'c', 'b')], bound='for each item')),
        msg('m4', 'return', 'b', 'a')])]), 'btn-1')
    v['S-14'] = seq_case(source([trig('btn-1', [
        frag('alt', 'f1',
             op([frag('opt', 'f2', op([frag('loop', 'f3', op([msg('m1', 'call', 'a', 'b')], bound='each'))], guard='inner'))], guard='x'),
             op([msg('m2', 'call', 'a', 'b')], guard='y'))])]), 'btn-1', 'detail')
    v['S-15'] = seq_case(source([trig('btn-1', [frag('opt', 'f1', op([msg('m1', 'call', 'a', 'b')]))])]), 'btn-1')
    v['S-16'] = seq_case(source([trig('btn-1', pingpong(20))]), 'btn-1', 'standard', 'reject')
    v['S-17'] = seq_case(source([trig('btn-1', pingpong(20))]), 'btn-1', 'standard', 'summarize')
    four = [trig('btn-checkout', [msg('m1', 'call', 'a', 'b'), msg('m2', 'call', 'b', 'c'), msg('m3', 'return', 'c', 'b'), msg('m4', 'return', 'b', 'a')]),
            trig('btn-cancel', [msg('m1', 'call', 'a', 'b'), msg('m2', 'async', 'b', 'c')]),
            trig('btn-track', [msg('m1', 'call', 'a', 'b'), msg('m2', 'return', 'b', 'a')]),
            trig('sched-reminder', [msg('m1', 'async', 'c', 'd')], kind='schedule', enters='c')]
    v['S-18'] = ('panels', {'source': source(copy.deepcopy(four)), 'partition': 'trigger', 'granularity': 'standard', 'overflow': 'reject'})
    v['S-19'] = ('panels', {'source': source(copy.deepcopy(four)), 'partition': 'trigger', 'granularity': 'standard', 'overflow': 'reject',
                            'tamper': 'drop_message'})
    v['S-20'] = v['S-13'][0], copy.deepcopy(v['S-13'][1])
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp08-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP08_ACCEPTANCE_SPEC.md §5 + oracles/independent_s01_s20.json', 'cases': cases}
    (HERE/'fixtures/s01_s20_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
