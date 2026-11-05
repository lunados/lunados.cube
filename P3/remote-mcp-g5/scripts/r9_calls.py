"""MILE-015 TASK-077: G5 wire calls for core 0.9.2-proof (P1.15 binding-context/11, VP-07.8).

R9 = every R8 call (unchanged bytes), the fourteen P1.15 vectors SN-01…SN-14 through cube_validate, and four
VP-07.8 calls on the synthetic plan of P2 tests/test_vp077.py with an X endpoint (Admission) as object.
"""
from __future__ import annotations
import json
from pathlib import Path
import r5_calls
import r8_calls

REPO = Path(__file__).resolve().parents[3]
P078 = 'P2-VP-MIGRATION/0.7.8'
HOST = r8_calls.HOST | {'V-SN-02', 'V-SN-08', 'V-SN-10', 'V-SN-11', 'P78-01', 'P78-02'}
run_chain = r5_calls.run_chain


def calls():
    out = [c for c in r8_calls.calls()]
    for c in json.loads((REPO/'P1/scope-nesting-profile-v1/fixtures/sn01_sn14_materialized.json').read_text('utf-8'))['cases']:
        args = {'input_text': c['input_text'], 'input_format': c['input_format'], 'context': c['context']}
        out.append(r5_calls.chain('V-'+c['id'], 'V', [{'op': 'cube_validate', 'args': args}]))
    t = r8_calls._vp077()
    x_ctx = t.context()
    ref = next(r for r in x_ctx['referents'] if r['ref'] == 's:grant')
    ref.update(concept_id='X:endpoint:admission', home='X')
    x_ctx['predicate_contracts'][0]['object_concept_ids'].append('X:endpoint:admission')
    src = r5_calls.source
    out += [
        r5_calls.views_chain('P78-01', src(x_ctx, 'pm-077', 'vpmigration', profile=P078, origin_lines=True),
                             {'view': 'cube.flow', 'granularity': 'detail', 'partition': 'subject'}),
        r5_calls.views_chain('P78-02', src(x_ctx, 'pm-077', 'vpmigration', profile=P078),
                             {'view': 'cube.phases', 'granularity': 'detail', 'partition': 'subject'}),
        r5_calls.views_chain('P78-03', src(t.context(), 'pm-077', 'vpmigration', profile=P078, origin_lines=True),
                             {'view': 'cube.flow', 'granularity': 'standard', 'partition': 'subject'}),
        r5_calls.chain('P78-04', 'P', [src(x_ctx, 'pm-077', 'vpmigration', profile='P2-VP-MIGRATION/0.7.7', origin_lines=True)]),
    ]
    for c in out:
        c['live'] = 'host' if c['id'] in HOST else None
    return out
