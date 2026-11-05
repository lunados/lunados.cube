"""VP-12 shared helpers. Reuses VP-01…VP-07 code (imported, never edited)."""
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

from vpmigration.common import (Printer, NS, add, line, rect, text, excerpt, cjson, fmt, no_active_content, encode,  # noqa: E402,F401
                                sha_bytes, sha_json, KEY, LEVELS, NOT_EVALUATED, STROKE, INK, MUTED, DASH, UNASSIGNED, P078,
                                VP07Error, clean, publish_dir, write_new, fs_isdir, fs_names, fs_bytes, fs_json, load_json)

PROFILE = 'P2-VP-LANDSCAPE/0.12.0'  # default; byte-identical since VP-12.1
P0121 = 'P2-VP-LANDSCAPE/0.12.1'  # VP-12.1 (MILE-018 E18-1): VG anchor of the layer column, opt-in
PROFILES = (PROFILE, P0121)
COLUMN_ANCHOR = 'skeleton-shell.section'  # VP-12.1 D-1: UI anchor, no Cube statement
SOURCE_PROFILE = P078
INPUT_FORMAT = 'aiaeao.cube.vp12-landscape-input/1'
PANEL_INPUT = 'aiaeao.cube.vp12-panel-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp12-panel-report/1'
CHECK_FORMAT = 'aiaeao.cube.vp12-panel-check/1'
ERROR_FORMAT = 'aiaeao.cube.vp12-diagnostic/1'
VIEW = 'cube.landscape'
X_FAMILY = 'contract-pairs'
# §1.3 default columns: anchor families in Morphology reading order (Z module bodies, Z boundary, Y identity, Y resources)
FAMILIES = ('module-bodies', 'governance-boundary', 'identity-anchors', 'resource-objects')
MAX_COLUMNS, MAX_BANDS = 6, 4
BUDGET = {'overview': 5, 'standard': 8, 'detail': 12}   # nodes per column and band (§1.10)
PLACEMENT_DEFAULT = ('runs-on', 'hosted-by')
STATUS = ('derived', 'Morphology 01.3')                    # B10: Y × Z, T as declared steps
LOCALES = ('en', 'de')
ORIGIN_STYLE = {'declared': 'solid', 'derived': 'dashed', 'unknown': 'dotted', 'unbound': 'dotted'}


class VP12Error(ValueError):
    """Machine-readable VP-12 display error; never a P1 semantic verdict."""

    def __init__(self, code, message, stage='input'):
        super().__init__(message)
        self.code, self.stage = code, stage

    def diagnostic(self):
        return {'format': ERROR_FORMAT, 'profile': PROFILE, 'status': 'FAIL', 'code': self.code, 'stage': self.stage,
                'message': str(self), 'files_written': False, **NOT_EVALUATED}


def need(ok, code, message, stage='input'):
    if not ok:
        raise VP12Error(code, message, stage)


def diagnostic(e):
    """VP-07 errors of the reused source path keep their codes (§1.1)."""
    return e.diagnostic()


def locale_text(locale):
    need(locale in LOCALES, 'VP12_INPUT', 'locale must be one of '+', '.join(LOCALES))
    doc = json.loads((Path(__file__).parent/'locales'/f'{locale}.json').read_text('utf-8'))
    need(doc.get('format') == 'aiaeao.cube.vp12-locale/1' and doc.get('locale') == locale, 'VP12_INPUT', 'locale file malformed')
    return doc['text']
