"""CP-001 / G6: VP-07, VP-08 and VP-09 plan views as in-memory MCP operations (local stdio only).

The view decides the printer. Printers run unchanged through their `api` modules; this layer only
validates arguments, dispatches, enforces the transport limits and turns printer errors into tool
errors. No paths, no files, no network; nothing is inferred and nothing is validated semantically.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
_PKGS = ('visual-printer-migration-v1', 'visual-printer-sequence-v1', 'visual-printer-axes-v1')
for _d in _PKGS:
    if not (ROOT/'P2'/_d).is_dir():
        raise RuntimeError('P2 plan printer required as sibling tree: '+_d)
    if str(ROOT/'P2'/_d) not in sys.path:
        sys.path.insert(0, str(ROOT/'P2'/_d))
from vpmigration import api as vp07, common as c07  # noqa: E402
from vpmigration.source import FORMAT as VP07_SOURCE  # noqa: E402
from vpsequence import api as vp08, common as c08  # noqa: E402
from vpsequence.source import FORMAT as VP08_SOURCE  # noqa: E402
from vpaxes import api as vp09, common as c09  # noqa: E402
from vpaxes.common import INPUT_FORMAT as VP09_INPUT  # noqa: E402

DIAG_FORMAT = 'aiaeao.cube.mcp-plan-diagnostic/1'
MAX_REQUEST_BYTES = 2*1024*1024
MAX_SVG_BYTES = 512*1024
MAX_RESPONSE_BYTES = 2*1024*1024
TOOLS = ('cube_plan_source', 'cube_plan_views', 'cube_plan_check')
VIEWS = {'cube.phases': 'vpmigration', 'cube.flow': 'vpmigration', 'cube.sequence': 'vpsequence', 'cube.axes': 'vpaxes'}
PRINTERS = ('vpmigration', 'vpsequence', 'vpaxes')
# options each view takes (MT-1, §2 P3_PLAN_ARGUMENT_INVALID); `granularity` is common to all
OPTIONS = {'cube.phases': {'partition', 'locale', 'hide_ledger'}, 'cube.flow': {'partition', 'lens', 'locale', 'hide_ledger'},
           'cube.sequence': {'partition', 'overflow'}, 'cube.axes': {'rows', 'cols', 'hide_empty', 'locale'}}
# C-12: display options of VP-07.5 / VP-09.2; the printers accept them only for their 0.7.5 / 0.9.2 sources (D-1)
DISPLAY_OPTIONS = {'vpmigration': {'profile': c07.P075, 'locale': None, 'hide_ledger': 'bool', 'selections': [c07.METHOD_SETS]},
                   'vpaxes': {'profile': c09.P092, 'locale': None, 'hide_empty': list(c09.HIDE_EMPTY), 'pairs_added': ['Y × Y']}}
REQUIRED = {'cube.phases': {'partition'}, 'cube.flow': {'partition', 'lens'}, 'cube.sequence': set(), 'cube.axes': {'rows', 'cols'}}
SOURCE_OPTIONS = {'vpmigration': {'tracks', 'track', 'labels', 'steps', 'subjects', 'edge_styles', 'witness_prefixes', 'profile', 'layers'},
                  'vpaxes': {'tracks', 'track', 'labels', 'steps', 'subjects', 'layers', 'profile'}}
HINT = 'choose a partition, the granularity overview or standard, or a step/subject/track slice (from-plan); nothing was truncated'
ERRORS = (c07.VP07Error, c08.VP08Error, c09.VP09Error)
NOT_EVALUATED = {'epistemic_warrant': 'NOT_EVALUATED', 'current_authority': 'NOT_EVALUATED', 'canonical_admission': 'NOT_EVALUATED'}


class PlanFailure(Exception):
    def __init__(self, diagnostic: dict):
        self.diagnostic = diagnostic
        super().__init__(diagnostic['code']+': '+diagnostic['message'])


def _fail(code, message, stage='transport', **extra):
    raise PlanFailure({'format': DIAG_FORMAT, 'status': 'FAIL', 'code': code, 'stage': stage, 'message': message,
                       'files_written': False, **extra, **NOT_EVALUATED})


def canonical(obj) -> bytes:
    """The bytes the server sends as text content (and the shape of structuredContent): the measure of D-5."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _bound(args: dict) -> None:
    try:
        n = len(canonical(args))
    except (TypeError, ValueError, OverflowError):
        _fail('P3_PLAN_INPUT_INVALID', 'arguments must contain finite JSON values only', 'input')
    if n > MAX_REQUEST_BYTES:
        _fail('P3_PLAN_INPUT_INVALID', f'MCP arguments are {n} bytes; the limit is {MAX_REQUEST_BYTES}', 'input',
              size_bytes=n, limit_bytes=MAX_REQUEST_BYTES)


def _printer(printer, input_profile, fn, *a, **k):
    """Run a printer; its error passes through unchanged plus printer and input profile (§2 row 1)."""
    try:
        return fn(*a, **k)
    except ERRORS as e:
        d = e.diagnostic()
        d.update(printer=printer, input_profile=input_profile)
        raise PlanFailure(d) from e


def _limit(payload: dict, printer: str) -> dict:
    """512 KiB per SVG, 2 MiB per response; over a limit nothing partial is returned (D-6)."""
    svgs = [(p['name'], p['svg']) for p in payload.get('panels', [])]+([('index', payload['index']['svg'])] if 'index' in payload else [])
    for name, svg in svgs:
        n = len(svg.encode('utf-8'))
        if n > MAX_SVG_BYTES:
            _fail('P3_PLAN_SVG_TOO_LARGE', f'{name}.svg is {n} bytes; the limit is {MAX_SVG_BYTES}; '+HINT, 'output',
                  printer=printer, input_profile=payload.get('profile'), panel=name, size_bytes=n, limit_bytes=MAX_SVG_BYTES, hint=HINT)
    n = len(canonical(payload))
    if n > MAX_RESPONSE_BYTES:
        _fail('P3_PLAN_RESPONSE_TOO_LARGE', f'the response is {n} bytes; the limit is {MAX_RESPONSE_BYTES}; '+HINT, 'output',
              printer=printer, input_profile=payload.get('profile'), panels=len(payload.get('panels', [])), size_bytes=n,
              limit_bytes=MAX_RESPONSE_BYTES, hint=HINT)
    return payload


def plan_source(context: Any, plan_id: Any, printer: Any, **options) -> dict:
    """cube_plan_source: the printer's input document from a binding context, exactly as `from-plan` writes it."""
    options = {k: v for k, v in options.items() if v is not None}
    _bound({'context': context, 'plan_id': plan_id, 'printer': printer, **options})
    if printer == 'vpsequence':
        _fail('P3_PLAN_SOURCE_UNSUPPORTED', 'VP-08 sequence sources are declared directly; there is no from-plan for VP-08 '
              '(G6 D-7). Pass the sequence source to cube_plan_views with view cube.sequence.', 'input', printer=printer)
    if printer not in SOURCE_OPTIONS:
        _fail('P3_PLAN_ARGUMENT_INVALID', 'printer must be vpmigration, vpaxes or vpsequence', 'input')
    extra = set(options)-SOURCE_OPTIONS[printer]
    if extra:
        _fail('P3_PLAN_ARGUMENT_INVALID', f'{printer} from-plan takes no option '+', '.join(sorted(extra)), 'input', printer=printer)
    api = vp07 if printer == 'vpmigration' else vp09
    return _limit(_printer(printer, options.get('profile'), api.source, context, plan_id, **options), printer)


def plan_views(source: Any, view: Any, granularity: Any, **options) -> dict:
    """cube_plan_views: panels, index and report in memory; the view selects the printer."""
    options = {k: v for k, v in options.items() if v is not None}
    _bound({'source': source, 'view': view, 'granularity': granularity, **options})
    if view not in VIEWS:
        _fail('P3_PLAN_VIEW_UNKNOWN', f'view {view!r} is not one of '+', '.join(VIEWS), 'input')
    printer = VIEWS[view]
    fmt = source.get('format') if isinstance(source, dict) else None
    owner = {VP07_SOURCE: ('vpmigration', 'vpaxes'), VP08_SOURCE: ('vpsequence',), VP09_INPUT: ('vpaxes',)}.get(fmt)
    if owner is not None and printer not in owner:      # a source of another printer; anything else the printer judges (MP-2)
        _fail('P3_PLAN_ARGUMENT_INVALID', f'view {view} needs a {printer} source; got a {owner[0]} source ({fmt})', 'input', printer=printer)
    extra, missing = set(options)-OPTIONS[view], REQUIRED[view]-set(options)
    if extra or missing:
        _fail('P3_PLAN_ARGUMENT_INVALID', f'view {view} takes '+(', '.join(sorted(OPTIONS[view] | {'granularity'})))
              + (f'; unexpected: {", ".join(sorted(extra))}' if extra else '')+(f'; missing: {", ".join(sorted(missing))}' if missing else ''),
              'input', printer=printer)
    prof = source.get('profile')
    if printer == 'vpmigration':
        res = _printer(printer, prof, vp07.views, source, view, granularity, options['partition'], options.get('lens'),
                       options.get('locale'), options.get('hide_ledger', False))
    elif printer == 'vpsequence':
        res = _printer(printer, prof, vp08.views, source, view, granularity, options.get('partition', 'trigger'), options.get('overflow', 'summarize'))
    else:
        res = _printer(printer, prof, vp09.views, source, view, granularity, options['rows'], options['cols'],
                       options.get('hide_empty'), options.get('locale'))
    return _limit(res, printer)


def plan_check(result: Any) -> dict:
    """cube_plan_check: the checks of check-panels on a plan-views result held in memory."""
    _bound({'result': result})
    printer = result.get('printer') if isinstance(result, dict) else None
    if printer not in PRINTERS:
        _fail('P3_PLAN_ARGUMENT_INVALID', 'result must be a cube_plan_views result (printer vpmigration, vpsequence or vpaxes)', 'input')
    api = {'vpmigration': vp07, 'vpsequence': vp08, 'vpaxes': vp09}[printer]
    return {**_printer(printer, result.get('profile'), api.check, result), 'printer': printer}


def _display_options() -> dict:
    from vpmigration.locale import PINNED
    out = {k: dict(v) for k, v in DISPLAY_OPTIONS.items()}
    for v in out.values():
        v['locale'] = sorted(PINNED)
    out['note'] = 'display text only; IDs, method IDs, decl: references and report keys are never translated; en is the identity'
    return out


def capabilities() -> dict:
    """Plan-view section of the local surface (G6 §1.5): tools, views, printer profiles, limits."""
    return {
        'tools': list(TOOLS),
        'views': dict(VIEWS),
        'printers': {'vpmigration': {'profiles': list(c07.PROFILES), 'default_profile': 'context-dependent (as CLI from-plan)'},
                     'vpsequence': {'profiles': [c08.PROFILE], 'source': 'declared directly; cube_plan_source unsupported'},
                     'vpaxes': {'profiles': list(c09.PROFILES), 'default_profile': c09.PROFILE}},
        'display_options': _display_options(),
        'limits': {'max_request_bytes': MAX_REQUEST_BYTES, 'max_svg_bytes': MAX_SVG_BYTES, 'max_response_bytes': MAX_RESPONSE_BYTES,
                   'over_limit': 'FAIL with P3_PLAN_SVG_TOO_LARGE / P3_PLAN_RESPONSE_TOO_LARGE; never truncated'},
        'files_returned_inline': True,
        'filesystem_side_effects': False,
        'remote_available': False,
        'cli_parity': 'byte_identical_files',
        'source_warrant': 'declared_unverified',
        'p1_validation_included': False,
    }
