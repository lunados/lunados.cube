"""G6: in-memory API of VP-10 (source via from-plan; one panel; check). No paths, no files, no side effects.

The result has the shape of the other plan printers (`aiaeao.cube.plan-views/1`): VP-10 draws one view, so there is
exactly one panel; its `input` re-renders it. VP-10 has no panel index, so `index` carries the same SVG.
"""
from __future__ import annotations
import json

from vpmigration.api import RESULT_FORMAT, SOURCE_FORMAT
from .common import PROFILE, PROFILE_101, PROFILE_110, MATRIX_FORMAT, VP10Error, encode, sha_bytes, need
from .source import from_plan
from .statements import from_statements
from .cells import render_cells

PANEL_INPUT = 'aiaeao.cube.vp10-panel-input/1'


def source(context, plan_id, predicate=None, tracks=None, track=None, labels=None, steps=None, subjects=None, layers=None, statements=None,
           projection=None):
    if statements is not None or projection is not None:          # 0.11.0: a statement set instead of a plan (PO-7)
        need(plan_id is None and not any((tracks, track, labels, steps, subjects, layers)), 'VP10_ADAPTER_INPUT',
             'a statement-set source takes context, statements, predicate and projection only (no plan_id or plan slice)')
        doc = from_statements(context, statements, predicate, projection)
        return {'format': SOURCE_FORMAT, 'printer': 'vpcells', 'profile': PROFILE_110, 'source': doc, 'mapping': None}
    doc, mapping = from_plan(context, plan_id, predicate, tracks, track, labels, steps, subjects, layers)
    return {'format': SOURCE_FORMAT, 'printer': 'vpcells', 'profile': PROFILE, 'source': doc, 'mapping': mapping}


def _render(inp):
    return render_cells(inp['input'], inp['rows'], inp['cols'], inp['granularity'], inp.get('hide_empty'), inp.get('locale'),
                        inp.get('axis_order'))


def views(source, view='cube.cells', granularity='standard', rows=None, cols=None, hide_empty=None, locale=None, axis_order=None):
    prof = PROFILE if axis_order is None else PROFILE_101          # VP-10.1: only a declared order selects 0.10.1
    if isinstance(source, dict) and source.get('format') == MATRIX_FORMAT:
        prof = PROFILE_110
    inp = {'format': PANEL_INPUT, 'profile': prof, 'input': source, 'rows': rows or 'Y:referent', 'cols': cols or 'Y:referent',
           'granularity': granularity,
           **{k: v for k, v in (('hide_empty', hide_empty), ('locale', locale), ('axis_order', axis_order)) if v is not None}}
    report, svg = _render(inp)
    raw = encode(inp)
    panel = {'name': 'panel-01', 'svg': svg.decode('utf-8'), 'sha256': sha_bytes(svg), 'input': json.loads(raw), 'input_sha256': sha_bytes(raw)}
    return {'format': RESULT_FORMAT, 'printer': 'vpcells', 'profile': prof, 'view': view, 'panels': [panel],
            'index': {'svg': panel['svg'], 'sha256': panel['sha256'], 'note': 'single view: the index is the panel'}, 'report': report}


def check(result):
    """Re-render the panel from its input; SVG bytes, digests and the report must match."""
    try:
        need(isinstance(result, dict) and result.get('format') == RESULT_FORMAT and result.get('printer') == 'vpcells'
             and len(result.get('panels', [])) == 1, 'VP10_PANEL_CHECK', 'not a single-panel VP-10 plan-views result', 'coverage')
        p = result['panels'][0]
        need(sha_bytes(encode(p['input'])) == p['input_sha256'], 'VP10_PANEL_CHECK', 'panel input digest mismatch', 'coverage')
        need(p['input'].get('format') == PANEL_INPUT, 'VP10_PANEL_CHECK', 'panel input format', 'coverage')
        report, svg = _render(p['input'])
        need(svg.decode('utf-8') == p['svg'] and sha_bytes(svg) == p['sha256'] == result['index']['sha256'], 'VP10_PANEL_CHECK',
             'SVG differs from the deterministic re-render of its input', 'coverage')
        need(report == result['report'], 'VP10_PANEL_CHECK', 'report differs from the re-render', 'coverage')
    except (KeyError, TypeError, AttributeError) as e:
        raise VP10Error('VP10_PANEL_CHECK', 'plan-views result is malformed: '+type(e).__name__, 'coverage') from e
    return {'status': 'PASS', 'panels': 1, 'svg_sha256': p['sha256'], 'state_counts': report['state_counts'],
            'checks': ['INPUT_DIGEST', 'DETERMINISTIC_RERENDER', 'REPORT_MATCH']}
