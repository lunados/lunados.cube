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
P090, P091 = PROFILE, 'P2-VP-AXES/0.9.1'
PROFILES = (P090, P091)
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
CATALOG_ORDER = ('migrate.import/v1', 'migrate.rebuild/v1', 'migrate.retire/v1', 'migrate.rewrite/v1', 'migrate.reconfigure/v1')
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
CATALOG_SHA256 = '5e317bce914609f42bbcbe8b22edd2989a63247686de840faae63f686f6b4c49'  # pinned P1.11 catalog the IDs above come from (FM-1)
METHOD_PROFILE_REF = 'P1.11/migration-methods-v1'


class VP09Error(ValueError):
    """Machine-readable VP-09 display error; never a P1 semantic verdict."""

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
        raise VP09Error(code, message, stage)


def via07(fn, *a, code=None, **k):
    """Run VP-07 code; map its errors to VP-09 codes (code=None keeps the VP07_ suffix as VP09_)."""
    try:
        return fn(*a, **k)
    except _c.VP07Error as e:
        raise VP09Error(code or e.code.replace('VP07_', 'VP09_'), str(e), e.stage) from e


def load_json(path, code='VP09_INPUT_INVALID'):
    return via07(_c.load_json, path, code.replace('VP09_', 'VP07_'))


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


def kind_label(k):
    return KIND_LABEL.get(k, k)
