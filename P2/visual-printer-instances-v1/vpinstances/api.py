"""G6: in-memory API of VP-11 (source via from-trace; one panel; check). No paths, no files, no side effects.

Same shape as the other plan printers (`aiaeao.cube.plan-views/1`): one view, one panel; its `input` re-renders it,
and `index` carries the same SVG.
"""
from __future__ import annotations
import json

from vpmigration.api import RESULT_FORMAT, SOURCE_FORMAT
from .common import PROFILE, VIEW, VP11Error, encode, sha_bytes, need
from .trace import from_trace
from .view import render_instances

PANEL_INPUT = 'aiaeao.cube.vp11-panel-input/1'


def source(context, statements, records=None):
    doc = from_trace(context, statements, records)
    return {'format': SOURCE_FORMAT, 'printer': 'vpinstances', 'profile': PROFILE, 'source': doc, 'mapping': None}


def _render(inp):
    return render_instances(inp['input'], inp.get('locale'))


def views(source, view=VIEW, locale=None):
    need(view == VIEW, 'VP11_VIEW_INVALID', f'VP-11 draws {VIEW} only')
    inp = {'format': PANEL_INPUT, 'profile': PROFILE, 'input': source, **({'locale': locale} if locale is not None else {})}
    report, svg = _render(inp)
    raw = encode(inp)
    panel = {'name': 'panel-01', 'svg': svg.decode('utf-8'), 'sha256': sha_bytes(svg), 'input': json.loads(raw), 'input_sha256': sha_bytes(raw)}
    return {'format': RESULT_FORMAT, 'printer': 'vpinstances', 'profile': PROFILE, 'view': view, 'panels': [panel],
            'index': {'svg': panel['svg'], 'sha256': panel['sha256'], 'note': 'single view: the index is the panel'}, 'report': report}


def check(result):
    """Re-render the panel from its input; SVG bytes, digests and the report must match."""
    try:
        need(isinstance(result, dict) and result.get('format') == RESULT_FORMAT and result.get('printer') == 'vpinstances'
             and len(result.get('panels', [])) == 1, 'VP11_PANEL_CHECK', 'not a single-panel VP-11 plan-views result', 'check')
        p = result['panels'][0]
        need(sha_bytes(encode(p['input'])) == p['input_sha256'], 'VP11_PANEL_CHECK', 'panel input digest mismatch', 'check')
        need(p['input'].get('format') == PANEL_INPUT, 'VP11_PANEL_CHECK', 'panel input format', 'check')
        report, svg = _render(p['input'])
        need(svg.decode('utf-8') == p['svg'] and sha_bytes(svg) == p['sha256'] == result['index']['sha256'], 'VP11_PANEL_CHECK',
             'SVG differs from the deterministic re-render of its input', 'check')
        need(report == result['report'], 'VP11_PANEL_CHECK', 'report differs from the re-render', 'check')
    except (KeyError, TypeError, AttributeError) as e:
        raise VP11Error('VP11_PANEL_CHECK', 'plan-views result is malformed: '+type(e).__name__, 'check') from e
    return {'status': 'PASS', 'panels': 1, 'svg_sha256': p['sha256'], 'violation_marks': report['violation_marks'],
            'checks': ['INPUT_DIGEST', 'DETERMINISTIC_RERENDER', 'REPORT_MATCH']}
