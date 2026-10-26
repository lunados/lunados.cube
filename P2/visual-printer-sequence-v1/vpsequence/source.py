"""VP-08 sequence source (SS-1…SS-6): validation of `aiaeao.cube.vp08-sequence-source/1`."""
from __future__ import annotations

from .common import (PROFILE, TRIGGER_KINDS, MESSAGE_KINDS, FRAGMENTS, MAX_DEPTH, LIMITS, Printer, VP01Error, VP08Error, need, keys,
                     clean, stable_id, scoped_ref)

FORMAT = 'aiaeao.cube.vp08-sequence-source/1'
REQUIRED = ('format', 'profile', 'reference_version', 'source_id', 'title', 'participants', 'triggers', 'declaration_status')
OPTIONAL = ('subtitle', 'method_contracts')
MSG_REQUIRED = ('id', 'kind', 'from', 'to', 'label', 'declaration_ref')


def _count(seq):
    n = 0
    for it in seq if isinstance(seq, list) else []:
        if isinstance(it, dict) and 'fragment' in it:
            for o in it.get('operands', []) if isinstance(it.get('operands'), list) else []:
                n += _count(o.get('sequence') if isinstance(o, dict) else None)
        else:
            n += 1
    return n


def validate_source(src):
    need(isinstance(src, dict) and src.get('format') == FORMAT, 'VP08_SOURCE_INVALID', 'input is not an '+FORMAT+' document')
    keys(src, REQUIRED, OPTIONAL, 'VP08_SOURCE_INVALID', 'sequence source')
    need(src['profile'] == PROFILE and src['reference_version'] == 'v9.4', 'VP08_SOURCE_INVALID', 'wrong profile or reference_version')
    need(src['declaration_status'] == 'declared_unverified', 'VP08_SOURCE_INVALID', 'declaration_status must be declared_unverified')
    need(clean(src['source_id'], 100) and clean(src['title'], 78), 'VP08_SOURCE_INVALID', 'source_id <= 100, title <= 78 clean text')
    if 'subtitle' in src:
        need(clean(src['subtitle'], 95), 'VP08_SOURCE_INVALID', 'subtitle must be clean text <= 95')
    parts, trigs = src['participants'], src['triggers']
    # SS-5 hard limits first
    need(isinstance(parts, list) and 1 <= len(parts) <= LIMITS['participants'], 'VP08_SOURCE_INVALID',
         f'participants must be an array of 1..{LIMITS["participants"]} (SS-5)')
    need(isinstance(trigs, list) and 1 <= len(trigs) <= LIMITS['triggers'], 'VP08_SOURCE_INVALID',
         f'triggers must be an array of 1..{LIMITS["triggers"]} (SS-5)')
    total = 0
    for t in trigs:
        n = _count(t.get('sequence') if isinstance(t, dict) else None)
        need(n <= LIMITS['messages_per_trigger'], 'VP08_SOURCE_INVALID', f'a trigger declares {n} messages > {LIMITS["messages_per_trigger"]} (SS-5)')
        total += n
    need(total <= LIMITS['messages'], 'VP08_SOURCE_INVALID', f'{total} messages > {LIMITS["messages"]} (SS-5)')
    base = Printer()
    pmap = {}
    for p in parts:
        need(isinstance(p, dict), 'VP08_SOURCE_INVALID', 'participant must be an object')
        keys(p, ('id', 'anchor_id', 'form_id', 'label'), ('semantic_ref',), 'VP08_SOURCE_INVALID', 'participant')
        try:
            base._node(p)
        except VP01Error as e:
            raise VP08Error('VP08_SOURCE_INVALID', 'participant '+repr(p.get('id'))+': '+str(e)) from e
        need(clean(p['label'], 60), 'VP08_SOURCE_INVALID', 'participant label must be clean text <= 60')
        need(p['id'] not in pmap, 'VP08_SOURCE_INVALID', 'duplicate participant '+p['id'])
        pmap[p['id']] = p
    known = None
    if 'method_contracts' in src:
        mc = src['method_contracts']
        need(isinstance(mc, list) and len(mc) <= 500, 'VP08_SOURCE_INVALID', 'method_contracts must be an array of <= 500')
        known = set()
        for m in mc:
            keys(m, ('method_id',), (), 'VP08_SOURCE_INVALID', 'method contract')
            need(clean(m['method_id'], 100), 'VP08_SOURCE_INVALID', 'method_id must be clean text <= 100')
            known.add(m['method_id'])
    tmap = {}
    for t in trigs:
        need(isinstance(t, dict), 'VP08_SOURCE_INVALID', 'trigger must be an object')
        keys(t, ('id', 'kind', 'label', 'enters', 'declaration_ref', 'sequence'), ('use_case', 'returns'), 'VP08_SOURCE_INVALID', 'trigger')
        need(stable_id(t['id']) and t['id'] not in tmap, 'VP08_SOURCE_INVALID', 'trigger id must be a unique stable ID')
        need(t['kind'] in TRIGGER_KINDS, 'VP08_TRIGGER_INVALID', 'trigger '+t['id']+': kind '+repr(t['kind'])+' outside '+'|'.join(TRIGGER_KINDS))
        need(t['enters'] in pmap, 'VP08_TRIGGER_INVALID', 'trigger '+t['id']+' enters unknown participant '+repr(t['enters']))
        need(clean(t['label'], 60), 'VP08_SOURCE_INVALID', 'trigger label must be clean text <= 60')
        need(scoped_ref(t['declaration_ref']), 'VP08_SOURCE_INVALID', 'trigger declaration_ref must be scoped decl: or fixture:')
        if 'use_case' in t:
            need(stable_id(t['use_case']), 'VP08_SOURCE_INVALID', 'use_case must be a stable ID')
        if 'returns' in t:
            need(t['returns'] == 'expected', 'VP08_SOURCE_INVALID', 'returns must be "expected"')
        ids = set()
        _items(t['sequence'], pmap, ids, 0, t['id'])
        need(_count(t['sequence']) >= 1, 'VP08_SOURCE_INVALID', 'trigger '+t['id']+' declares no message')
        tmap[t['id']] = t
    return {'participants': pmap, 'triggers': tmap, 'methods': known}


def _items(seq, pmap, ids, depth, where):
    need(isinstance(seq, list) and seq, 'VP08_FRAGMENT_INVALID' if depth else 'VP08_SOURCE_INVALID',
         where+': sequence must be a nonempty array')
    for it in seq:
        need(isinstance(it, dict), 'VP08_SOURCE_INVALID', where+': sequence item must be an object')
        if 'fragment' in it:
            keys(it, ('fragment', 'id', 'operands'), (), 'VP08_FRAGMENT_INVALID', 'fragment')
            k = it['fragment']
            need(k in FRAGMENTS, 'VP08_FRAGMENT_INVALID', 'fragment kind must be alt|opt|loop, got '+repr(k))
            need(stable_id(it['id']) and it['id'] not in ids, 'VP08_SOURCE_INVALID', 'fragment id must be a unique stable ID')
            ids.add(it['id'])
            need(depth+1 <= MAX_DEPTH, 'VP08_FRAGMENT_INVALID', f'fragment {it["id"]} nests deeper than {MAX_DEPTH} (D-5)')
            ops = it['operands']
            need(isinstance(ops, list), 'VP08_FRAGMENT_INVALID', 'operands must be an array')
            if k == 'alt':
                need(len(ops) >= 2, 'VP08_FRAGMENT_INVALID', f'alt {it["id"]} needs at least two operands')
            else:
                need(len(ops) == 1, 'VP08_FRAGMENT_INVALID', f'{k} {it["id"]} takes exactly one operand')
            text_key = 'bound' if k == 'loop' else 'guard'
            for o in ops:
                keys(o, (text_key, 'sequence'), (), 'VP08_FRAGMENT_INVALID', f'{k} operand (needs {text_key})')
                need(clean(o[text_key], 60), 'VP08_FRAGMENT_INVALID', f'{text_key} must be declared clean text <= 60')
                _items(o['sequence'], pmap, ids, depth+1, it['id'])
            continue
        keys(it, MSG_REQUIRED, ('method_id',), 'VP08_SOURCE_INVALID', 'message')
        need(stable_id(it['id']) and it['id'] not in ids, 'VP08_SOURCE_INVALID', 'message id must be a unique stable ID: '+repr(it['id']))
        ids.add(it['id'])
        need(it['kind'] in MESSAGE_KINDS, 'VP08_SOURCE_INVALID', 'message kind must be call|return|async|self')
        for end in ('from', 'to'):
            need(it[end] in pmap, 'VP08_SEQUENCE_REFERENCE', f'message {it["id"]} {end} unknown participant {it[end]!r}')
        if it['kind'] == 'self':
            need(it['from'] == it['to'], 'VP08_SEQUENCE_REFERENCE', f'self message {it["id"]} must have from = to')
        else:
            need(it['from'] != it['to'], 'VP08_SEQUENCE_REFERENCE', f'message {it["id"]} from = to needs kind self')
        need(clean(it['label'], 120), 'VP08_SOURCE_INVALID', 'message label must be clean text <= 120')
        need(scoped_ref(it['declaration_ref']), 'VP08_SOURCE_INVALID', 'message declaration_ref must be scoped decl: or fixture: (<= 180)')
        if 'method_id' in it:
            need(clean(it['method_id'], 100), 'VP08_SOURCE_INVALID', 'method_id must be clean text <= 100')
