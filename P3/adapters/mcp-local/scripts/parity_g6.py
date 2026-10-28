#!/usr/bin/env python3
"""G6 MP-1/MP-2 (K-17): every vector of VP-07 (V, W, L, M, N, O), VP-08 (S) and VP-09 (A, B, H) through the G6
tools equals the unchanged CLI — file by file (SHA-256) for PASS, the same error code for FAIL.

C-12: the O vectors (VP-07.5) carry locale / hide_ledger / method-sets; O-06 also prints its flow view. The H
vectors (VP-09.2) carry hide_empty / locale; their single-image cases are printed as panels for the comparison.

Covered per vector: from-plan (source and mapping bytes) and print-panels (all files). Single-image
operations (print-phases, print-sequence, print-axes, styled) are not part of G6 (D-9) and are skipped.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]; ROOT = BASE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE/'scripts'))
from aiaeao_mcp_local import plan_views as PV  # noqa: E402
import g6_cli as CLI  # noqa: E402
from vpmigration.common import encode  # noqa: E402

SETS = [('vpmigration', 'P2/visual-printer-migration-v1/fixtures/'+f) for f in
        ('v01_v28_materialized.json', 'w01_w17_materialized.json', 'l01_l13_materialized.json', 'm01_m12_materialized.json',
         'n01_n14_materialized.json', 'o01_o15_materialized.json')]
SETS += [('vpsequence', 'P2/visual-printer-sequence-v1/fixtures/s01_s20_materialized.json')]
SETS += [('vpaxes', 'P2/visual-printer-axes-v1/fixtures/'+f) for f in ('a01_a20_materialized.json', 'b01_b20_materialized.json',
                                                                          'h01_h16_materialized.json')]
PANELS_FOR_RENDER = ('H-',)   # VP-09.2 vectors: render cases are compared through print-panels as well
SOURCE_KEYS = ('tracks', 'track', 'labels', 'steps', 'subjects', 'edge_styles', 'witness_prefixes', 'profile', 'layers')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def outcome(fn):
    try:
        return 'PASS', fn()
    except PV.PlanFailure as e:
        return 'FAIL', e.diagnostic['code']
    except CLI.CliError as e:
        return 'FAIL', e.code


def tool_files(res):
    """MCP result → the files it stands for (same mapping check-panels reads)."""
    from vpmigration.api import to_files
    return to_files(res)


def compare(a, b):
    if a[0] != b[0]:
        return f'status {a[0]} vs {b[0]}'
    if a[0] == 'FAIL':
        return None if a[1] == b[1] else f'code {a[1]} vs {b[1]}'
    if isinstance(a[1], dict) and isinstance(b[1], dict):
        if set(a[1]) != set(b[1]):
            return 'file sets differ'
        bad = [n for n in a[1] if sha(a[1][n]) != sha(b[1][n])]
        return None if not bad else 'differ: '+', '.join(bad[:4])
    return None if a[1] == b[1] else 'bytes differ'


def run_case(printer, c):
    """Yield (step, problem or None) for one vector."""
    inp = c['input']
    op = c['op']
    if op in ('from-plan', 'render', 'panels') and 'context' in inp:
        p = 'vpaxes' if printer == 'vpaxes' else 'vpmigration'
        opt = {k: inp[k] for k in SOURCE_KEYS if k in inp}
        t = outcome(lambda: PV.plan_source(inp['context'], inp['plan_id'], p, **opt))
        cl = outcome(lambda: CLI.from_plan(p, inp['context'], inp['plan_id'], **opt))
        if t[0] == 'PASS' and cl[0] == 'PASS':
            yield 'from-plan', (None if encode(t[1]['source']) == cl[1][0] and (cl[1][1] is None or encode(t[1]['mapping']) == cl[1][1])
                                else 'source or mapping bytes differ')
            src = t[1]['source']
        else:
            yield 'from-plan', compare(t, cl)
            return
    elif 'source' in inp:
        src = inp['source']
    else:
        return
    if printer == 'vpmigration':
        then = inp.get('then') if op == 'from-plan' else (inp if op == 'panels' else None)
        if not then:
            return
        for name, t_ in (('print-panels', then), ('print-panels flow', inp.get('flow'))):
            if not t_:
                continue
            disp = {k: t_[k] for k in ('locale', 'hide_ledger') if t_.get(k)}
            kw = {'partition': t_['partition'], 'lens': t_.get('lens'), **disp}
            view, gran = t_['view'], t_['granularity']
            cli_kw = dict(view=view, partition=t_['partition'], granularity=gran, lens=t_.get('lens'), **disp)
            t = outcome(lambda: tool_files(PV.plan_views(src, view, gran, **kw)))
            cl = outcome(lambda: CLI.print_panels(printer, src, **cli_kw))
            yield name, compare(t, cl)
        return
    elif printer == 'vpsequence':
        if op != 'panels':
            return
        view, gran = 'cube.sequence', inp['granularity']
        kw = {'partition': inp['partition'], 'overflow': inp.get('overflow')}
        cli_kw = dict(partition=inp['partition'], granularity=gran, overflow=inp.get('overflow'))
    else:
        if op != 'panels' and not c['id'].startswith(PANELS_FOR_RENDER):
            return
        view, gran = 'cube.axes', inp['granularity']
        disp = {k: inp[k] for k in ('hide_empty', 'locale') if inp.get(k)}
        kw = {'rows': inp['rows'], 'cols': inp['cols'], **disp}
        cli_kw = dict(rows=inp['rows'], cols=inp['cols'], granularity=gran, **disp)
    t = outcome(lambda: tool_files(PV.plan_views(src, view, gran, **kw)))
    cl = outcome(lambda: CLI.print_panels(printer, src, **cli_kw))
    yield 'print-panels', compare(t, cl)


def sweep(verbose=False):
    total, bad = 0, []
    for printer, rel in SETS:
        for c in json.loads((ROOT/rel).read_text('utf-8'))['cases']:
            for step, problem in run_case(printer, c):
                total += 1
                if problem:
                    bad.append(f"{c['id']} {step}: {problem}")
                if verbose:
                    print('FAIL' if problem else 'PASS', c['id'], step, problem or '')
    return total, bad


def main():
    total, bad = sweep('-v' in sys.argv)
    for b in bad:
        print('DIFF', b)
    print(f'{total-len(bad)}/{total} MCP == CLI (from-plan and print-panels over V, W, L, M, N, O, S, A, B, H)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
