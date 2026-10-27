"""VP-09 local CLI `python3 -m vpaxes`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .common import PROFILE, AXES, RESERVED, PAIRS, BUDGET, LEVELS, VP09Error, encode, load_json, publish_dir, write_new
from .source import from_plan
from .axes import render_axes
from .panels import print_panels, check_panels


def capabilities():
    return {'format': 'aiaeao.cube.vp09-capabilities/1', 'profile': PROFILE, 'reference_version': 'v9.4', 'views': ['cube.axes'],
            'axes': list(AXES), 'reserved_axes': list(RESERVED), 'pairs': [sorted(p) if len(p) > 1 else ['X', 'X'] for p in PAIRS],
            'granularities': list(LEVELS), 'budgets': {k: dict(zip(('rows', 'cols', 'entries_per_cell'), v)) for k, v in BUDGET.items()},
            'operations': ['capabilities', 'from-plan', 'check-axes', 'print-axes', 'print-panels', 'check-panels'],
            'inputs': ['aiaeao.cube.vp07-migration-source/1 (0.7.1, 0.7.2)', 'aiaeao.cube.vp09-axes-input/1'],
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'numeric_encoding': False,
            'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vpaxes', description='AIAEAO VP-09 declared axes view (offline, deterministic SVG)')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    fp = s.add_parser('from-plan')
    for a in ('--context', '--plan', '--out'):
        fp.add_argument(a, required=True)
    for a in ('--tracks', '--track', '--labels', '--steps', '--subjects', '--layers'):
        fp.add_argument(a)
    for name in ('check-axes', 'print-axes', 'print-panels'):
        x = s.add_parser(name)
        x.add_argument('--input', required=True)
        x.add_argument('--rows', required=True)
        x.add_argument('--cols', required=True)
        x.add_argument('--granularity', default='standard')
        if name != 'check-axes':
            x.add_argument('--out', required=True)
    cp = s.add_parser('check-panels')
    cp.add_argument('--dir', required=True)
    a = p.parse_args(argv)
    out = sys.stdout.buffer
    try:
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command == 'from-plan':
            opt = lambda f: load_json(f, 'VP09_ADAPTER_INPUT') if f else None  # noqa: E731
            doc, mapping = from_plan(load_json(a.context, 'VP09_ADAPTER_INPUT'), a.plan, opt(a.tracks), a.track, opt(a.labels), a.steps,
                                     a.subjects.split(',') if a.subjects else None, opt(a.layers))
            target = Path(a.out)
            write_new(target, encode(doc))
            out.write(encode({'status': 'PASS', 'operation': 'from-plan', 'input_file': str(target), 'cells': len(doc['source']['cells']),
                              'method_bindings': len(doc['method_bindings'])}))
            return 0
        if a.command in ('check-axes', 'print-axes'):
            report, svg = render_axes(load_json(a.input, 'VP09_SOURCE_INVALID'), a.rows, a.cols, a.granularity)
            if a.command == 'print-axes':
                d = publish_dir({'render.svg': svg, 'report.json': encode(report)}, a.out)
                out.write(encode({'status': 'PASS', 'operation': a.command, 'output_dir': str(d), 'warnings': report['warnings']}))
            else:
                out.write(encode(report))
            return 0
        if a.command == 'print-panels':
            report, files = print_panels(load_json(a.input, 'VP09_SOURCE_INVALID'), a.rows, a.cols, a.granularity)
            d = publish_dir(files, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-panels', 'output_dir': str(d), 'panels': report['panel_count'],
                              'coverage': report['coverage']['status']}))
            return 0
        out.write(encode(check_panels(a.dir)))
        return 0
    except VP09Error as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
