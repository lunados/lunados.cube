"""VP-12 local CLI `python3 -m vplandscape`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .common import (PROFILE, PROFILES, SOURCE_PROFILE, VIEW, INPUT_FORMAT, MAX_COLUMNS, MAX_BANDS, BUDGET, LOCALES, PLACEMENT_DEFAULT, LEVELS,
                     VP12Error, VP07Error, encode, load_json, publish_dir, write_new)
from .source import from_plan
from .landscape import render_landscape
from .panels import print_panels, check_panels


def capabilities():
    return {'format': 'aiaeao.cube.vp12-capabilities/1', 'profile': PROFILE, 'profiles': list(PROFILES), 'reference_version': 'v9.4', 'views': [VIEW],
            'source_profile': SOURCE_PROFILE, 'inputs': ['aiaeao.cube.binding-context/10 (via VP-07.8 from-plan)', INPUT_FORMAT],
            'layer_map': 'aiaeao.cube.vp07-layer-map/1 (VP-07.2, optional)', 'max_columns': MAX_COLUMNS, 'max_bands': MAX_BANDS,
            'budgets': dict(BUDGET), 'granularities': list(LEVELS), 'locales': list(LOCALES), 'placement_default': list(PLACEMENT_DEFAULT),
            'operations': ['capabilities', 'from-plan', 'check-landscape', 'print-panels', 'check-panels'],
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'numeric_encoding': False,
            'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vplandscape', description='AIAEAO VP-12 landscape view (offline, deterministic SVG)')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    fp = s.add_parser('from-plan')
    for a in ('--context', '--plan', '--out'):
        fp.add_argument(a, required=True)
    fp.add_argument('--layers'); fp.add_argument('--labels')
    fp.add_argument('--steps', help='comma-separated declared step IDs (default first and last)')
    fp.add_argument('--placement', help='comma-separated placement predicates (default runs-on,hosted-by; empty for none)')
    fp.add_argument('--locale', choices=LOCALES, default='en')
    fp.add_argument('--granularity', choices=LEVELS, default='detail')
    fp.add_argument('--profile', default=PROFILE, help='0.12.0 (default) or 0.12.1 (VP-12.1: VG anchor of the layer column)')
    for name in ('check-landscape', 'print-panels'):
        x = s.add_parser(name)
        x.add_argument('--input', required=True)
        if name == 'print-panels':
            x.add_argument('--out', required=True)
    cp = s.add_parser('check-panels')
    cp.add_argument('--dir', required=True)
    a = p.parse_args(argv)
    out = sys.stdout.buffer
    try:
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command == 'from-plan':
            opt = lambda f: load_json(f, 'VP07_ADAPTER_INPUT') if f else None  # noqa: E731
            doc, info = from_plan(load_json(a.context, 'VP07_ADAPTER_INPUT'), a.plan, opt(a.layers), opt(a.labels),
                                  a.steps.split(',') if a.steps else None,
                                  None if a.placement is None else [x for x in a.placement.split(',') if x], a.locale, a.granularity, a.profile)
            write_new(Path(a.out), encode(doc))
            out.write(encode({'status': 'PASS', 'operation': 'from-plan', 'profile': doc['profile'], 'input_file': a.out,
                              'cells': len(doc['source']['cells']), 'steps': doc['steps']}))
            return 0
        if a.command == 'check-landscape':
            report, _ = render_landscape(load_json(a.input, 'VP12_INPUT'))
            out.write(encode(report)); return 0
        if a.command == 'print-panels':
            report, files = print_panels(load_json(a.input, 'VP12_INPUT'))
            d = publish_dir(files, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-panels', 'output_dir': str(d), 'panels': report['panel_count'],
                              'coverage': report['coverage']['status'], 'warnings': report['warnings']}))
            return 0
        out.write(encode(check_panels(a.dir))); return 0
    except (VP12Error, VP07Error) as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
