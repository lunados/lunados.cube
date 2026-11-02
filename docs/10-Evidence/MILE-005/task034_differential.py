#!/usr/bin/env python3
"""TASK-034 differential check: analyze.population/v1 evaluator vs. independent oracle beyond the 16 cases.

  task034_differential.py --lib <lunados.lib>

Derives variants from CC-01…CC-16 (flipped direction, open bounds, instance restrictions removed or added,
one-sided absence, dropped coverage, doubled or empty statement sets) and requires identical results.
Also checks that malformed rules are refused. Writes nothing; prints a JSON summary.
"""
import argparse, copy, glob, importlib.util, json
from pathlib import Path


def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lib', required=True); a = ap.parse_args()
    root = Path(a.lib).expanduser()/'entries/analyze.population/v1'
    E, O = load(root/'evaluator/evaluate.py', 'ev'), load(root/'oracle/oracle.py', 'orc')
    base = [json.loads(Path(f).read_text('utf-8'))['call'] for f in sorted(glob.glob(str(root/'cases/CC*.json')))]
    R = lambda x: x['inputs']['rule']
    variants = []
    for c in base:
        k = R(c)['kind']; muts = [lambda x: None]
        if k == 'count':
            muts += [lambda x: R(x).update(direction='incoming'), lambda x: R(x).update(min=0), lambda x: R(x).pop('max', None),
                     lambda x: R(x).update(instance_ref='bpmn:i1')]
        if k == 'absence':
            muts += [lambda x: R(x).pop('subject', None) if 'object' in R(x) else None,
                     lambda x: R(x).pop('object', None) if 'subject' in R(x) else None, lambda x: x['inputs'].update(coverage=[])]
        if k == 'join_activation':
            muts += [lambda x: [d.pop('instance_ref', None) for d in x['inputs']['coverage']], lambda x: R(x).update(instance_ref='bpmn:i1'),
                     lambda x: R(x)['incoming_flows'][0].update(min=2), lambda x: x['inputs']['coverage'][:1] and x['inputs']['coverage'].pop()]
        muts += [lambda x: x['inputs'].update(statements=x['inputs']['statements']*2), lambda x: x['inputs'].update(statements=[])]
        for m in muts:
            v = copy.deepcopy(c); m(v); variants.append(v)
    diffs, values = [], {}
    for v in variants:
        e, o = E.evaluate(v), O.oracle(v)
        values[e['value']] = values.get(e['value'], 0) + 1
        if e != o:
            diffs.append({'rule': R(v), 'evaluator': e, 'oracle': o})
    refused = []
    for bad in ({'rule': {'rule_id': 'r', 'kind': 'ratio', 'predicate_id': 'p'}},
                {'rule': {'rule_id': 'r', 'kind': 'count', 'predicate_id': 'p', 'referent': 'a', 'direction': 'outgoing', 'min': 3, 'max': 1}},
                {'rule': {'rule_id': 'r', 'kind': 'absence', 'predicate_id': 'p'}}):
        try:
            E.evaluate({'schema': 'lunados.lib/call/v1', 'method_id': 'analyze.population/v1', 'inputs': bad}); refused.append(False)
        except ValueError:
            refused.append(True)
    out = {'variants': len(variants), 'differences': len(diffs), 'values': values, 'malformed_refused': f'{sum(refused)}/{len(refused)}',
           'all_ok': not diffs and all(refused), 'diffs': diffs}
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    raise SystemExit(0 if out['all_ok'] else 1)


if __name__ == '__main__':
    main()
