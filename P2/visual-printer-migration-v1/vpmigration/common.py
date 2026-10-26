"""VP-07 shared helpers. Imports frozen VP-01…VP-06 code; never edits it."""
from __future__ import annotations
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
P2 = HERE.parent
for _d in ('visual-printer-release-v1', 'visual-printer-conformance-v1', 'visual-printer-granularity-v1', 'visual-printer-2d-lab'):
    _p = str(P2/_d)
    if not (P2/_d).is_dir():
        raise RuntimeError('frozen P2 baseline missing: '+_d)
    if _p not in sys.path:
        sys.path.append(_p)

from vp2d.printer import Printer, PrintError as VP01Error, NS, add, line, rect, text  # noqa: E402
from vpviews.printer import wrap_label, excerpt  # noqa: E402
from vplenses.printer import source_digest, cjson, PROFILES as LENSES  # noqa: E402

PROFILE = 'P2-VP-MIGRATION/0.7.0'
ERROR_FORMAT = 'aiaeao.cube.vp07-diagnostic/1'
MAX_INPUT_BYTES = 2*1024*1024
KEY = re.compile(r'^[A-Za-z][A-Za-z0-9_.:-]{0,99}$')
HEX64 = re.compile(r'^[0-9a-f]{64}$')
LEVELS = ('overview', 'standard', 'detail')
STYLES = ('solid', 'dashed', 'dotted', 'double')
DASH = {'dashed': '8 5', 'dotted': '2 4'}
STROKE = '#64748B'
INK = '#0F172A'
MUTED = '#475569'
NOT_EVALUATED = {'semantic_conformance': 'NOT_EVALUATED', 'epistemic_warrant': 'NOT_EVALUATED',
                 'current_authority': 'NOT_EVALUATED', 'canonical_admission': 'NOT_EVALUATED'}
FORBIDDEN_TAGS = {'script', 'foreignObject', 'image', 'use', 'animate', 'set', 'iframe', 'pattern'}


class VP07Error(ValueError):
    """Machine-readable VP-07 display error; never a P1 semantic verdict."""

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
        raise VP07Error(code, message, stage)


def keys(obj, required, optional, code, context):
    need(isinstance(obj, dict), code, context+' must be an object')
    missing = set(required)-set(obj)
    extra = set(obj)-set(required)-set(optional)
    need(not missing, code, context+' missing fields: '+','.join(sorted(missing)))
    need(not extra, code, context+' unexpected fields: '+','.join(sorted(extra)))


def clean(value, maxlen):
    return isinstance(value, str) and bool(value) and len(value) <= maxlen and not any(ord(c) < 32 for c in value)


def encode(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha_json(obj):
    return hashlib.sha256(cjson(obj).encode('utf-8')).hexdigest()


def load_json(path, code='VP07_INPUT_INVALID'):
    path = Path(path)
    try:
        need(path.stat().st_size <= MAX_INPUT_BYTES, code, 'input exceeds 2 MiB')
        raw = path.read_bytes().decode('utf-8')
    except VP07Error:
        raise
    except (OSError, UnicodeError) as e:
        raise VP07Error(code, 'input unreadable: '+str(e)) from e

    def pairs(items):
        d = {}
        for k, v in items:
            need(k not in d, code, 'duplicate JSON key: '+k)
            d[k] = v
        return d

    def nonfinite(v):
        raise VP07Error(code, 'nonfinite number: '+v)
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except VP07Error:
        raise
    except (ValueError, TypeError) as e:
        raise VP07Error(code, 'invalid JSON: '+str(e)) from e


def check_edge_styles(styles):
    """ES-1, ES-3: closed style set, one style per predicate, declared legend <= 40 chars."""
    need(isinstance(styles, list) and len(styles) <= 32, 'VP07_EDGE_STYLE', 'edge_styles must be an array of <= 32 entries')
    out = {}
    for s in styles:
        keys(s, ('predicate_id', 'style', 'legend'), (), 'VP07_EDGE_STYLE', 'edge style')
        need(clean(s['predicate_id'], 60), 'VP07_EDGE_STYLE', 'edge style predicate_id must be clean text <= 60')
        need(s['style'] in STYLES, 'VP07_EDGE_STYLE', 'style outside the closed set solid|dashed|dotted|double: '+repr(s['style']))
        need(clean(s['legend'], 40), 'VP07_EDGE_STYLE', 'legend must be declared clean text <= 40 chars')
        need(s['predicate_id'] not in out, 'VP07_EDGE_STYLE', 'predicate styled twice: '+s['predicate_id'])
        out[s['predicate_id']] = s
    return out


def no_active_content(root):
    for el in root.iter():
        tag = el.tag.rsplit('}', 1)[-1]
        if tag in FORBIDDEN_TAGS:
            return False
        for k, v in el.attrib.items():
            k2 = k.rsplit('}', 1)[-1].lower()
            if k2.startswith('on') or k2 == 'href' or 'url(' in str(v):
                return False
    return True


def style_line(el, style):
    if style in DASH:
        el.set('stroke-dasharray', DASH[style])


def double_of(parent, el, offset=3.0):
    """Second parallel line for style 'double' (geometry only, same colour)."""
    from xml.etree import ElementTree as ET
    x1, y1, x2, y2 = (float(el.get(k)) for k in ('x1', 'y1', 'x2', 'y2'))
    dx, dy = (0.0, offset) if y1 == y2 else (offset, 0.0) if x1 == x2 else (offset, offset)
    twin = ET.Element(el.tag, dict(el.attrib))
    for k, v in (('x1', x1+dx), ('y1', y1+dy), ('x2', x2+dx), ('y2', y2+dy)):
        twin.set(k, fmt(v))
    twin.set('data-vp07-double', 'twin')
    idx = list(parent).index(el)
    parent.insert(idx+1, twin)


def fmt(v):
    v = round(float(v), 2)
    return str(int(v)) if v == int(v) else str(v)


def publish_dir(files, output_dir):
    """Stage all files in one new sibling directory, publish by a single rename (VP-06 PE-5)."""
    out = Path(output_dir).expanduser().absolute()
    need(not out.exists(), 'VP07_OUTPUT_EXISTS', 'output directory already exists: '+str(out), 'output')
    stage = None
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.vp07-stage-', dir=out.parent))
        for name, data in files.items():
            (stage/name).write_bytes(data)
        need(not out.exists(), 'VP07_OUTPUT_EXISTS', 'output directory appeared while staging', 'output')
        os.rename(stage, out)
        stage = None
    except VP07Error:
        raise
    except OSError as e:
        raise VP07Error('VP07_OUTPUT_IO', str(e), 'output') from e
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
    return out


def write_new(path, data):
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            f.write(data)
    except FileExistsError as e:
        raise VP07Error('VP07_OUTPUT_EXISTS', 'output already exists: '+str(path), 'output') from e
    except OSError as e:
        raise VP07Error('VP07_OUTPUT_IO', str(e), 'output') from e
