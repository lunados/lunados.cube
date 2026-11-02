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
PROFILE_101 = 'P2-VP-CELLS/0.10.1'  # VP-10.1: selected by a declared axis_order (Q-2)
PROFILE_110 = 'P2-VP-CELLS/0.11.0'  # VP-10 0.11.0: statement sets without a plan (MILE-007)
BASE_PROFILE = P092
INPUT_FORMAT = 'aiaeao.cube.vp10-cells-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp10-cells-report/1'
ERROR_FORMAT = 'aiaeao.cube.vp10-diagnostic/1'
CTX_FORMATS = tuple(f'aiaeao.cube.binding-context/{n}' for n in (5, 6, 7, 8))
V8 = 'aiaeao.cube.binding-context/8'
MATRIX_FORMAT = 'aiaeao.cube.vp110-matrix-input/1'
SET_FORMAT = 'aiaeao.cube.statement-set/1'
RECORD_FORMAT = 'aiaeao.cube.projection-record/1'
STATES = ('marked', 'checked', 'unknown', 'hidden')
SCOPES = ('pair', 'row', 'column')
LOCALES = Path(__file__).resolve().parent/'locales'
LOCALE_PINNED = {'de': '73447ba2a023f9b1d1016d2ae017519ed2e46d84f5c782eb55650dd29fa3b831'}  # LC-1: reproducible from the code
LOCALE_PINNED_0101 = {'de': '653ad01c2335072659c81680ac14d1a6bb4d8c643677bb5a1ed8a62d609bdbc9'}
LOCALE_PINNED_0110 = {'de': '6b9c069098612059e05f5ef776d26c43f0d22c3c3ed8375ef7c85ecb5b77eac7'}


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


class OrderTexts(Texts):
    """VP-10.1 texts in their own pinned file, so the 0.10.0 locale (and its recorded digest) stays byte-identical."""

    def __init__(self, code=None):
        self.code = code or 'en'
        self.text = {}
        self.sha256 = None
        if code not in (None, 'en'):
            need(code in LOCALE_PINNED_0101, 'VP10_LOCALE_INVALID', f'locale must be one of en, {", ".join(sorted(LOCALE_PINNED_0101))}')
            raw = (LOCALES/f'{code}-0101.json').read_bytes()
            self.sha256 = hashlib.sha256(raw).hexdigest()
            need(self.sha256 == LOCALE_PINNED_0101[code], 'VP10_LOCALE_INVALID', f'locale file {code}-0101.json does not match its pin')
            self.text = json.loads(raw)['text']


class MatrixTexts(Texts):
    """VP-10 0.11.0 texts in their own pinned file; the 0.10.0 and 0.10.1 locale files stay byte-identical."""

    def __init__(self, code=None):
        self.code = code or 'en'
        self.text = {}
        self.sha256 = None
        if code not in (None, 'en'):
            need(code in LOCALE_PINNED_0110, 'VP10_LOCALE_INVALID', f'locale must be one of en, {", ".join(sorted(LOCALE_PINNED_0110))}')
            raw = (LOCALES/f'{code}-0110.json').read_bytes()
            self.sha256 = hashlib.sha256(raw).hexdigest()
            need(self.sha256 == LOCALE_PINNED_0110[code], 'VP10_LOCALE_INVALID', f'locale file {code}-0110.json does not match its pin')
            self.text = json.loads(raw)['text']
