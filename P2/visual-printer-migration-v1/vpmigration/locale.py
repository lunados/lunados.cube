"""VP-07.5 / VP-09.2 display locales (C-12 a): pinned files, display text only.

`Locale.t(key, default, **kw)` returns the locale text or the built-in English default; the identity locale `en`
returns every default unchanged, so `--locale en` equals no locale (LC-1). IDs, method IDs and short names,
`decl:` references and report keys are never translated. `post(svg, kind)` replaces texts of the frozen
VP-04/VP-05/VP-06 printers by exact full-text matches (VP-07.5 D-3); a required entry that does not match is
an audit failure, never a silent mix.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from .common import VP07Error, need, NS, no_active_content

FORMAT = 'aiaeao.cube.p2-locale/1'
DIR = Path(__file__).resolve().parent/'locales'
PINNED = {  # LC-1: a picture's text is reproducible from the locale code
    'en': 'bf7202d635cfb1587d084e82f8f076d33a24689363b2243e51c126f7493dc251',
    'de': 'a5ef8f0f5865a2899605fefed58df5df9d6c7bf1af4cc5df1b3ef8a4774150de',
}
_CACHE = {}


class Locale:
    def __init__(self, data):
        self.code = data['locale']
        self.identity = bool(data.get('identity'))
        self.text = data.get('text', {})
        self.roles = data.get('step_roles', {})
        self.predicates = data.get('predicates', {})
        self.partitions = data.get('partitions', {})
        self.replace = [(re.compile(r['match']), r['replace'], tuple(r.get('required', []))) for r in data.get('replace', [])]
        self.sha256 = data['_sha256']

    def t(self, key, default, **kw):
        s = self.text.get(key, default) if not self.identity else default
        return s.format(**kw) if kw else s

    def role(self, role):
        return role if self.identity else self.roles.get(role, role)

    def pred(self, pid):
        return pid if self.identity else self.predicates.get(pid, pid)

    def missing_predicates(self, pids):
        return [] if self.identity else [p for p in dict.fromkeys(pids) if p not in self.predicates]

    def partition(self, name):
        return name if self.identity else self.partitions.get(name, name)

    def record(self):
        return {'code': self.code, 'sha256': self.sha256}

    def post(self, svg, kind, code='VP07_AUDIT'):
        """Exact replacement of frozen texts in a finished SVG (D-3); identity returns the bytes unchanged."""
        if self.identity or not self.replace:
            return svg
        root = ET.fromstring(svg)
        hits = [0]*len(self.replace)
        for t in root.iter(f'{{{NS}}}text'):
            if t.text is None:
                continue
            for k, (rx, rep, _) in enumerate(self.replace):
                m = rx.fullmatch(t.text)
                if m:
                    t.text = m.expand(rep)
                    hits[k] += 1
                    break
        for k, (rx, _, req) in enumerate(self.replace):
            need(kind not in req or hits[k] >= 1, code, f'locale {self.code}: required frozen text not found in {kind}: {rx.pattern}', 'audit')
        out = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
        need(no_active_content(ET.fromstring(out)), code, 'localized SVG contains active content', 'audit')
        return out


def load(code, err='VP07_LOCALE_INVALID'):
    """A pinned locale by code; None means the identity locale `en`."""
    code = 'en' if code is None else code
    need(isinstance(code, str) and code in PINNED, err, f'unknown locale {code!r}; available: '+', '.join(sorted(PINNED)))
    if code not in _CACHE:
        raw = (DIR/f'{code}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == PINNED[code], err, f'locale {code} does not match its pinned SHA-256')
        data = json.loads(raw)
        need(data.get('format') == FORMAT and data.get('locale') == code, err, f'locale {code} is not an {FORMAT} file')
        _CACHE[code] = Locale({**data, '_sha256': digest})
    return _CACHE[code]


def hide_flow_ledger(svg):
    """VP-07.5 (b) in cube.flow: drop the frozen edge-ledger block (exact header, then its lines up to the footer rule)."""
    root = ET.fromstring(svg)
    texts = list(root.iter(f'{{{NS}}}text'))
    head = [t for t in texts if t.text == 'DECLARATION LEDGER · each edge is a fixture assertion, not P1 proof']
    foot = [t for t in texts if t.text == 'DISPLAY-ONLY · not an ACG validation, warrant or authority decision']
    need(len(head) == 1 and len(foot) == 1, 'VP07_AUDIT', 'cube.flow ledger block not found exactly once (VP-07.5 D-3)', 'audit')
    y0, y1 = float(head[0].get('y')), float(foot[0].get('y'))
    drop = {id(t) for t in texts if y0 <= float(t.get('y', -1)) < y1-30}
    for parent in list(root.iter()):
        for ch in list(parent):
            if id(ch) in drop:
                parent.remove(ch)
    root.set('data-vp07-ledger-hidden', 'true')
    return ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
