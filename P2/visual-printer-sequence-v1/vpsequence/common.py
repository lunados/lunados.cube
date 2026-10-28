"""VP-08 shared helpers. Imports frozen VP-01…VP-06 primitives (via the VP-07 path setup); never edits them."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
_VP07 = HERE.parent/'visual-printer-migration-v1'
if not _VP07.is_dir():
    raise RuntimeError('P2 baseline missing: visual-printer-migration-v1')
if str(_VP07) not in sys.path:
    sys.path.append(str(_VP07))

from vpmigration import common as _c  # noqa: E402  (path setup for VP-01…VP-06; helpers only)
from vpmigration.common import (Printer, VP01Error, NS, add, line, rect, text, excerpt, cjson, source_digest, fmt,  # noqa: E402,F401
                                no_active_content, encode, sha_bytes, sha_json, KEY, LEVELS, NOT_EVALUATED, STROKE, INK, MUTED,
                                MAX_INPUT_BYTES)

PROFILE = 'P2-VP-SEQUENCE/0.8.0'
ERROR_FORMAT = 'aiaeao.cube.vp08-diagnostic/1'
TRIGGER_KINDS = ('ui_button', 'schedule', 'webhook', 'cli', 'event', 'manual')
MESSAGE_KINDS = ('call', 'return', 'async', 'self')
FRAGMENTS = ('alt', 'opt', 'loop')
MAX_DEPTH = 2  # D-5
# participants / messages / fragment depth per drawn window (D-6)
BUDGET = {'overview': (4, 8, 1), 'standard': (7, 16, 2), 'detail': (10, 30, 2)}
LIMITS = {'participants': 40, 'triggers': 100, 'messages_per_trigger': 300, 'messages': 3000}  # SS-5
OVERFLOWS = ('summarize', 'reject')


class VP08Error(ValueError):
    """Machine-readable VP-08 display error; never a P1 semantic verdict."""

    def __init__(self, code, message, stage='input'):
        super().__init__(message)
        self.code = code
        self.stage = stage

    def diagnostic(self):
        return {'format': ERROR_FORMAT, 'profile': PROFILE, 'status': 'FAIL', 'code': self.code, 'stage': self.stage,
                'message': str(self), 'files_written': False, 'epistemic_warrant': 'NOT_EVALUATED',
                'current_authority': 'NOT_EVALUATED', 'canonical_admission': 'NOT_EVALUATED'}


def need(ok, code, message, stage='input'):
    if not ok:
        raise VP08Error(code, message, stage)


def keys(obj, required, optional, code, context):
    need(isinstance(obj, dict), code, context+' must be an object')
    missing = set(required)-set(obj)
    extra = set(obj)-set(required)-set(optional)
    need(not missing, code, context+' missing fields: '+','.join(sorted(missing)))
    need(not extra, code, context+' unexpected fields: '+','.join(sorted(extra)))


def clean(value, maxlen):
    return isinstance(value, str) and bool(value) and len(value) <= maxlen and not any(ord(c) < 32 for c in value)


def stable_id(value):
    return isinstance(value, str) and KEY.fullmatch(value) is not None


def scoped_ref(value):
    return clean(value, 180) and value.startswith(('decl:', 'fixture:'))


def _vp07(fn, *a, **k):
    """Run a VP-07 I/O helper and translate its error codes into VP-08 codes."""
    try:
        return fn(*a, **k)
    except _c.VP07Error as e:
        raise VP08Error(e.code.replace('VP07_', 'VP08_'), str(e), e.stage) from e


def load_json(path, code='VP08_INPUT_INVALID'):
    return _vp07(_c.load_json, path, code.replace('VP08_', 'VP07_'))


def fs_isdir(d):
    return _c.fs_isdir(d)


def fs_names(d):
    return _c.fs_names(d)


def fs_bytes(d, name, code='VP08_INPUT_INVALID'):
    return _vp07(_c.fs_bytes, d, name, code.replace('VP08_', 'VP07_'))


def fs_json(d, name, code='VP08_INPUT_INVALID'):
    return _vp07(_c.fs_json, d, name, code.replace('VP08_', 'VP07_'))


def publish_dir(files, output_dir):
    return _vp07(_c.publish_dir, files, output_dir)


def write_new(path, data):
    return _vp07(_c.write_new, path, data)


def wrap_words(s, width):
    """Wrap on spaces without truncation; an overlong word is split, never cut."""
    out, cur = [], ''
    for w in s.split(' '):
        while len(w) > width:
            if cur:
                out.append(cur); cur = ''
            out.append(w[:width]); w = w[width:]
        if cur and len(cur)+1+len(w) > width:
            out.append(cur); cur = w
        else:
            cur = (cur+' '+w) if cur else w
    if cur:
        out.append(cur)
    return out or ['']


def two_lines(s, width):
    """SM-2: at most two lines, never truncated; widen the line when two lines at `width` do not suffice."""
    w = max(8, width)
    while True:
        lines = wrap_words(s, w)
        if len(lines) <= 2:
            return lines
        w += 4


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)
