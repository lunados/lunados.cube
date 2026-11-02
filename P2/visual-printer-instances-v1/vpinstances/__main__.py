"""VP-11 local CLI `python3 -m vpinstances`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .common import PROFILE, VIEW, INPUT_FORMAT, LOCALE_PINNED, VP09Error, encode, load_json, publish_dir, write_new
from .trace import from_trace
from .view import render_instances


def capabilities():
    return {'format': 'aiaeao.cube.vp11-capabilities/1', 'profile': PROFILE, 'reference_version': 'v9.4', 'views': [VIEW],
            'context': 'aiaeao.cube.binding-context/9 (P1.13 control_flow)', 'trace': 'aiaeao.cube.statement-set/1 for that context',
            'records': 'aiaeao.cube.conformance-record/1 of lunados.lib analyze.trace-conformance/v1; read, never recomputed',
            'gateways': ['exclusive split', 'exclusive merge', 'parallel split', 'parallel join'], 'inputs': [INPUT_FORMAT],
            'locales': ['en']+sorted(LOCALE_PINNED), 'operations': ['capabilities', 'from-trace', 'check-instances', 'print-instances'],
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'numeric_encoding': False,
            'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vpinstances')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    ft = s.add_parser('from-trace')
    for a_ in ('--context', '--trace', '--out'):
        ft.add_argument(a_, required=True)
    ft.add_argument('--record', action='append', default=[])
    for name in ('check-instances', 'print-instances'):
        x = s.add_parser(name)
        x.add_argument('--input', required=True)
        x.add_argument('--locale')
        if name == 'print-instances':
            x.add_argument('--out', required=True)
    a = p.parse_args(argv)
    out = sys.stdout.buffer
    try:
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command == 'from-trace':
            doc = from_trace(load_json(a.context, 'VP11_ADAPTER_INPUT'), load_json(a.trace, 'VP11_TRACE_INVALID'),
                             [load_json(r, 'VP11_RECORD_INVALID') for r in a.record])
            target = Path(a.out)
            write_new(target, encode(doc))
            out.write(encode({'status': 'PASS', 'operation': 'from-trace', 'profile': PROFILE, 'input_file': str(target),
                              'tokens': len(doc['tokens']), 'records': len(doc['records'])}))
            return 0
        report, svg = render_instances(load_json(a.input, 'VP11_SOURCE_INVALID'), a.locale)
        if a.command == 'print-instances':
            d = publish_dir({'render.svg': svg, 'report.json': encode(report)}, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-instances', 'output_dir': str(d), 'violation_marks': report['violation_marks'],
                              'warnings': report['warning_summary']}))
        else:
            out.write(encode(report))
        return 0
    except VP09Error as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
