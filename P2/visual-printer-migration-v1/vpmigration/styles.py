"""VP-07 Path F: declared edge styles over an unchanged VP-06 result (ES-1…ES-6, D-9).

The frozen VP-06 `render_job` renders first; VP-07 only changes dash geometry of the
`line` children of each `g[data-predicate-id]` and appends a legend below the canvas.
The arrowhead path, colours and every VP-03/VP-04/VP-05 marker stay as rendered.
"""
from __future__ import annotations
from xml.etree import ElementTree as ET

from .common import (PROFILE, PROFILES, P070, NS, DASH, STROKE, MUTED, NOT_EVALUATED, add, line, rect, text, cjson, sha_bytes, VP07Error, need,
                     keys, check_edge_styles, style_line, double_of, no_active_content, fmt)
from vpprint.core import render_job, PrintError as VP06PrintError

ENVELOPE_FORMAT = 'aiaeao.cube.vp07-styled-print/1'
RESULT_FORMAT = 'aiaeao.cube.vp07-styled-print-result/1'


def validate_envelope(env):
    keys(env, ('format', 'profile', 'reference_version', 'job'), ('edge_styles',), 'VP07_ENVELOPE_INVALID', 'VP-07 styled print envelope')
    need(env['format'] == ENVELOPE_FORMAT, 'VP07_ENVELOPE_INVALID', 'format must be '+ENVELOPE_FORMAT)
    need(env['profile'] in PROFILES, 'VP07_ENVELOPE_INVALID', 'profile must be one of '+', '.join(PROFILES))
    need(env['reference_version'] == 'v9.4', 'VP07_ENVELOPE_INVALID', 'reference_version must be v9.4')
    need(isinstance(env['job'], dict), 'VP07_ENVELOPE_INVALID', 'job must be a VP-04 request object')
    return check_edge_styles(env['edge_styles']) if 'edge_styles' in env else None


def apply_styles(base_svg, styles, profile_note='VP-07 · EDGE STYLES', profile=P070):
    """Return (styled_svg, ledger). `styles` may be empty dict; None means: return base bytes unchanged."""
    if styles is None:
        return base_svg, {'edge_styles_present': False, 'styled': {}, 'unstyled': []}
    root = ET.fromstring(base_svg)
    styled, unstyled, seen = {}, [], []
    for g in root.iter(f'{{{NS}}}g'):
        pid = g.get('data-predicate-id')
        if pid is None:
            continue
        if pid not in seen:
            seen.append(pid)
        st = styles[pid]['style'] if pid in styles else 'solid'
        if pid in styles:
            styled[pid] = st
        elif pid not in unstyled:
            unstyled.append(pid)
        g.set('data-vp07-edge-style', st)
        for el in [x for x in list(g) if x.tag == f'{{{NS}}}line']:
            style_line(el, st)
            if st == 'double':
                double_of(g, el)
    h0 = int(float(root.get('height')))
    rows = [(pid, styled.get(pid, 'solid')) for pid in seen]
    extra = 58+22*(len(rows) or 1)
    h1 = h0+extra
    root.set('height', str(h1))
    root.set('viewBox', f'0 0 1200 {h1}')
    bg = next((c for c in root if c.tag == f'{{{NS}}}rect' and c.get('x') == '0' and c.get('y') == '0' and c.get('width') == '1200'), None)
    if bg is not None:
        bg.set('height', str(h1))
    root.set('data-vp07-printer-profile', profile)
    root.set('data-vp07-base-svg-sha256', sha_bytes(base_svg))
    lg = add(root, 'g', **{'data-vp07-legend': 'display-only', 'aria-label': 'Declared edge style legend'})
    rect(lg, 48, h0+8, 1104, extra-16, '#94A3B8', '#F8FAFC', 9)
    text(lg, 65, h0+32, profile_note+' · declared legend · line style is not a verdict, cause or time order', 13, '#334155', 'bold')
    y = h0+56
    if not rows:
        text(lg, 65, y, 'no declared edges in this view', 12, MUTED)
    for pid, st in rows:
        sample = line(lg, 70, y-4, 130, y-4, STROKE)
        style_line(sample, st)
        if st == 'double':
            line(lg, 70, y-1, 130, y-1, STROKE)
        lab = styles[pid]['legend'] if pid in styles else pid+' · unstyled (solid)'
        text(lg, 142, y, f'{st} · {lab}', 12, '#334155')
        y += 22
    ledger = {'edge_styles_present': True, 'styled': styled, 'unstyled': unstyled}
    meta = add(root, 'metadata', id='vp07-edge-style-ledger')
    meta.text = cjson({'profile': profile, 'base_svg_sha256': sha_bytes(base_svg), **ledger, 'status': 'declared_unverified'})
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(svg)), 'VP07_AUDIT', 'styled SVG contains active content', 'audit')
    return svg, ledger


def render_styled(env):
    styles = validate_envelope(env)
    try:
        base_result, base_svg = render_job(env['job'])
    except VP06PrintError as e:
        raise VP07Error(e.code, str(e), e.stage) from e
    svg, ledger = apply_styles(base_svg, styles, profile=env['profile'])
    warnings = [{'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': p} for p in ledger['unstyled']]
    result = {'format': RESULT_FORMAT, 'profile': env['profile'], 'reference_version': 'v9.4', 'status': 'PASS',
              'migration_view_profile': env['profile'], 'base_svg_sha256': sha_bytes(base_svg), 'svg_sha256': sha_bytes(svg),
              'svg_unchanged': svg == base_svg, 'edge_style_ledger': ledger, 'warnings': warnings,
              'vp06_result': base_result, 'source_status': 'declared_unverified', **NOT_EVALUATED,
              'notices': ['The VP-06 result is nested unmodified; only dash geometry and a legend were added.',
                          'Edge styles carry only their declared legend text.']}
    return result, svg
