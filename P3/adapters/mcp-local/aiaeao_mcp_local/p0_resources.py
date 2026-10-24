"""CP-001/G1: immutable, offline-only, allowlisted P0 resources.

P0 morphology is authoritative for its *documentary reference* content, NOT
external truth or authenticated referents. Public HTTPS URIs are identifiers,
not fetch targets. No network calls, files from clients or arbitrary paths.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

SNAPSHOT_ROOT = Path(__file__).resolve().parent.parent / 'p0_snapshot'
LOCK_FILE = SNAPSHOT_ROOT / 'lock.json'
PINNED_LOCK_SHA256 = 'cb259c5962a61c507ace6260d37ae364cf6658794a115052e3bc4fefdca477a1'
INDEX_URI = 'aiaeao://p0/resources/v1'

class P0ResourceError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f'{code}: {message}')


def _load_lock() -> dict[str, Any]:
    try:
        lock_bytes = LOCK_FILE.read_bytes()
    except OSError as exc:
        raise P0ResourceError('P0_LOCK_UNAVAILABLE', 'Pinned P0 resource catalogue unavailable') from exc
    if hashlib.sha256(lock_bytes).hexdigest() != PINNED_LOCK_SHA256:
        raise P0ResourceError('P0_LOCK_MISMATCH', 'P0 resource catalogue lock integrity check failed')
    lock = json.loads(lock_bytes.decode('utf-8'))
    if lock['format'] != 'aiaeao.cube.mcp-p0-pinned-lock/1':
        raise P0ResourceError('P0_LOCK_INVALID', 'Unexpected P0 resource catalogue format')
    return lock


def entries() -> tuple[dict[str, Any], ...]:
    """Return a stable, explicit list of pinned resources, excluding index."""
    result = _load_lock()['resources']
    uris = [e['uri'] for e in result]
    if uris != sorted(set(uris)):
        raise P0ResourceError('P0_LOCK_INVALID', 'P0 resources are not unique and ordered')
    return tuple(result)


def _content(entry: dict[str, Any]) -> bytes:
    relative = entry['path']
    if not isinstance(relative, str) or relative.startswith('/') or '\\' in relative or any(p in ('', '.', '..') for p in relative.split('/')):
        raise P0ResourceError('P0_LOCK_INVALID', 'Unsafe entry in signed resource catalogue')
    path = SNAPSHOT_ROOT.joinpath(*relative.split('/'))
    try:
        base = SNAPSHOT_ROOT.resolve(strict=True)
        target = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise P0ResourceError('P0_CONTENT_UNAVAILABLE', 'Pinned P0 resource unavailable') from exc
    if not target.is_relative_to(base) or path.is_symlink():
        raise P0ResourceError('P0_PATH_INVALID', 'Resource is not a regular pinned snapshot')
    try:
        size = target.stat().st_size
        if size != entry['bytes'] or size > 1024 * 1024:
            raise P0ResourceError('P0_CONTENT_MISMATCH', 'Pinned P0 resource size mismatch')
        data = target.read_bytes()
    except OSError as exc:
        raise P0ResourceError('P0_CONTENT_UNAVAILABLE', 'Pinned P0 resource unavailable') from exc
    if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise P0ResourceError('P0_CONTENT_MISMATCH', 'Pinned P0 resource checksum mismatch')
    return data


def catalog() -> dict[str, Any]:
    """Source and digest information, without local paths or unrelated data."""
    data = _load_lock()
    resources = [{k:v for k,v in e.items() if k != 'path'} for e in entries()]
    return {'format':'aiaeao.cube.mcp-p0-resources/1',
            'reference_version':'v9.4', 'domain':'P0',
            'snapshot_lock_sha256': PINNED_LOCK_SHA256,
            'verified_repository_commit': data['verified_main_commit'],
            'offline': True, 'source_warrant':'canonical_documentary_reference_only',
            'resources':resources}


def read_bytes(uri: str) -> bytes:
    """Accept only known exact URIs. HTTPS URIs never trigger HTTP requests."""
    if type(uri) is not str:
        raise P0ResourceError('P0_URI_INVALID','P0 URI must be an exact registered string')
    if uri == INDEX_URI:
        return (json.dumps(catalog(), sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    for entry in entries():
        if entry['uri'] == uri:
            return _content(entry)
    raise P0ResourceError('P0_URI_NOT_FOUND', 'Requested P0 URI is not in the pinned allowlist')


def read_text(uri: str) -> str:
    """Byte-preserving UTF-8 conversion; no newline/unicode normalization."""
    data = read_bytes(uri)
    try:
        return data.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise P0ResourceError('P0_INVALID_UTF8','Pinned P0 resource is not valid UTF-8') from exc


def verify_snapshot() -> dict[str, Any]:
    """Verify the entire snapshot, including the root manifest's cross-links."""
    listed = entries()
    total = 0
    for entry in listed:
        data = _content(entry)
        data.decode('utf-8', errors='strict')
        total += len(data)
    manifest = json.loads(read_text('https://cube.lunados.net/manifest.json'))
    for entry in listed:
        if entry['path'] == 'manifest.json':
            continue
        matching = [v for v in manifest['assets'].values() if
                    v.get('href') == entry['uri']]
        if len(matching) != 1 or matching[0]['sha256'] != entry['sha256'] or matching[0]['bytes'] != entry['bytes']:
            raise P0ResourceError('P0_MANIFEST_MISMATCH', 'Pinned P0 item differs from canonical root manifest')
    return {'status':'PASS','resources':len(listed),'total_content_bytes':total,
            'reference_version':'v9.4','lock_sha256':PINNED_LOCK_SHA256}


def register_resources(mcp: Any) -> None:
    """Register fixed URI resources using the official MCPServer.resource API."""
    # Per-resource meta announces verifiable content digest at discovery time.
    for entry in entries():
        resource_uri = entry['uri']
        description = ('Pinned offline P0 v9.4 reference; SHA-256: ' + entry['sha256'] +
                       '. Read-only; no HTTP retrieval, truth/admission, or authorization.')
        def factory(uri: str):
            def resource_text() -> str:
                return read_text(uri)
            return resource_text
        mcp.resource(resource_uri, name='p0_' + entry['path'].replace('/','_').replace('.','_'),
                     title=entry['path'], description=description,
                     mime_type=entry['mime_type'],
                     meta={'sha256':entry['sha256'],'bytes':entry['bytes'],
                           'source_uri':resource_uri,'reference_version':'v9.4',
                           'source_role':'read_only_offline_snapshot'})(factory(resource_uri))
    mcp.resource(INDEX_URI, name='p0_resource_index', title='P0 pinned resource index',
                 description='P0 canonical resource URI, byte count and SHA-256 catalogue; offline. '
                             'Contains snapshot lock hash; no validation or online calls.',
                 mime_type='application/json')(lambda: read_text(INDEX_URI))
