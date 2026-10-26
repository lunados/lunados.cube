"""VP-07 local CLI `python3 -m vpmigration`. Machine-readable failures only (exit 2)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .common import PROFILE, VP07Error, encode, load_json, publish_dir, write_new, LEVELS, LENSES, STYLES
from .phases import render_plan, BUDGET
from .styles import render_styled
from .adapter import from_plan
from .panels import print_panels, check_panels, PARTITIONS


def capabilities():
    return {'format': 'aiaeao.cube.vp07-capabilities/1', 'profile': PROFILE, 'reference_version': 'v9.4',
            'views': ['cube.phases'], 'styled_views': ['cube.flow', 'cube.tree'], 'lens_cube_phases': ['neutral'],
            'flow_lenses': list(LENSES), 'granularities': list(LEVELS),
            'phases_budgets': {k: dict(zip(('rows', 'steps', 'cells', 'lanes_per_row'), v)) for k, v in BUDGET.items()},
            'edge_styles': list(STYLES), 'partitions': list(PARTITIONS),
            'operations': ['capabilities', 'check-phases', 'print-phases', 'check-styled', 'print-styled', 'from-plan',
                           'print-panels', 'check-panels'],
            'transport': 'local_cli_only', 'network_api': False, 'mcp_tool': False, 'p1_validation_included': False,
            'projection_semantics': 'declared_unverified_display_only'}


def main(argv=None):
    p = argparse.ArgumentParser(prog='vpmigration', description='AIAEAO VP-07 migration views (offline, deterministic SVG)')
    s = p.add_subparsers(dest='command', required=True)
    s.add_parser('capabilities')
    for name in ('check-phases', 'print-phases'):
        x = s.add_parser(name)
        x.add_argument('--plan', required=True)
        x.add_argument('--overflow', default='summarize', choices=['summarize', 'reject'])
        if name == 'print-phases':
            x.add_argument('--out', required=True)
    for name in ('check-styled', 'print-styled'):
        x = s.add_parser(name)
        x.add_argument('--input', required=True)
        if name == 'print-styled':
            x.add_argument('--out', required=True)
    fp = s.add_parser('from-plan')
    fp.add_argument('--context', required=True)
    fp.add_argument('--plan', required=True)
    fp.add_argument('--tracks')
    fp.add_argument('--track')
    fp.add_argument('--labels')
    fp.add_argument('--steps')
    fp.add_argument('--subjects')
    fp.add_argument('--edge-styles')
    fp.add_argument('--witness-prefixes')
    fp.add_argument('--out', required=True)
    pp = s.add_parser('print-panels')
    pp.add_argument('--source', required=True)
    pp.add_argument('--view', required=True)
    pp.add_argument('--partition', required=True)
    pp.add_argument('--granularity', required=True)
    pp.add_argument('--lens')
    pp.add_argument('--out', required=True)
    cp = s.add_parser('check-panels')
    cp.add_argument('--dir', required=True)
    a = p.parse_args(argv)
    try:
        out = sys.stdout.buffer
        if a.command == 'capabilities':
            out.write(encode(capabilities())); return 0
        if a.command in ('check-phases', 'print-phases'):
            report, svg = render_plan(load_json(a.plan), a.overflow)
            if a.command == 'print-phases':
                d = publish_dir({'render.svg': svg, 'report.json': encode(report)}, a.out)
                out.write(encode({'status': 'PASS', 'operation': a.command, 'output_dir': str(d), 'svg_sha256': report['svg_sha256'],
                                  'warnings': report['warnings']}))
            else:
                out.write(encode(report))
            return 0
        if a.command in ('check-styled', 'print-styled'):
            result, svg = render_styled(load_json(a.input))
            if a.command == 'print-styled':
                d = publish_dir({'render.svg': svg, 'report.json': encode(result)}, a.out)
                out.write(encode({'status': 'PASS', 'operation': a.command, 'output_dir': str(d), 'svg_sha256': result['svg_sha256']}))
            else:
                out.write(encode(result))
            return 0
        if a.command == 'from-plan':
            opt = lambda f: load_json(f, 'VP07_ADAPTER_INPUT') if f else None  # noqa: E731
            src, mapping = from_plan(load_json(a.context, 'VP07_ADAPTER_INPUT'), a.plan, opt(a.tracks), a.track, opt(a.labels), a.steps,
                                     a.subjects.split(',') if a.subjects else None, opt(a.edge_styles), opt(a.witness_prefixes))
            target = Path(a.out)
            mpath = target.with_name(target.stem+'.mapping.json')
            if mpath.exists():
                raise VP07Error('VP07_OUTPUT_EXISTS', 'output already exists: '+str(mpath), 'output')
            write_new(target, encode(src))
            write_new(mpath, encode(mapping))
            out.write(encode({'status': 'PASS', 'operation': 'from-plan', 'source_file': str(target), 'mapping_file': str(mpath),
                              'cells': len(src['cells']), 'empty_steps': mapping['empty_steps']}))
            return 0
        if a.command == 'print-panels':
            report, files = print_panels(load_json(a.source, 'VP07_SOURCE_INVALID'), a.view, a.partition, a.granularity, a.lens)
            d = publish_dir(files, a.out)
            out.write(encode({'status': 'PASS', 'operation': 'print-panels', 'output_dir': str(d), 'panels': report['panel_count'],
                              'coverage': report['coverage']['status'], 'warnings': len(report['warnings'])}))
            return 0
        out.write(encode(check_panels(a.dir)))
        return 0
    except VP07Error as e:
        sys.stderr.buffer.write(encode(e.diagnostic()))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
