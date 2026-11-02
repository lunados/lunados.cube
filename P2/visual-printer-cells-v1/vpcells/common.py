"""VP-10 shared helpers. Reuses VP-09 (`vpaxes`, 0.9.2) and VP-07 code unchanged (imported, never edited)."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
_VP09 = HERE.parent/'visual-printer-axes-v1'
if not _VP09.is_dir():
    raise RuntimeError('P2 baseline missing: visual-printer-axes-v1')
if str(_VP09) not in sys.path:
    sys.path.append(str(_VP09))

from vpaxes import common as _ax  # noqa: E402  (also puts VP-07 on the path)
from vpaxes.common import VP09Error, P092, NS, NOT_EVALUATED, encode, sha_bytes, sha_json, cjson, wrap_sep  # noqa: E402,F401

PROFILE = 'P2-VP-CELLS/0.10.0'
BASE_PROFILE = P092
INPUT_FORMAT = 'aiaeao.cube.vp10-cells-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp10-cells-report/1'
ERROR_FORMAT = 'aiaeao.cube.vp10-diagnostic/1'
CTX_FORMATS = tuple(f'aiaeao.cube.binding-context/{n}' for n in (5, 6, 7, 8))
V8 = 'aiaeao.cube.binding-context/8'
STATES = ('marked', 'checked', 'unknown', 'hidden')
SCOPES = ('pair', 'row', 'column')
LOCALES = Path(__file__).resolve().parent/'locales'
LOCALE_PINNED = {'de': '73447ba2a023f9b1d1016d2ae017519ed2e46d84f5c782eb55650dd29fa3b831'}  # LC-1: reproducible from the code


class VP10Error(VP09Error):
    """Machine-readable VP-10 display error; never a P1 semantic verdict."""

    def diagnostic(self):
        return {'format': ERROR_FORMAT, 'profile': PROFILE, 'status': 'FAIL', 'code': self.code, 'stage': self.stage, 'message': str(self)}


def need(ok, code, message, stage='input'):
    if not ok:
        raise VP10Error(code, message, stage)


class Texts:
    """VP-10 display texts: built-in English defaults or a pinned locale file (the VP-07.5 files stay untouched)."""

    def __init__(self, code=None):
        self.code = code or 'en'
        self.text = {}
        self.sha256 = None
        if code not in (None, 'en'):
            need(code in LOCALE_PINNED, 'VP10_LOCALE_INVALID', f'locale must be one of en, {", ".join(sorted(LOCALE_PINNED))}')
            raw = (LOCALES/f'{code}.json').read_bytes()
            self.sha256 = hashlib.sha256(raw).hexdigest()
            need(self.sha256 == LOCALE_PINNED[code], 'VP10_LOCALE_INVALID', f'locale file {code}.json does not match its pin')
            self.text = json.loads(raw)['text']

    def t(self, key, default, **kw):
        s = self.text.get(key, default)
        return s.format(**kw) if kw else s

    def record(self):
        return None if self.sha256 is None else {'code': self.code, 'sha256': self.sha256}
