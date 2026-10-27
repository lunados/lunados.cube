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
P16 = REPO / 'P1' / 'instantiation-profile-v1'
P18 = REPO / 'P1' / 'simulation-profile-v1'
P19 = REPO / 'P1' / 'comparison-profile-v1'
P110 = REPO / 'P1' / 'migration-profile-v1'
P1101 = REPO / 'P1' / 'migration-profile-v2'
P111 = REPO / 'P1' / 'migration-methods-v1'
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


def _validator_for(context: dict | None):
    """Explicit /2 ... /7 dispatch, no auto-upgrade or hidden version negotiation.

    P1.6, P1.8, P1.9, P1.10, P1.10.1 and P1.11 are lazy-loaded so a legacy /1 installation works unchanged.
    A /2 ... /7 request without its module fails closed as an MCP adapter error.
    """
    if context is not None and context.get('format') == 'aiaeao.cube.binding-context/7':
        if not all(p.is_dir() for p in (P16, P18, P19, P110, P1101, P111)):
            _error('P1_MCP_P111_UNAVAILABLE', 'P1.11 validator is not installed')
        for path in (P16, P18, P19, P110, P1101, P111):
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        try:
            from cube_p111.validator import P111Validator
        except ImportError:
            _error('P1_MCP_P111_UNAVAILABLE', 'P1.11 validator cannot be loaded')
        validator = P111Validator()
        validator.validate_context(context)
        return validator
    if context is not None and context.get('format') == 'aiaeao.cube.binding-context/6':
        if not (P16.is_dir() and P18.is_dir() and P19.is_dir() and P110.is_dir() and P1101.is_dir()):
            _error('P1_MCP_P1101_UNAVAILABLE', 'P1.10.1 validator is not installed')
        for path in (P16, P18, P19, P110, P1101):
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        try:
            from cube_p1101.validator import P1101Validator
        except ImportError:
            _error('P1_MCP_P1101_UNAVAILABLE', 'P1.10.1 validator cannot be loaded')
        validator = P1101Validator()
        validator.validate_context(context)
        return validator
    if context is not None and context.get('format') == 'aiaeao.cube.binding-context/5':
        if not (P16.is_dir() and P18.is_dir() and P19.is_dir() and P110.is_dir()):
            _error('P1_MCP_P110_UNAVAILABLE', 'P1.10 validator is not installed')
        for path in (P16, P18, P19, P110):
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        try:
            from cube_p110.validator import P110Validator
        except ImportError:
            _error('P1_MCP_P110_UNAVAILABLE', 'P1.10 validator cannot be loaded')
        validator = P110Validator()
        validator.validate_context(context)
        return validator
    if context is not None and context.get('format') == 'aiaeao.cube.binding-context/4':
        if not (P16.is_dir() and P18.is_dir() and P19.is_dir()):
            _error('P1_MCP_P19_UNAVAILABLE', 'P1.9 validator is not installed')
        for path in (P16, P18, P19):
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        try:
            from cube_p19.validator import P19Validator
        except ImportError:
            _error('P1_MCP_P19_UNAVAILABLE', 'P1.9 validator cannot be loaded')
        validator = P19Validator()
        validator.validate_context(context)
        return validator
    if context is not None and context.get('format') == 'aiaeao.cube.binding-context/3':
        if not (P16.is_dir() and P18.is_dir()):
            _error('P1_MCP_P18_UNAVAILABLE', 'P1.8 validator is not installed')
        for path in (P16, P18):
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        try:
            from cube_p18.validator import P18Validator
        except ImportError:
            _error('P1_MCP_P18_UNAVAILABLE', 'P1.8 validator cannot be loaded')
        validator = P18Validator()
        validator.validate_context(context)
        return validator
    if context is None or context.get('format') != 'aiaeao.cube.binding-context/2':
        if context is not None:
            validate_context(context)
        return SemanticValidator()
    if not P16.is_dir():
        _error('P1_MCP_P16_UNAVAILABLE', 'P1.6 validator is not installed')
    if str(P16) not in sys.path:
        sys.path.insert(0,str(P16))
    try:
        from cube_p16.validator import P16Validator, validate_context as validate_p16_context
    except ImportError:
        _error('P1_MCP_P16_UNAVAILABLE', 'P1.6 validator cannot be loaded')
    validate_p16_context(context)
    return P16Validator()


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
        validator = _validator_for(context)
        if qualification_profiles is not None:
            validate_qualification_profiles(qualification_profiles)
        report = validator.validate_bytes(
            raw, input_format=input_format, context=context,
            qualification_profiles=qualification_profiles)
    except (ContextError, ContractError, ProfileError, ValueError, TypeError, RecursionError, OSError, KeyError, AttributeError, IndexError):
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
        **({'binding_context_profile': 'P1.6/instantiation-profile-v1'}
           if context is not None and context.get('format') in
              ('aiaeao.cube.binding-context/2', 'aiaeao.cube.binding-context/3',
               'aiaeao.cube.binding-context/4', 'aiaeao.cube.binding-context/5',
               'aiaeao.cube.binding-context/6', 'aiaeao.cube.binding-context/7') else {}),
        **({'simulation_profile': 'P1.8/simulation-profile-v1',
            'evaluation_performed_by_cube': False}
           if context is not None and context.get('format') in
              ('aiaeao.cube.binding-context/3', 'aiaeao.cube.binding-context/4',
               'aiaeao.cube.binding-context/5', 'aiaeao.cube.binding-context/6',
               'aiaeao.cube.binding-context/7') else {}),
        **({'comparison_profile': 'P1.9/comparison-profile-v1'}
           if context is not None and context.get('format') in
              ('aiaeao.cube.binding-context/4', 'aiaeao.cube.binding-context/5',
               'aiaeao.cube.binding-context/6', 'aiaeao.cube.binding-context/7') else {}),
        **({'migration_profile': 'P1.10/migration-profile-v1'}
           if context is not None and context.get('format')=='aiaeao.cube.binding-context/5' else {}),
        **({'migration_profile': 'P1.10.1/migration-profile-v2'}
           if context is not None and context.get('format')=='aiaeao.cube.binding-context/6' else {}),
        **({'migration_profile': 'P1.11/migration-methods-v1', 'method_execution_by_cube': False}
           if context is not None and context.get('format')=='aiaeao.cube.binding-context/7' else {}),
        'report': report,  # EXACT P1-VC/1.0.0 structure; no fields added or removed.
        'transport': 'local_mcp_stdio',
        'core_profile': 'P1-VC/1.0.0',  # underlying frozen P1 report schema for both context versions
        'source_warrant': 'declared_unverified',
        'input_encoding': 'utf-8',
        'declared_context_sha256': hashlib.sha256(_json_bytes(context)).hexdigest() if context is not None else None,
        'declared_qualification_profiles_sha256': hashlib.sha256(_json_bytes(qualification_profiles)).hexdigest()
            if qualification_profiles is not None else None,
        'declaration_digest_encoding': 'canonical_utf8_json_sorted_keys_compact_v1',
        'p1_validation_performed': True,
        'p2_printing_performed': False,
    }
