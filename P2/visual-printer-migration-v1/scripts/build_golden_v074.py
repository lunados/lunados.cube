#!/usr/bin/env python3
"""Build fixtures/golden_v074.json (VP074-07, D-8): synthetic, no client data.

Same P1.11 golden plan GM-pos as golden_v073.json, declared expectations for VP-07.4: the method partition
of cube.phases and the methods lines of cube.flow panels (from-plan with profile 0.7.4).
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
G73 = json.loads((HERE/'fixtures/golden_v073.json').read_text('utf-8'))
EXPECTED = {
    'phases': {'view': 'cube.phases', 'partition': 'method', 'granularity': 'standard'},
    'groups': [['migrate.rewrite/v1'], ['none']],
    'rewrite_cells': 16,
    'flow': {'view': 'cube.flow', 'partition': 'subject', 'granularity': 'standard', 'lens': 'cube.lens.execution'},
    'line_codes_by_step': {'p0': [], 'p1': ['T1'], 'p2': ['T2', 'T3', 'T4'], 'p3': []},
    'coverage': 'COMPLETE',
}


def main():
    out = {'format': 'aiaeao.cube.vp07-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (P1.11 golden GM-pos); no client data',
           'gm_pos_sha256': G73['gm_pos_sha256'], 'context': G73['context'], 'plan_id': G73['plan_id'], 'profile': 'P2-VP-MIGRATION/0.7.4',
           'expected': EXPECTED}
    (HERE/'fixtures/golden_v074.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden')


if __name__ == '__main__':
    main()
