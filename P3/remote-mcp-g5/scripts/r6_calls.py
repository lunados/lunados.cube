"""MILE-011 TASK-067: fixed /10 validation and VP-07.6 G5 wire calls.

The payloads are the committed HO and OL vectors. The host subset is small enough
for the existing Worker CPU budget; the scripted offline and live suites use all.
"""
from __future__ import annotations
import json
from pathlib import Path
import r5_calls

REPO = Path(__file__).resolve().parents[3]
HOST = {'D-01', 'V-HO-01', 'V-HO-03', 'V-HO-05', 'P-OL-02', 'P-OL-04',
        'P-OL-06', 'P-OL-08', 'P-OL-11'}
run_chain = r5_calls.run_chain


def _cases(path):
    return json.loads((REPO/path).read_text('utf-8'))['cases']


def calls():
    out = [r5_calls.chain('D-01', 'D', [{'op': 'cube_discover_surface', 'args': {}}], 'host')]
    for c in _cases('P1/relation-origin-profile-v1/fixtures/ho01_ho12_materialized.json'):
        args = {'input_text': c['input_text'], 'context': c['context']}
        if c.get('input_format'):
            args['input_format'] = c['input_format']
        out.append(r5_calls.chain('V-'+c['id'], 'V', [{'op': 'cube_validate', 'args': args}],
                                  'host' if 'V-'+c['id'] in HOST else None))
    for c in _cases('P2/visual-printer-migration-v1/fixtures/ol01_ol12_materialized.json'):
        source = {'op': 'cube_plan_source', 'args': c['plan_source']}
        out.append(r5_calls.views_chain('P-'+c['id'], source, c['plan_views'],
                                        live='host' if 'P-'+c['id'] in HOST else None))
    return out
