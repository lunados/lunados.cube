"""VP-11 shared helpers. Reuses the VP-09 (`vpaxes`) and VP-07 drawing helpers unchanged (imported, never edited)."""
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

from vpaxes.common import (VP09Error, NS, NOT_EVALUATED, INK, MUTED, add, line, rect, text, fmt, no_active_content,  # noqa: E402,F401
                           encode, sha_bytes, sha_json, cjson, wrap_sep, load_json, publish_dir, write_new)

PROFILE = 'P2-VP-INSTANCES/0.12.0'
VIEW = 'cube.instances'
INPUT_FORMAT = 'aiaeao.cube.vp11-instances-input/1'
REPORT_FORMAT = 'aiaeao.cube.vp11-instances-report/1'
ERROR_FORMAT = 'aiaeao.cube.vp11-diagnostic/1'
V9 = 'aiaeao.cube.binding-context/9'
SET_FORMAT = 'aiaeao.cube.statement-set/1'
RECORD_FORMAT = 'aiaeao.cube.conformance-record/1'
METHOD = 'analyze.trace-conformance/v1'
RESULT_SCHEMA = 'aiaeao.trace-conformance-result/v1'
CHECKS = ('exclusive', 'condition_order', 'join', 'split', 'merge')
FIT = {'exclusive': 'xs', 'condition_order': 'xs', 'merge': 'xm', 'split': 'ps', 'join': 'pj'}   # RC-3
ROLES = ('xs', 'xm', 'ps', 'pj')
PASS_VALUES = ('exclusive_one_path', 'condition_first_true', 'default_without_true', 'join_complete', 'join_waiting', 'split_complete',
               'merge_pass_through')
FAIL_VALUES = ('exclusive_two_paths', 'exclusive_no_path', 'default_with_true_condition', 'not_first_true', 'join_incomplete',
               'split_incomplete', 'merge_mismatch')
UNRESOLVED_VALUES = ('coverage_undeclared', 'conditions_unrecorded')
STATUS_OF = {**{v: 'PASS' for v in PASS_VALUES}, **{v: 'FAIL' for v in FAIL_VALUES}, **{v: 'UNRESOLVED' for v in UNRESOLVED_VALUES}}
LOCALES = Path(__file__).resolve().parent/'locales'
LOCALE_PINNED = {'de': 'fec3e6024fc9dff3fb9c562d6be400487190f565720eaf1480264d138c9d73bd'}  # LC-1: set from the committed file

# §3.1 value texts and §9 DR-3a…DR-7a fixed texts (English defaults; German in locales/de.json)
EN = {
    'value.exclusive_one_path': 'one path', 'value.exclusive_two_paths': 'more than one path for one activation', 'value.exclusive_no_path': 'no path',
    'value.condition_first_true': 'first true condition taken', 'value.default_without_true': 'default without true condition',
    'value.default_with_true_condition': 'default although a condition was true', 'value.not_first_true': 'not the first true condition',
    'value.join_complete': 'all inputs', 'value.join_waiting': 'waiting', 'value.join_incomplete': 'continued without all inputs',
    'value.split_complete': 'all outputs', 'value.split_incomplete': 'not all outputs', 'value.merge_pass_through': 'passed through',
    'value.merge_mismatch': 'inputs and outputs differ', 'value.coverage_undeclared': 'coverage missing',
    'value.conditions_unrecorded': 'condition outcomes not recorded',
    'check.exclusive': 'exclusive', 'check.condition_order': 'condition order', 'check.join': 'join', 'check.split': 'split', 'check.merge': 'merge',
    'state.checked': 'checked', 'state.violation': 'rule violation', 'state.not_checkable': 'not checkable', 'state.not_checked': 'not checked',
    'extra.paths': 'paths', 'extra.taken': 'taken', 'extra.first_true': 'first true', 'extra.missing': 'missing', 'extra.foreign': 'foreign',
    'extra.excess': 'excess', 'extra.undeclared': 'undeclared',
    'role.xs': 'exclusive split', 'role.xm': 'exclusive merge', 'role.ps': 'parallel split', 'role.pj': 'parallel join',
    'row.activation': 'activation {token}', 'row.order': 'order {n}', 'row.default': 'default', 'row.taken': 'taken', 'row.not_taken': 'not taken',
    'row.arrived': 'arrived', 'row.missing': 'missing', 'row.token': 'token {tokens}', 'row.no_token': 'no token',
    'row.foreign': 'token of instance {instance} present · not part ({token})',
    'frame.title': 'instance {instance}', 'frame.undeclared': 'instance undeclared',
    'model.title': 'process model · no trace', 'model.in': 'in {flows}', 'model.not_drawn': 'not drawn',
    'title': 'instances · {set_id}', 'subtitle': 'v9.4 · VP-11 0.12.0 · trace {set_id} · context {context_id} · display only, no verdict of its own',
    'header': 'CUBE.INSTANCES · DECLARED TRACE PER INSTANCE · verdicts read from lunados.lib records',
    'legend.title': 'LEGEND · declared display conventions · not a verdict',
    'legend.solid': 'solid mark = a token of this instance in the trace (taken, arrived, token)',
    'legend.dotted': 'dotted mark = no token of this instance in the trace (not taken, missing, no token)',
    'legend.dashed': 'dashed mark = a token of another instance on that flow; it is not part of this instance',
    'legend.hatch': 'hatched mark = rule violation, read from a FAIL record of lunados.lib analyze.trace-conformance/v1',
    'legend.records': 'Verdicts are read from lunados.lib records, not computed by the view; "not checked" = no record given.',
    'legend.started': 'A step counts as started only if a token on its flow shows it; the process model below carries no trace.',
    'legend.colour': 'States differ by text and line style, not by colour.',
    'footer': 'DISPLAY-ONLY · not an ACG validation, warrant or authority decision',
}


class VP11Error(VP09Error):
    """Machine-readable VP-11 display error; never a P1 semantic verdict."""

    def diagnostic(self):
        return {'format': ERROR_FORMAT, 'profile': PROFILE, 'status': 'FAIL', 'code': self.code, 'stage': self.stage, 'message': str(self)}


def need(ok, code, message, stage='input'):
    if not ok:
        raise VP11Error(code, message, stage)


class Texts:
    """VP-11 display texts: built-in English defaults or the pinned German locale file."""

    def __init__(self, code=None):
        self.code = code or 'en'
        self.text = {}
        self.sha256 = None
        if code not in (None, 'en'):
            need(code in LOCALE_PINNED, 'VP11_LOCALE_INVALID', f'locale must be one of en, {", ".join(sorted(LOCALE_PINNED))}')
            raw = (LOCALES/f'{code}.json').read_bytes()
            self.sha256 = hashlib.sha256(raw).hexdigest()
            need(self.sha256 == LOCALE_PINNED[code], 'VP11_LOCALE_INVALID', f'locale file {code}.json does not match its pin')
            self.text = json.loads(raw)['text']

    def t(self, key, **kw):
        s = self.text.get(key, EN[key])
        return s.format(**kw) if kw else s

    def record(self):
        return None if self.sha256 is None else {'code': self.code, 'sha256': self.sha256}
