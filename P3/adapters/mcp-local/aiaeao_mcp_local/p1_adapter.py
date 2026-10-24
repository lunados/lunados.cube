"""CP-001/G2: read-only MCP facade for the *unchanged* P1-VC/1.0.0 validator.

Semantic PASS/FAIL/UNRESOLVED are successful MCP tool results. Invalid API
configuration is a transport/adapter error (P1 CLI exit 3 analogue).
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[4]
P1 = REPO / 'P1' / 'semantic-validator-v1'
if not P1.is_dir():
    raise RuntimeError('P1-VC/1.0.0 reference validator must be installed as sibling P1 tree')
if str(P1) not in sys.path:
    sys.path.insert(0, str(P1))
from cube_semantic.validator import (  # noqa: E402
    SemanticValidator, validate_qualification_profiles, ProfileError,
)
from cube_resolver.resolver import validate_context, ContextError, ContractError  # noqa: E402

MAX_MCP_BYTES = 2 * 1024 * 1024
MAX_P1_TEXT_BYTES = 1024 * 1024
CHECKS = ('syntax','structure','concept_resolution','referent_binding',
          'predicate_typing','method_typing','qualifier_typing','scope_consistency')


class P1AdapterFailure(Exception):
    def __init__(self, code: str, message: str):
        self.diagnostic = {
            'format': 'aiaeao.cube.mcp-p1-adapter-error/1',
            'code': code, 'message': message, 'stage': 'p1_adapter',
            'semantic_status': 'NOT_EVALUATED', 'files_written': False,
        }
        super().__init__(code + ': ' + message)


def _error(code: str, message: str) -> None:
    raise P1AdapterFailure(code, message)


def _json_bytes(obj: Any) -> bytes:
    try:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError):
        _error('P1_MCP_INPUT_INVALID', 'Arguments must contain finite UTF-8 JSON values')


def validate(input_text: str, input_format: str='acg_text', context: dict | None=None,
             qualification_profiles: dict | None=None) -> dict:
    """Return the exact frozen P1 report inside a transport metadata envelope.

    Text is UTF-8-encoded *as received*. Declaration hashes cover a documented
    canonical JSON serialization, not unknown original HTTP/JSON wire bytes.
    """
    if type(input_text) is not str:
        _error('P1_MCP_INPUT_INVALID', 'input_text must be a Unicode string')
    if input_format not in ('acg_text', 'json_ast'):
        _error('P1_MCP_FORMAT_INVALID', 'input_format must be acg_text or json_ast')
    if context is not None and type(context) is not dict:
        _error('P1_MCP_CONTEXT_INVALID', 'context must be a JSON object or null')
    if qualification_profiles is not None and type(qualification_profiles) is not dict:
        _error('P1_MCP_PROFILE_INVALID', 'qualification_profiles must be a JSON object or null')
    serialized = _json_bytes({'input_text':input_text,'input_format':input_format,
                              'context':context,'qualification_profiles':qualification_profiles})
    if len(serialized) > MAX_MCP_BYTES:
        _error('P1_MCP_INPUT_TOO_LARGE', 'MCP request exceeds 2 MiB')
    try:
        raw = input_text.encode('utf-8', errors='strict')
    except UnicodeError:
        _error('P1_MCP_INPUT_INVALID', 'input_text must be valid UTF-8')
    if len(raw) > MAX_P1_TEXT_BYTES:
        _error('P1_MCP_TEXT_TOO_LARGE', 'P1 input exceeds 1 MiB')
    try:
        if context is not None:
            validate_context(context)
        if qualification_profiles is not None:
            validate_qualification_profiles(qualification_profiles)
        report = SemanticValidator().validate_bytes(
            raw, input_format=input_format, context=context,
            qualification_profiles=qualification_profiles)
    except (ContextError, ContractError, ProfileError, ValueError, TypeError, RecursionError, OSError):
        # CLI exit-3 analogue: no raw exceptions, local paths or payload echoed.
        _error('P1_MCP_CONFIG_INVALID', 'P1 input context, profile, or local reference is invalid')
    if report.get('overall_status') not in ('PASS', 'FAIL', 'UNRESOLVED'):
        _error('P1_MCP_RESULT_INVALID', 'P1 returned an unsupported semantic status')
    if tuple(report.get('checks',{})) != CHECKS:
        _error('P1_MCP_RESULT_INVALID', 'P1 report has an unexpected check set or order')
    if any(report.get(k) != 'NOT_EVALUATED' for k in
           ('epistemic_warrant','current_authority','canonical_admission')):
        _error('P1_MCP_RESULT_INVALID', 'P1 reported a forbidden truth or authority conclusion')
    if report.get('input_sha256') != hashlib.sha256(raw).hexdigest():
        _error('P1_MCP_RESULT_INVALID', 'P1 input digest does not match submitted UTF-8 text')
    return {
        'report': report,  # EXACT P1-VC/1.0.0 structure; no fields added or removed.
        'transport': 'local_mcp_stdio',
        'core_profile': 'P1-VC/1.0.0',
        'source_warrant': 'declared_unverified',
        'input_encoding': 'utf-8',
        'declared_context_sha256': hashlib.sha256(_json_bytes(context)).hexdigest() if context is not None else None,
        'declared_qualification_profiles_sha256': hashlib.sha256(_json_bytes(qualification_profiles)).hexdigest()
            if qualification_profiles is not None else None,
        'declaration_digest_encoding': 'canonical_utf8_json_sorted_keys_compact_v1',
        'p1_validation_performed': True,
        'p2_printing_performed': False,
    }
