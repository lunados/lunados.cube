"""MILE-013 TASK-074: G5 wire calls for core 0.9.1-proof (VP-07.7, Workers Paid CPU limit).

R8 = every R6 call (HO and OL vectors, unchanged bytes), the two R5 calls that ended with
G5_CORE_UNAVAILABLE under the free CPU budget (P-K07-flow, P-K08-sequence), and five
VP-07.7 calls on the synthetic plan of P2 tests/test_vp077.py.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import r5_calls
import r6_calls

REPO = Path(__file__).resolve().parents[3]
HEAVY = ('P-K07-flow', 'P-K08-sequence')
P077 = 'P2-VP-MIGRATION/0.7.7'
P076 = 'P2-VP-MIGRATION/0.7.6'
HOST = {'D-01', 'P-OL-07', 'P-K07-flow', 'P77-01', 'P77-02', 'P77-04'}
run_chain = r5_calls.run_chain


def _vp077():
    spec = importlib.util.spec_from_file_location('vp077_cases', REPO/'P2/visual-printer-migration-v1/tests/test_vp077.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def calls():
    t = _vp077()
    ctx = t.context()
    x_ctx = t.context()
    ref = next(r for r in x_ctx['referents'] if r['ref'] == 's:grant')
    ref.update(concept_id='X:endpoint:admission', home='X')
    x_ctx['predicate_contracts'][0]['object_concept_ids'].append('X:endpoint:admission')
    statements = {'format': 'aiaeao.cube.statement-set/2', 'set_id': 'set-077', 'context_id': ctx['context_id'],
                  'referents': ['s:core', 's:grant'],
                  'statements': [{'statement_id': 'st-1', 'subject': 's:core', 'predicate_id': 'uses', 'object': 's:grant',
                                  'origin': 'declared'}]}
    src = r5_calls.source
    out = [c for c in r6_calls.calls()]
    out += [c for c in r5_calls.calls() if c['id'] in HEAVY]
    out += [
        r5_calls.views_chain('P77-01', src(ctx, 'pm-077', 'vpmigration', profile=P077, origin_lines=True),
                             {'view': 'cube.flow', 'granularity': 'detail', 'partition': 'subject'}),
        r5_calls.views_chain('P77-02', src(ctx, 'pm-077', 'vpmigration', profile=P077),
                             {'view': 'cube.phases', 'granularity': 'detail', 'partition': 'subject'}),
        r5_calls.views_chain('P77-03', src(ctx, None, 'vpmigration', profile=P077, origin_lines=True, statements=statements),
                             {'view': 'cube.flow', 'granularity': 'standard', 'partition': 'subject'}),
        r5_calls.chain('P77-04', 'P', [src(ctx, 'pm-077', 'vpmigration', profile=P076, origin_lines=True)]),
        r5_calls.chain('P77-05', 'P', [src(x_ctx, 'pm-077', 'vpmigration', profile=P077, origin_lines=True)]),
    ]
    for c in out:
        c['live'] = 'host' if c['id'] in HOST else None
    return out
