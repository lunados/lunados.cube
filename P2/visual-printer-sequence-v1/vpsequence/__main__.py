"""VP-08 local CLI `python3 -m vpsequence`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys

from .common import (PROFILE, VP08Error, encode, load_json, publish_dir, LEVELS, BUDGET, TRIGGER_KINDS, MESSAGE_KINDS, FRAGMENTS,
                     MAX_DEPTH, LIMITS)
from .sequence import render_sequence
from .panels import print_panels, check_panels, PARTITIONS


def capabilities():
    return {'format': 'aiaeao.cube.vp08-capabilities/1', 'profile': PROFILE, 'reference_version': 'v9.4',
            'views': ['cube.sequence'], 'lenses': ['neutral'], 'granularities': list(LEVELS),
            'budgets': {k: dict(zip(('participants', 'messages', 'fragment_depth'), v)) for k, v in BUDGET.items()},
            'trigger_kinds': list(TRIGGER_KINDS), 'message_kinds': list(MESSAGE_KINDS), 'fragments': list(FRAGMENTS),
            'max_fragment_depth': MAX_DEPTH, 'limits': LIMITS, 'partitions': list(PARTITIONS),
            'operations': ['capabilities', 'check-sequence', 'print-sequence', 'print-panels', 'check-panels'],
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'p1_validation_included': False,
            'time_axis': False, 'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vpsequence', description='AIAEAO VP-08 sequence views (offline, deterministic SVG)')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    for name in ('check-sequence', 'print-sequence'):
        x = s.add_parser(name)
        x.add_argument('--source', required=True)
        x.add_argument('--trigger', required=True)
        x.add_argument('--granularity', default='standard', choices=list(LEVELS))
        x.add_argument('--overflow', default='summarize', choices=['summarize', 'reject'])
        if name == 'print-sequence':
            x.add_argument('--out', required=True)
    pp = s.add_parser('print-panels')
    pp.add_argument('--source', required=True)
    pp.add_argument('--partition', default='trigger')
    pp.add_argument('--granularity', default='standard')
    pp.add_argument('--overflow', default='summarize')
    pp.add_argument('--out', required=True)
    cp = s.add_parser('check-panels')
    cp.add_argument('--dir', required=True)
    a = p.parse_args(argv)
    out = sys.stdout.buffer
    try:
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command in ('check-sequence', 'print-sequence'):
            report, svgs = render_sequence(load_json(a.source, 'VP08_SOURCE_INVALID'), a.trigger, a.granularity, a.overflow)
            if a.command == 'print-sequence':
                files = {(f'window-{i+1:02d}.svg' if len(svgs) > 1 else 'render.svg'): b for i, b in enumerate(svgs)}
                files['report.json'] = encode(report)
                d = publish_dir(files, a.out)
                out.write(encode({'status': 'PASS', 'operation': a.command, 'output_dir': str(d), 'windows': len(svgs),
                                  'warnings': report['warnings']}))
            else:
                out.write(encode(report))
            return 0
        if a.command == 'print-panels':
            report, files = print_panels(load_json(a.source, 'VP08_SOURCE_INVALID'), a.partition, a.granularity, a.overflow)
            d = publish_dir(files, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-panels', 'output_dir': str(d), 'panels': report['panel_count'],
                              'coverage': report['coverage']['status'], 'warnings': len(report['warnings'])}))
            return 0
        out.write(encode(check_panels(a.dir)))
        return 0
    except VP08Error as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
