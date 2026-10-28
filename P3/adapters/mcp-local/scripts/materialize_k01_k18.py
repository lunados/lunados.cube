#!/usr/bin/env python3
"""Materialise K-01..K-18 (G6) from G6_PLAN_VIEWS_ACCEPTANCE_SPEC.md §5.

Expected values come from tests/g6/independent_k01_k18.json (transcribed before code). Inputs point to the
synthetic P2 fixtures by path, case and SHA-256; K-14 generates a large synthetic plan (160 jobs) whose
panel files exceed 2 MiB with the unchanged printers. No client data.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]; ROOT = BASE.parents[2]
sys.dont_write_bytecode = True
ORACLE = json.loads((BASE/'tests/g6/independent_k01_k18.json').read_text('utf-8'))
FIX = {
    'g73': 'P2/visual-printer-migration-v1/fixtures/golden_v073.json',
    'g74': 'P2/visual-printer-migration-v1/fixtures/golden_v074.json',
    'gseq': 'P2/visual-printer-sequence-v1/fixtures/golden_sequence.json',
    'gax': 'P2/visual-printer-axes-v1/fixtures/golden_axes.json',
    'avec': 'P2/visual-printer-axes-v1/fixtures/a01_a20_materialized.json',
}
FLOW = {'view': 'cube.flow', 'partition': 'subject', 'granularity': 'standard', 'lens': 'cube.lens.execution'}


def big_context(n=160):
    sys.path.insert(0, str(ROOT/'P2/visual-printer-axes-v1')); sys.path.insert(0, str(ROOT/'P2/visual-printer-axes-v1/scripts'))
    import materialize_a01_a20 as A
    from vpaxes import from_plan, print_panels      # unchanged 0.9.0 code: the plan must really exceed the limit
    ctx = A.context(jobs=[f'job-{i:03d}' for i in range(1, n+1)])
    d, _ = from_plan(ctx, 'mp-axes')
    _, files = print_panels(d, 'Z:referent', 'T', 'standard')
    size = sum(len(v) for v in files.values())
    assert size > int(2.5*1024*1024), size
    return ctx, size


def build():
    big, size = big_context()
    return {
        'K-01': {'kind': 'views_vs_cli', 'printer': 'vpmigration', 'source_from': {'fixture': 'g73', 'profile': None},
                 'view': {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'}},
        'K-02': {'kind': 'check_vs_cli', 'like': 'K-01'},
        'K-03': {'kind': 'baseline'},
        'K-04': {'kind': 'deterministic', 'like': 'K-01'},
        'K-05': {'kind': 'source_vs_cli', 'printer': 'vpmigration', 'fixture': 'g73', 'profile': None},
        'K-06': {'kind': 'source_vs_cli', 'printer': 'vpaxes', 'fixture': 'gax', 'profile': 'P2-VP-AXES/0.9.1'},
        'K-07': {'kind': 'views_vs_cli', 'printer': 'vpmigration', 'source_from': {'fixture': 'g74', 'profile': 'P2-VP-MIGRATION/0.7.4'}, 'view': FLOW},
        'K-08': {'kind': 'views_vs_cli', 'printer': 'vpsequence', 'source_from': {'fixture': 'gseq'},
                 'view': {'view': 'cube.sequence', 'partition': 'trigger', 'granularity': 'standard'}},
        'K-09': {'kind': 'views_vs_cli', 'printer': 'vpaxes', 'source_from': {'fixture': 'gax', 'profile': 'P2-VP-AXES/0.9.1'},
                 'view': {'view': 'cube.axes', 'rows': 'F', 'cols': 'Z:referent', 'granularity': 'standard'}},
        'K-10': {'kind': 'check', 'like': 'K-09'},
        'K-11': {'kind': 'tool', 'tool': 'cube_plan_source',
                 'args': {'context': {'format': 'aiaeao.cube.binding-context/9', 'context_id': 'k11'}, 'plan_id': 'mp-x', 'printer': 'vpmigration'}},
        'K-12': {'kind': 'tool_views', 'like': 'K-01', 'override': {'view': 'cube.matrix'}},
        'K-13': {'kind': 'tool_views_avec', 'case': 'A-18', 'view': {'view': 'cube.axes', 'rows': 'Z:referent', 'cols': 'T', 'granularity': 'detail'}},
        'K-14': {'kind': 'tool_views_context', 'printer': 'vpaxes', 'context': big, 'plan_id': 'mp-axes', 'raw_panel_bytes': size,
                 'view': {'view': 'cube.axes', 'rows': 'Z:referent', 'cols': 'T', 'granularity': 'standard'}},
        'K-15': {'kind': 'check_tampered', 'like': 'K-01'},
        'K-16': {'kind': 'tool', 'tool': 'cube_plan_source',
                 'args': {'context': {'format': 'aiaeao.cube.binding-context/7'}, 'plan_id': 'mp-x', 'printer': 'vpsequence'}},
        'K-17': {'kind': 'parity'},
        'K-18': {'kind': 'surface'},
    }


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    fixtures = {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in FIX.items()}
    cases = [{'id': k, 'input': vecs[k], **{x: exp[k][x] for x in ('expected_status', 'expected_code', 'expect')}} for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.g6-vectors/1', 'source': 'G6_PLAN_VIEWS_ACCEPTANCE_SPEC.md §5 + tests/g6/independent_k01_k18.json',
           'fixtures': fixtures, 'cases': cases}
    (BASE/'tests/g6/k01_k18_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
