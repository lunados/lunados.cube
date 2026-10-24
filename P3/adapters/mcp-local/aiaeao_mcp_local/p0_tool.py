"""CP-001/G1.1: tool-only MCP host compatibility for pinned P0 Resources.

The canonical surface remains MCP Resources. This bounded read-only tool
reuses *exactly the same locked snapshots and SHA-256-verifying read_bytes*
for MCP bridges that forward tools but not resources. No network or FS paths
are accepted. byte_offset and next_offset refer to UTF-8 byte positions.
"""
from __future__ import annotations
import hashlib
from typing import Any
from . import bridge, p0_resources as p0

FORMAT = 'aiaeao.cube.mcp-p0-reference-page/1'
DEFAULT_PAGE_BYTES = 8192
MAX_PAGE_BYTES = 32768


def _error(code: str, message: str) -> None:
    raise bridge.BridgeFailure({'code':code,'message':message,'stage':'p0_reference','status':'FAIL'})


def read_reference(uri: str, offset: int = 0, max_bytes: int = DEFAULT_PAGE_BYTES) -> dict[str, Any]:
    """Return byte-faithful UTF-8 page + pinned full-file SHA-256 or a diagnostic.

    The response never includes a local path and never returns more than 32 KiB
    of original reference text. Query strings / aliases / external URLs fail.
    """
    if type(uri) is not str or not uri or len(uri.encode('utf-8')) > 512:
        _error('P0_URI_INVALID','URI must be an exact registered P0 reference URI')
    if type(offset) is not int or offset < 0:
        _error('P0_OFFSET_INVALID','offset must be a non-negative UTF-8 byte offset')
    if type(max_bytes) is not int or not 4 <= max_bytes <= MAX_PAGE_BYTES:
        _error('P0_PAGE_LIMIT_INVALID','max_bytes must be an integer from 4 through 32768')
    try:
        original = p0.read_bytes(uri)  # verifies allowlist, signed lock and source digest
    except p0.P0ResourceError as exc:
        _error(exc.code, exc.message)
    if offset > len(original):
        _error('P0_OFFSET_INVALID','offset is beyond the end of the pinned reference')
    if offset < len(original) and (original[offset] & 0xC0) == 0x80:
        _error('P0_OFFSET_INVALID','offset splits a UTF-8 encoded character')

    end = min(len(original), offset + max_bytes)
    while True:
        try:
            content = original[offset:end].decode('utf-8', 'strict')
            break
        except UnicodeDecodeError as exc:
            if exc.reason != 'unexpected end of data' or end <= offset:
                _error('P0_INVALID_UTF8','Pinned reference is not valid UTF-8 at requested boundary')
            end -= 1
    if offset < len(original) and end == offset:
        _error('P0_PAGE_LIMIT_INVALID','Page budget cannot include one whole UTF-8 character')

    digest = hashlib.sha256(original).hexdigest()
    entries = p0.entries()
    expected = (p0.PINNED_LOCK_SHA256 if uri == p0.INDEX_URI else
                next((e['sha256'] for e in entries if e['uri'] == uri), None))
    # Index is generated deterministically from the verified lock and is not a
    # member of the lock's content list; report its own runtime digest.
    if uri != p0.INDEX_URI and expected != digest:
        _error('P0_CONTENT_MISMATCH','Pinned P0 reference digest does not match source lock')
    return {
        'format': FORMAT,
        'uri': uri,
        'reference_version': 'v9.4',
        'read_only': True,
        'source_warrant': 'canonical_documentary_reference_only',
        'transport_role': 'mcp_tool_fallback_for_resources',
        'p1_validation_performed': False,
        'encoding': 'utf-8',
        'integrity_verified': True,
        'sha256': digest,
        'total_bytes': len(original),
        'offset': offset,
        'page_bytes': end - offset,
        'next_offset': end if end < len(original) else None,
        'complete': end == len(original),
        'content': content,
    }
