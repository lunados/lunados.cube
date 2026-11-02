"""VP-10 local CLI `python3 -m vpcells`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from vpaxes.common import load_json, publish_dir, write_new
from .common import PROFILE, PROFILE_101, PROFILE_110, BASE_PROFILE, INPUT_FORMAT, MATRIX_FORMAT, LOCALE_PINNED, VP09Error, encode
from .source import from_plan
from .statements import from_statements
from .cells import render_cells


def capabilities():
    return {'format': 'aiaeao.cube.vp10-capabilities/1', 'profile': PROFILE, 'base_profile': BASE_PROFILE, 'reference_version': 'v9.4',
            'views': ['cube.cells'], 'pairs': [['Y:referent', 'Y:referent']], 'states': ['marked', 'checked', 'unknown', 'hidden'],
            'coverage_source': 'coverage_declarations of aiaeao.cube.binding-context/8 (P1.12), one predicate per view',
            'inputs': [INPUT_FORMAT], 'locales': ['en']+sorted(LOCALE_PINNED), 'hide_empty': ['rows', 'cols', 'both'],
            'operations': ['capabilities', 'from-plan', 'from-statements', 'check-cells', 'print-cells'],
            'display_options': {'axis_order': f'optional list of Y display IDs (--axis-order a,b,c); selects {PROFILE_101}, without it {PROFILE}'},
            'statement_sets': {'profile': PROFILE_110, 'operation': 'from-statements', 'input': MATRIX_FORMAT, 'pairs': [['Y:referent', 'Y:referent'], ['Z:referent', 'Z:referent']],
                               'aggregation': 'reads a lunados.lib project.aggregate-relations/v1 record; never recomputes'},
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'numeric_encoding': False,
            'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vpcells')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    fp = s.add_parser('from-plan')
    for a in ('--context', '--plan', '--predicate', '--out'):
        fp.add_argument(a, required=True)
    for a in ('--tracks', '--track', '--labels', '--steps', '--subjects', '--layers'):
        fp.add_argument(a)
    fs = s.add_parser('from-statements')
    for a_ in ('--context', '--statements', '--out'):
        fs.add_argument(a_, required=True)
    fs.add_argument('--predicate')
    fs.add_argument('--projection')
    for name in ('check-cells', 'print-cells'):
        x = s.add_parser(name)
        x.add_argument('--input', required=True)
        x.add_argument('--rows', default='Y:referent')
        x.add_argument('--cols', default='Y:referent')
        x.add_argument('--granularity', default='standard')
        x.add_argument('--hide-empty', choices=('rows', 'cols', 'both'))
        x.add_argument('--locale')
        x.add_argument('--axis-order', help='comma-separated display IDs (VP-10.1)')
        if name == 'print-cells':
            x.add_argument('--out', required=True)
    a = p.parse_args(argv)
    out = sys.stdout.buffer
    try:
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command == 'from-plan':
            opt = lambda f: load_json(f, 'VP10_ADAPTER_INPUT') if f else None  # noqa: E731
            doc, _ = from_plan(load_json(a.context, 'VP10_ADAPTER_INPUT'), a.plan, a.predicate, opt(a.tracks), a.track, opt(a.labels), a.steps,
                               a.subjects.split(',') if a.subjects else None, opt(a.layers))
            target = Path(a.out)
            write_new(target, encode(doc))
            c = doc['coverage']
            out.write(encode({'status': 'PASS', 'operation': 'from-plan', 'profile': PROFILE, 'input_file': str(target), 'predicate': c['predicate'],
                              'declarations': len(c['declarations']), 'ignored': len(c['ignored'])}))
            return 0
        if a.command == 'from-statements':
            doc = from_statements(load_json(a.context, 'VP10_ADAPTER_INPUT'), load_json(a.statements, 'VP10_STATEMENT_SET_INVALID'), a.predicate,
                                  load_json(a.projection, 'VP10_PROJECTION_INVALID') if a.projection else None)
            target = Path(a.out)
            write_new(target, encode(doc))
            out.write(encode({'status': 'PASS', 'operation': 'from-statements', 'profile': PROFILE_110, 'input_file': str(target),
                              'predicate': doc['predicate'], 'entries': len(doc['entries']), 'aggregated': doc['aggregation'] is not None}))
            return 0
        order = a.axis_order.split(',') if a.axis_order is not None else None
        report, svg = render_cells(load_json(a.input, 'VP10_SOURCE_INVALID'), a.rows, a.cols, a.granularity, a.hide_empty, a.locale, order)
        if a.command == 'print-cells':
            d = publish_dir({'render.svg': svg, 'report.json': encode(report)}, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-cells', 'output_dir': str(d), 'state_counts': report['state_counts'],
                              'warnings': report['warning_summary']}))
        else:
            out.write(encode(report))
        return 0
    except VP09Error as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
