"""VP-09 shared helpers. Reuses VP-01…VP-07 code (imported, never edited)."""
from __future__ import annotations
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
_VP07 = HERE.parent/'visual-printer-migration-v1'
if not _VP07.is_dir():
    raise RuntimeError('P2 baseline missing: visual-printer-migration-v1')
if str(_VP07) not in sys.path:
    sys.path.append(str(_VP07))

from vpmigration import common as _c  # noqa: E402
from vpmigration.common import (Printer, NS, add, line, rect, text, excerpt, cjson, fmt, no_active_content, encode,  # noqa: E402,F401
                                sha_bytes, sha_json, KEY, LEVELS, NOT_EVALUATED, STROKE, INK, MUTED, P071, P072)

PROFILE = 'P2-VP-AXES/0.9.0'  # base profile: default of from-plan and of every 0.9.0 code path (VP-09.1 D-1)
P090, P091, P092 = PROFILE, 'P2-VP-AXES/0.9.1', 'P2-VP-AXES/0.9.2'
PROFILES = (P090, P091, P092)
V91UP = (P091, P092)  # profiles with the VP-09.1 F axes and binding ledger (0.9.2 includes 0.9.1, VP-09.2 §1)
ERROR_FORMAT = 'aiaeao.cube.vp09-diagnostic/1'
INPUT_FORMAT = 'aiaeao.cube.vp09-axes-input/1'
AXES = ('X', 'Y:kind', 'Y:referent', 'Z:kind', 'Z:referent', 'T', 'F')
RESERVED = ('M', 'O')
PAIRS = ({'Z', 'T'}, {'F', 'Z'}, {'Y', 'T'}, {'F', 'T'}, {'X'}, {'Y', 'Z'}, {'X', 'Z'})  # D-2, field-test priority
# rows / columns / visible entries per cell (D-7, D-8)
BUDGET = {'overview': (8, 4, 2), 'standard': (14, 6, 3), 'detail': (24, 8, 6)}
X_DIMS = (('epistemology', 'Ψ', 'Epistemology'), ('governance', 'Γ', 'Governance'), ('semantics', 'Σ', 'Semantics'),
          ('execution', 'Ξ', 'Execution'), ('provenance', 'Π', 'Provenance'))
LENS_OF = {d: 'cube.lens.'+d for d, _, _ in X_DIMS}
# Morphology v9.4 §3.2 declared reading order of kinds (AX-3)
KIND_ORDER = {
    'Y': ['Actor', 'RoleBinding', 'Principal', 'SessionBinding', 'CapabilityProfile', 'AdaptationProfile',
          'Source', 'Resource', 'Content', 'Revision', 'Artifact', 'Evidence', 'Cache', 'WorkItem', 'Execution', 'Outcome', 'Annotation'],
    'Z': ['Core', 'Connector', 'Toolbox', 'Tool', 'Adapter', 'Integration', 'Runtime', 'Provider', 'ThirdPartyDependency'],
}
KIND_LABEL = {'ThirdPartyDependency': 'Third-party Dependency', 'RoleBinding': 'Role Binding', 'SessionBinding': 'Session Binding',
              'CapabilityProfile': 'Capability Profile', 'AdaptationProfile': 'Adaptation Profile', 'WorkItem': 'Work Item'}
CATALOG_ORDER = _c.METHOD_CATALOG  # VP-07.3 D-6: one P2 copy of the P1.11 catalog IDs, kept in vpmigration
SEMREF = re.compile(r'^([XYZ]):[^:]+:([A-Za-z]+)\[')
RULES = {
    frozenset({'Z', 'T'}): 'cell lists declared dependencies naming the row referent that hold in the column step',
    frozenset({'Y', 'T'}): 'cell lists declared dependencies naming the referent that hold in the step, plus retired/introduced markers of transitions at that step',
    frozenset({'Y', 'Z'}): 'cell lists declared dependencies between the two referents (either direction), with predicate',
    frozenset({'X'}): 'cell lists items carrying declared facets in both lenses (diagonal: facets of that lens)',
    frozenset({'X', 'Z'}): 'cell lists declared facet notes of the lens on the component or on dependencies naming it',
    frozenset({'F', 'Z'}): 'cell lists declared method bindings of the method that name the component (owner and role)',
    frozenset({'F', 'T'}): 'cell lists declared method bindings of the method on transitions at the step or dependencies ending there',
}
# VP-09.1 (0.9.1): F × Y joins the pair list (FP-1); F × T places dependency bindings by the declared successor (D-3)
PAIRS_091 = PAIRS+({'F', 'Y'},)
RULES_091 = dict(RULES)
RULES_091[frozenset({'F', 'Z'})] = 'cell lists declared method bindings of the method that name the component (owner · role)'
RULES_091[frozenset({'F', 'Y'})] = 'cell lists declared method bindings of the method that name the identity or resource (owner · role)'
RULES_091[frozenset({'F', 'T'})] = ('cell lists declared method bindings of the method on transitions at the step, or on dependencies '
                                    'at the first declared step of their successor (else their own last step)')
# VP-09.2 (0.9.2): Y × Y joins the pair list (directed, D-2); F × T entries carry their arguments (D-3)
PAIRS_092 = PAIRS_091+({'Y'},)
RULES_092 = dict(RULES_091)
RULES_092[frozenset({'F', 'T'})] = RULES_091[frozenset({'F', 'T'})]+', with arguments'
RULES_092[frozenset({'Y'})] = ('cell lists declared dependencies from the row identity or resource (subject) to the column identity or '
                               'resource (object), with predicate')
RULE_KEYS = {frozenset({'Z', 'T'}): 'Z|T', frozenset({'Y', 'T'}): 'Y|T', frozenset({'Y', 'Z'}): 'Y|Z', frozenset({'X'}): 'X',
             frozenset({'X', 'Z'}): 'X|Z', frozenset({'F', 'Z'}): 'F|Z', frozenset({'F', 'Y'}): 'F|Y', frozenset({'F', 'T'}): 'F|T',
             frozenset({'Y'}): 'Y'}  # keys of the VP-07.5 locale files (D-6)
# FA-1: catalog role order of the pinned P1.11 catalog (verified against its file in the tests)
ROLE_ORDER = {'migrate.import/v1': ('source', 'target'), 'migrate.rebuild/v1': ('target',), 'migrate.retire/v1': ('retired',),
              'migrate.rewrite/v1': ('dependant', 'new_object'), 'migrate.reconfigure/v1': ('target',)}
HIDE_EMPTY = ('rows', 'cols', 'both')
CATALOG_SHA256 = _c.METHOD_CATALOG_SHA256  # pinned P1.11 catalog the IDs above come from (FM-1)
METHOD_PROFILE_REF = _c.METHOD_PROFILE_REF


class VP09Error(ValueError):
    """Machine-readable VP-09 display error; never a P1 semantic verdict."""

    def __init__(self, code, message, stage='input'):
        super().__init__(message)
        self.code = code
        self.stage = stage

    def diagnostic(self):
        d = {'format': ERROR_FORMAT, 'profile': PROFILE, 'status': 'FAIL', 'code': self.code, 'stage': self.stage,
             'message': str(self), 'files_written': False, 'epistemic_warrant': 'NOT_EVALUATED',
             'current_authority': 'NOT_EVALUATED', 'canonical_admission': 'NOT_EVALUATED'}
        if getattr(self, 'input_profile', None):  # VP-09.2 D-8: 0.9.2 inputs only; 0.9.0 / 0.9.1 error output unchanged
            d.update(profile=self.input_profile, printer_profile=PROFILE)
        return d


def tag_profile(fn, profile_of):
    """VP-09.2 (i): a VP09Error raised for a 0.9.2 input names that profile (D-8)."""
    import functools

    @functools.wraps(fn)
    def wrapped(*a, **k):
        try:
            return fn(*a, **k)
        except VP09Error as e:
            try:
                p = profile_of(*a, **k)
            except Exception:  # noqa: BLE001 - the profile probe never masks the original error
                p = None
            if p == P092 and not getattr(e, 'input_profile', None):
                e.input_profile = p
            raise
    return wrapped


def need(ok, code, message, stage='input'):
    if not ok:
        raise VP09Error(code, message, stage)


def via07(fn, *a, code=None, **k):
    """Run VP-07 code; map its errors to VP-09 codes (code=None keeps the VP07_ suffix as VP09_)."""
    try:
        return fn(*a, **k)
    except _c.VP07Error as e:
        raise VP09Error(code or e.code.replace('VP07_', 'VP09_'), str(e), e.stage) from e


def load_json(path, code='VP09_INPUT_INVALID'):
    return via07(_c.load_json, path, code.replace('VP09_', 'VP07_'))


def fs_isdir(d):
    return _c.fs_isdir(d)


def fs_names(d):
    return _c.fs_names(d)


def fs_bytes(d, name, code='VP09_INPUT_INVALID'):
    return via07(_c.fs_bytes, d, name, code.replace('VP09_', 'VP07_'))


def fs_json(d, name, code='VP09_INPUT_INVALID'):
    return via07(_c.fs_json, d, name, code.replace('VP09_', 'VP07_'))


def publish_dir(files, output_dir):
    return via07(_c.publish_dir, files, output_dir)


def write_new(path, data):
    return via07(_c.write_new, path, data)


def wrap_words(s, width):
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


SEPS = '-_/.:·'


def wrap_sep(s, width):
    """VP-09.2 WR-1 (D-5): break at spaces and after `- _ / . : ·`; a piece longer than a line is shortened with `…`.
    Returns (lines, shortened); the caller keeps the full text in `<title>` and the ledger. Used only by 0.9.2."""
    pieces, cur = [], ''
    for ch in s:
        cur += ch
        if ch == ' ' or ch in SEPS:
            pieces.append(cur); cur = ''
    if cur:
        pieces.append(cur)
    out, line_, short = [], '', False
    for pc in pieces:
        if len(line_)+len(pc.rstrip()) <= width:
            line_ += pc
            continue
        if line_.strip():
            out.append(line_.rstrip()); line_ = ''
        if len(pc.rstrip()) > width:
            out.append(pc.rstrip()[:width-1]+'…'); short = True
        else:
            line_ = pc
    if line_.strip():
        out.append(line_.rstrip())
    return out or [''], short


def kind_label(k):
    return KIND_LABEL.get(k, k)
