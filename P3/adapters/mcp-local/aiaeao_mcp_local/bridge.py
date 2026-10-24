"""Transport-neutral, in-memory VP-06 bridge (local PoC-A, no new renderer).

No filesystem paths, URLs, processes or shell commands are accepted as tool args.
Source declarations remain declared_unverified; P1 is never invoked.
"""
from __future__ import annotations
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Prevent ordinary import caching from writing to source directories.
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
PRINTER = ROOT / 'P2' / 'visual-printer-release-v1'
if not PRINTER.is_dir():
    raise RuntimeError('Frozen VP-06 release is required as sibling P2 tree')
if str(PRINTER) not in sys.path:
    sys.path.insert(0, str(PRINTER))
from vpprint.core import PrintError, capabilities, make_job, render_job  # noqa: E402

# PoC-local safety limits; not a change to VP-06's on-disk input contract.
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_SVG_BYTES = 512 * 1024
TOOL_NAMES = ('cube_get_capabilities', 'cube_prepare_print',
              'cube_check_print', 'cube_render_svg')

class BridgeFailure(Exception):
    def __init__(self, diagnostic: dict):
        self.diagnostic = diagnostic
        super().__init__(diagnostic['code'] + ': ' + diagnostic['message'])


def _fail(code: str, message: str, stage='transport') -> None:
    raise BridgeFailure(PrintError(code, message, stage).diagnostic())


def _bound(obj: dict) -> None:
    if type(obj) is not dict:
        _fail('VP06_INPUT_INVALID', 'arguments must be a JSON object', 'input')
    try:
        encoded = json.dumps(obj, ensure_ascii=False, allow_nan=False,
                             separators=(',', ':'), sort_keys=True).encode('utf-8')
    except (TypeError, ValueError, OverflowError) as exc:
        _fail('VP06_INPUT_INVALID', 'arguments must contain finite JSON values only', 'input')
    if len(encoded) > MAX_REQUEST_BYTES:
        _fail('VP06_INPUT_TOO_LARGE', 'MCP arguments exceed 2 MiB', 'input')


def _run(fn, args: dict) -> dict:
    _bound(args)
    try:
        return fn()
    except BridgeFailure:
        raise
    except PrintError as exc:
        raise BridgeFailure(exc.diagnostic()) from exc


def get_capabilities() -> dict:
    def go():
        # The frozen card is intact in `core` and never mutated.
        return {'core': capabilities(), 'adapter': {
            'name': 'aiaeao-cube-mcp-local', 'version': 'P3-MCP-LOCAL/0.1.1',
            'transport': 'stdio', 'remote_available': False,
            'mcp_protocol_target': '2026-07-28',
            'sdk_major': 2, 'tools': list(TOOL_NAMES),
            'maximum_request_bytes': MAX_REQUEST_BYTES,
            'maximum_svg_bytes': MAX_SVG_BYTES,
            'source_warrant': 'declared_unverified',
            'p1_validation': False, 'filesystem_effects': False,
            'http_endpoint': False}}
    return _run(go, {})


def prepare_print(bundle: dict, lens: str, granularity: str,
                  overflow: str = 'summarize', focus: dict | None = None,
                  max_items: int | None = None,
                  max_edges: int | None = None) -> dict:
    args = dict(bundle=bundle, lens=lens, granularity=granularity,
                overflow=overflow, focus=focus,
                max_items=max_items, max_edges=max_edges)
    def go():
        # Validate untrusted budget types before core (bool is an int subclass).
        for k, n in (('max_items', max_items), ('max_edges', max_edges)):
            if n is not None and (type(n) is not int or n < 1):
                _fail('VP06_BUDGET_INCOMPATIBLE', k + ' must be positive integer', 'granularity')
        if focus is not None and (type(focus) is not dict or set(focus) != {'kind','id'}
                                   or focus.get('kind') not in ('node','edge','sample','metric')
                                   or type(focus.get('id')) is not str or not focus['id']):
            _fail('VP06_FOCUS_INVALID', 'focus must be {kind:node|edge|sample|metric,id:string}', 'input')
        return make_job(bundle, lens, granularity, overflow, focus, max_items, max_edges)
    return _run(go, args)


def check_print(job: dict) -> dict:
    def go():
        report, _ = render_job(job)
        return report
    return _run(go, {'job': job})


def _guard_svg(svg: bytes) -> None:
    if len(svg) > MAX_SVG_BYTES:
        _fail('VP06_OUTPUT_TOO_LARGE', 'SVG exceeds local MCP 512 KiB output ceiling', 'output')
    try:
        content = svg.decode('utf-8')
        # Avoid any markup declarations not expected in frozen VP-06 SVG output.
        lowered=content.lower()
        for token in ('<!doctype', '<!entity', '<?xml-stylesheet'):
            if token in lowered:
                _fail('VP06_UNSAFE_SVG', 'disallowed SVG markup declaration', 'output')
        root=ET.fromstring(svg)
        if root.tag != '{http://www.w3.org/2000/svg}svg':
            _fail('VP06_UNSAFE_SVG', 'SVG document root is not svg', 'output')
        forbidden={'script','foreignObject','image','use','iframe','animate','set','animateMotion','animateTransform'}
        for el in root.iter():
            local=el.tag.split('}')[-1] if isinstance(el.tag,str) else ''
            if local in forbidden:
                _fail('VP06_UNSAFE_SVG', 'active or externally referenceable SVG element', 'output')
            for key,value in el.attrib.items():
                key=key.split('}')[-1].lower()
                if key.startswith('on') or key in ('href', 'src') or 'url(' in value.lower():
                    _fail('VP06_UNSAFE_SVG', 'active SVG attribute or reference', 'output')
    except ET.ParseError:
        _fail('VP06_UNSAFE_SVG', 'invalid SVG XML', 'output')


def render_svg(job: dict) -> dict:
    def go():
        report,svg=render_job(job)
        _guard_svg(svg)
        if hashlib.sha256(svg).hexdigest()!=report['svg_sha256']:
            _fail('VP06_DIGEST_MISMATCH','SVG does not match report digest','output')
        return {'report':report,'artifact':{
            'media_type':'image/svg+xml',
            'encoding':'utf-8',
            'sha256':report['svg_sha256'],
            'byte_length':len(svg),
            'svg_text':svg.decode('utf-8')},
            'transport':'local_mcp_stdio',
            'source_status':'declared_unverified'}
    return _run(go, {'job':job})
