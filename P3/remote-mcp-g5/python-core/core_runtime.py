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

VERSION = 'P3-MCP-REMOTE/0.9.3-proof'  # R10 (MILE-016): VP-12 cube.landscape, VP-09.3 locale; R9: P1.15 /11, VP-07.8
PLAN_OPERATIONS = ('cube_plan_source', 'cube_plan_views', 'cube_plan_check')


def _plan_views():
    """The G6 plan layer, imported on first use so that the other tools keep their cold start (R5 §1)."""
    from aiaeao_mcp_local import plan_views
    return plan_views

OPERATIONS = frozenset({
    'cube_get_capabilities', 'cube_prepare_print', 'cube_check_print',
    'cube_render_svg', 'cube_read_reference', 'cube_validate',
    'cube_discover_surface', 'p0_resource_read',
    *PLAN_OPERATIONS,
})

class RemoteDiagnostic(Exception):
    def __init__(self, code, message):
        self.diagnostic = {'format': 'aiaeao.cube.mcp-g5-diagnostic/1',
                           'code': code, 'message': message,
                           'status': 'FAIL', 'files_written': False}
        super().__init__(code + ': ' + message)


def _sanitized_error(exc):
    if isinstance(exc, (bridge.BridgeFailure, p1_adapter.P1AdapterFailure)) or type(exc).__name__ == 'PlanFailure':
        return exc.diagnostic  # RW-2: the local diagnostic, unchanged
    if isinstance(exc, p0_resources.P0ResourceError):
        return {'code': exc.code, 'message': exc.message,
                'format': 'aiaeao.cube.mcp-p0-error/1', 'files_written': False}
    if isinstance(exc, RemoteDiagnostic):
        return exc.diagnostic
    return RemoteDiagnostic('G5_INTERNAL_ERROR','Internal operation failed').diagnostic


def _remote_surface():
    result = copy.deepcopy(surface.discover_surface())
    result['release'] = {**result['release'], 'name':'aiaeao-cube-mcp-remote-g5',
        'version':VERSION,
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
    result['p18_simulation'] = {
        'profile': 'P1.8/simulation-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/3'],
        'activation': 'explicit_context_format_3_only',
        'scope': 'declared_return_types_scenarios_evaluation_records',
        'scenario_modes': ['simulation', 'replay'],
        'evaluation_performed_by_cube': False,
        'library_resolution': 'format_check_only',
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p19_comparison'] = {
        'profile': 'P1.9/comparison-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/4'],
        'activation': 'explicit_context_format_4_only',
        'scope': 'declared_comparison_protocols_arms_pairing_parity_outcomes_replay_of',
        'outcome_vocabulary': ['a_preferred', 'b_preferred', 'equivalent_under_criteria',
                               'incomparable_under_criteria', 'undetermined_with_available_evidence'],
        'statistics_computed_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p110_migration'] = {
        'profile': 'P1.10/migration-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/5'],
        'activation': 'explicit_context_format_5_only',
        'scope': 'declared_migration_plans_phases_transitions_dependency_inventory',
        'predicate_profiles': ['P1.10/migration-predicates-v1'],
        'phase_roles': ['current', 'intermediate', 'target'],
        'transition_t_roles': ['scheduling'],
        'live_system_checked_by_cube': False,
        'migration_order_decided_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p1101_migration'] = {
        'profile': 'P1.10.1/migration-profile-v2',
        'binding_context_formats': ['aiaeao.cube.binding-context/6'],
        'activation': 'explicit_context_format_6_only',
        'scope': 'p110_migration_rules_plus_dependency_gap',
        'additional_diagnostics': ['P1_MIGRATION_DEPENDENCY_GAP'],
        'ends_reason_values': ['scope_end', 'replaced_outside_plan', 'other'],
        'live_system_checked_by_cube': False,
        'migration_order_decided_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p111_migration_methods'] = {
        'profile': 'P1.11/migration-methods-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/7'],
        'activation': 'explicit_context_format_7_only',
        'scope': 'p1101_rules_plus_pinned_method_catalog_and_method_bindings',
        'method_catalogs': ['P1.11/migration-methods-v1'],
        'catalog_methods': ['migrate.import/v1', 'migrate.rebuild/v1', 'migrate.retire/v1', 'migrate.rewrite/v1', 'migrate.reconfigure/v1'],
        'additional_diagnostics': ['P1_MIGRATION_METHOD_UNKNOWN', 'P1_MIGRATION_METHOD_SIGNATURE', 'P1_MIGRATION_METHOD_PLAN'],
        'method_execution_by_cube': False,
        'live_system_checked_by_cube': False,
        'migration_order_decided_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p112_coverage_instance'] = {
        'profile': 'P1.12/coverage-instance-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/8'],
        'activation': 'explicit_context_format_8_only',
        'scope': 'p111_rules_plus_declared_coverage_population_rules_and_typed_instance_membership',
        'additional_diagnostics': ['P1_COVERAGE_UNDECLARED', 'P1_INSTANCE_MISMATCH', 'P1_INSTANCE_UNDECLARED'],
        'population_rule_evaluation': 'lunados.lib analyze.population/v1 (not run by the Cube)',
        'population_evaluation_by_cube': False,
        'coverage_inferred_by_cube': False,
        'live_system_checked_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p113_control_flow'] = {
        'profile': 'P1.13/control-flow-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/9'],
        'activation': 'explicit_context_format_9_only',
        'scope': 'p112_rules_plus_declared_control_flow_and_flow_binding',
        'additional_diagnostics': ['P1_CONTROL_FLOW_INVALID', 'P1_CONTROL_FLOW_UNSUPPORTED', 'P1_FLOW_UNDECLARED', 'P1_TOKEN_POSITION_UNDECLARED'],
        'trace_conformance': 'lunados.lib analyze.trace-conformance/v1 (not run by the Cube)',
        'trace_evaluation_by_cube': False,
        'condition_evaluation_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p114_relation_origin'] = {
        'profile': 'P1.14/relation-origin-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/10'],
        'activation': 'explicit_context_format_10_only',
        'scope': 'declared_relation_origin_and_basis',
        'origin_values': ['declared', 'derived', 'unknown'],
        'origin_computed_by_cube': False,
        'derivation_computed_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    result['p115_scope_nesting'] = {
        'profile': 'P1.15/scope-nesting-profile-v1',
        'binding_context_formats': ['aiaeao.cube.binding-context/11'],
        'activation': 'explicit_context_format_11_only',
        'scope': 'declared_x_scope_chains_reference_v2_and_admission_outcomes',
        'additional_diagnostics': ['P1_SCOPE_NESTING_INVALID', 'P1_ADMISSION_OUTCOME_CONFLICT'],
        'instantiation_reference': 'P1.6 reference v2 (Authority resource_scope_ref + Revision, Artifact) for /11 only',
        'policy_narrowing_checked_by_cube': False,
        'outcome_decided_by_cube': False,
        'evaluation_performed_by_cube': False,
        'epistemic_warrant': 'NOT_EVALUATED',
        'current_authority': 'NOT_EVALUATED',
        'canonical_admission': 'NOT_EVALUATED',
    }
    # R5 (MILE-010, Q-6): the plan tools are remote now; this supersedes G6 C-13 §5 for the remote card only.
    pv = _plan_views()
    result['mcp'] = {**result['mcp'], 'tools': list(result['mcp']['tools']) + list(PLAN_OPERATIONS)}
    result['domains']['P2'] = {**result['domains']['P2'], 'plan_views': {**pv.capabilities(), 'remote_available': True,
                                                                          'transport': 'streamable_http'}}
    result['remote_adapter'] = {'name':'aiaeao-cube-mcp-g5',
        'version':VERSION,
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
                'version':VERSION}
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
        elif operation == 'cube_plan_source':          # RW-1: as the local server passes the options
            a = arguments
            result = _plan_views().plan_source(a['context'], a['plan_id'], a['printer'], tracks=a.get('track_map'), track=a.get('track'),
                labels=a.get('labels'), layers=a.get('layers'), witness_prefixes=a.get('witness_prefixes'), edge_styles=a.get('edge_styles'),
                steps=a.get('steps'), subjects=a.get('subjects'), profile=a.get('profile'), predicate=a.get('predicate'),
                statements=a.get('statements'), projection=a.get('projection'), records=a.get('records'),
                origin_lines=a.get('origin_lines'), placement_predicates=a.get('placement_predicates'))
        elif operation == 'cube_plan_views':
            a = arguments
            result = _plan_views().plan_views(a['source'], a['view'], a['granularity'], partition=a.get('partition'), rows=a.get('rows'),
                cols=a.get('cols'), lens=a.get('lens'), overflow=a.get('overflow'), locale=a.get('locale'),
                hide_ledger=a.get('hide_ledger') or None, hide_empty=a.get('hide_empty'), axis_order=a.get('axis_order'))
        elif operation == 'cube_plan_check':
            result = _plan_views().plan_check(arguments['result'])
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
    except Exception as exc:  # noqa: BLE001
        if type(exc).__name__ == 'PlanFailure':   # plan_views.PlanFailure (lazy import, RW-2)
            return {'ok':False,'diagnostic':_sanitized_error(exc)}
        if isinstance(exc,(KeyError,ValueError,TypeError,RecursionError)):
            return {'ok':False,'diagnostic':RemoteDiagnostic('G5_ARGUMENTS_INVALID','Invalid operation arguments').diagnostic}
        return {'ok':False,'diagnostic':RemoteDiagnostic('G5_INTERNAL_ERROR','Internal operation failed').diagnostic}


def wire_call(payload):
    if type(payload) is not dict or type(payload.get('operation')) is not str:
        return {'ok':False,'diagnostic':RemoteDiagnostic(
            'G5_REQUEST_INVALID','Request must provide an operation name').diagnostic}
    return dispatch(payload['operation'],payload.get('arguments',{}))
