"""G5: transport-only facade over frozen G4 business functions.

Works with ordinary CPython for exact local parity testing; loaded by a private
Cloudflare Python Worker in remote feasibility testing. No stdio SDK imported.
"""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / 'P3' / 'adapters' / 'mcp-local'
if str(ADAPTER) not in sys.path:
    sys.path.insert(0, str(ADAPTER))
from aiaeao_mcp_local import bridge, p0_resources, p0_tool, p1_adapter, surface

OPERATIONS = frozenset({
    'cube_get_capabilities', 'cube_prepare_print', 'cube_check_print',
    'cube_render_svg', 'cube_read_reference', 'cube_validate',
    'cube_discover_surface', 'p0_resource_read',
})

class RemoteDiagnostic(Exception):
    def __init__(self, code, message):
        self.diagnostic = {'format': 'aiaeao.cube.mcp-g5-diagnostic/1',
                           'code': code, 'message': message,
                           'status': 'FAIL', 'files_written': False}
        super().__init__(code + ': ' + message)


def _sanitized_error(exc):
    if isinstance(exc, (bridge.BridgeFailure, p1_adapter.P1AdapterFailure)):
        return exc.diagnostic
    if isinstance(exc, p0_resources.P0ResourceError):
        return {'code': exc.code, 'message': exc.message,
                'format': 'aiaeao.cube.mcp-p0-error/1', 'files_written': False}
    if isinstance(exc, RemoteDiagnostic):
        return exc.diagnostic
    return RemoteDiagnostic('G5_INTERNAL_ERROR','Internal operation failed').diagnostic


def _remote_surface():
    result = copy.deepcopy(surface.discover_surface())
    result['release'] = {**result['release'], 'name':'aiaeao-cube-mcp-remote-g5',
        'version':'P3-MCP-REMOTE/0.1.0-proof',
        'status':'remote_proof_not_accepted',
        'local_surface_profile':'P3-MCP-LOCAL/0.2.0-rc1'}
    result['mcp'] = {**result['mcp'], 'transport':'streamable_http',
                     'protocol_target':'2026-07-28'}
    result['deployment'] = {
        'local_mcp_available': True,  # existing separate stdio installation
        'remote_mcp_available': True,
        'remote_transport': 'streamable_http',
        'remote_status': 'G5_PROOF_NOT_PRODUCTION_AUTHORIZED',
        'host_authentication': 'gateway_bearer_proof_only',
        'http_api_available': False,
        'webmcp_available': False,
        'filesystem_side_effects_from_mcp_tools': False,
    }
    result['p16_instantiation'] = {
        'profile': 'P1.6/instantiation-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/1',
                                    'aiaeao.cube.binding-context/2'],
        'activation': 'explicit_context_format_2_only',
        'scope': 'declared_X_endpoint_slots',
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['remote_adapter'] = {'name':'aiaeao-cube-mcp-g5',
        'version':'P3-MCP-REMOTE/0.1.0-proof',
        'profile':'remote_service_binding_to_frozen_P0_P1_P2'}
    return result


def dispatch(operation, arguments=None):
    """Callable internal boundary: {ok, result}|{ok:false,diagnostic}.

    P1 FAIL remains ok:true. All expected input errors stay in explicit diagnostic.
    """
    if arguments is None: arguments = {}
    if operation not in OPERATIONS:
        return {'ok': False, 'diagnostic': RemoteDiagnostic(
            'G5_OPERATION_UNKNOWN','Operation not in approved allowlist').diagnostic}
    if type(arguments) is not dict:
        return {'ok': False, 'diagnostic': RemoteDiagnostic(
            'G5_ARGUMENTS_INVALID','Operation arguments must be a JSON object').diagnostic}
    try:
        if operation == 'cube_get_capabilities':
            result = copy.deepcopy(bridge.get_capabilities())
            result['remote_adapter'] = {'transport':'streamable_http',
                'remote_available':True,'name':'aiaeao-cube-mcp-g5',
                'version':'P3-MCP-REMOTE/0.1.0-proof'}
        elif operation == 'cube_discover_surface':
            result = _remote_surface()
        elif operation == 'cube_prepare_print':
            result = bridge.prepare_print(
                arguments['bundle'],arguments['lens'],arguments['granularity'],
                arguments.get('overflow','summarize'),arguments.get('focus'),
                arguments.get('max_items'),arguments.get('max_edges'))
        elif operation == 'cube_check_print':
            result = bridge.check_print(arguments['job'])
        elif operation == 'cube_render_svg':
            result = copy.deepcopy(bridge.render_svg(arguments['job']))
            result['transport'] = 'remote_mcp_streamable_http'
        elif operation == 'cube_read_reference':
            result = p0_tool.read_reference(arguments['uri'],
                arguments.get('offset',0),arguments.get('max_bytes',8192))
        elif operation == 'cube_validate':
            result = copy.deepcopy(p1_adapter.validate(
                arguments['input_text'],arguments.get('input_format','acg_text'),
                arguments.get('context'),arguments.get('qualification_profiles')))
            result['transport'] = 'remote_mcp_streamable_http'
        else:  # p0_resource_read; resources hosted by Gateway using same pinned backend.
            uri = arguments['uri']
            result = {'uri':uri,'text':p0_resources.read_text(uri),
                      'sha256':__import__('hashlib').sha256(p0_resources.read_bytes(uri)).hexdigest(),
                      'mime_type':('application/json' if uri == p0_resources.INDEX_URI else
                                   next(entry['mime_type'] for entry in p0_resources.entries() if entry['uri'] == uri))}
        return {'ok':True,'result':result}
    except (bridge.BridgeFailure,p1_adapter.P1AdapterFailure,p0_resources.P0ResourceError,
            RemoteDiagnostic) as exc:
        return {'ok':False,'diagnostic':_sanitized_error(exc)}
    except (KeyError,ValueError,TypeError,RecursionError):
        return {'ok':False,'diagnostic':RemoteDiagnostic(
            'G5_ARGUMENTS_INVALID','Invalid operation arguments').diagnostic}
    except Exception:
        return {'ok':False,'diagnostic':RemoteDiagnostic(
            'G5_INTERNAL_ERROR','Internal operation failed').diagnostic}


def wire_call(payload):
    if type(payload) is not dict or type(payload.get('operation')) is not str:
        return {'ok':False,'diagnostic':RemoteDiagnostic(
            'G5_REQUEST_INVALID','Request must provide an operation name').diagnostic}
    return dispatch(payload['operation'],payload.get('arguments',{}))
