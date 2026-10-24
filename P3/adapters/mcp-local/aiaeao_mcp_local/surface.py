"""CP-001 / G4: whole-Cube capability discovery without changing P0/P1/P2.

This is metadata about *available local interfaces*, never a validation result.
The v0.1.1 printer capability card deliberately remains backward compatible.
"""
from __future__ import annotations
from typing import Any
from . import bridge, p0_resources, p1_adapter

FORMAT = 'aiaeao.cube.mcp-capability-surface/1'
RELEASE = 'P3-MCP-LOCAL/0.2.0-rc1'
TOOLS = (
    'cube_get_capabilities', 'cube_prepare_print', 'cube_check_print',
    'cube_render_svg', 'cube_read_reference', 'cube_validate',
    'cube_discover_surface',
)
PRINTER_TOOLS = TOOLS[:4]
P1_STATUSES = ('PASS', 'FAIL', 'UNRESOLVED')


def discover_surface() -> dict[str, Any]:
    """Return a deterministic, non-authoritative advertised surface.

    No network, filesystem writes, runtime validation or SVG rendering. P0
    source lock is checked, but the content itself is checked independently by
    G1 verifier. Unsupported host-side Resource access is NOT asserted.
    """
    entries = p0_resources.entries()  # checks pinned, immutable manifest lock
    legacy = bridge.get_capabilities()
    printer = legacy['core']
    adapter = legacy['adapter']
    if adapter['tools'] != list(PRINTER_TOOLS):
        raise RuntimeError('LEGACY_PRINTER_TOOL_CONTRACT_MISMATCH')
    if tuple(p1_adapter.CHECKS) != (
        'syntax', 'structure', 'concept_resolution', 'referent_binding',
        'predicate_typing', 'method_typing', 'qualifier_typing',
        'scope_consistency',
    ):
        raise RuntimeError('P1_CHECK_CONTRACT_MISMATCH')
    if len(entries) != 13:
        raise RuntimeError('P0_RESOURCE_CATALOGUE_MISMATCH')
    uris = [item['uri'] for item in entries] + [p0_resources.INDEX_URI]
    return {
        'format': FORMAT,
        'release': {
            'name': 'aiaeao-cube-local',
            'version': RELEASE,
            'status': 'release_candidate',
            'architecture': 'ADR-001/ACCEPTED;CP-001/G0-G3/ACCEPTED',
            'reference_version': 'v9.4',
        },
        'mcp': {
            'transport': 'stdio',
            'protocol_target': '2026-07-28',
            'official_python_sdk_major': 2,
            'tools': list(TOOLS),
            'resource_uris': uris,
            'host_resource_visibility': 'host_dependent_unverified',
            'fallback_when_host_hides_resources': 'cube_read_reference',
        },
        'domains': {
            'P0': {
                'role': 'canonical_documentary_reference',
                'reference_version': 'v9.4',
                'interface': 'MCP Resources primary, one allowlisted paged Tool fallback',
                'resource_count': len(uris),
                'source_reference_count': len(entries),
                'snapshot_lock_sha256': p0_resources.PINNED_LOCK_SHA256,
                'source_warrant': 'canonical_documentary_reference_only',
                'validation_performed': False,
                'truth_evaluated': False,
                'tools': ['cube_read_reference'],
            },
            'P1': {
                'role': 'descriptive_validation_only',
                'core_profile': 'P1-VC/1.0.0',
                'tools': ['cube_validate'],
                'statuses': list(P1_STATUSES),
                'checks': list(p1_adapter.CHECKS),
                'semantic_failure_is_mcp_error': False,
                'configuration_error_is_mcp_error': True,
                'source_truth': 'NOT_EVALUATED',
                'authority': 'NOT_EVALUATED',
                'admission': 'NOT_EVALUATED',
            },
            'P2': {
                'role': 'presentation_projection_only',
                'core_profile': printer['profile'],
                'tools': list(PRINTER_TOOLS),
                'views': printer['views'],
                'lenses': printer['lenses'],
                'granularity': printer['granularities'],
                'source_warrant': 'declared_unverified',
                'p1_validation_included': False,
                'automatic_acg_to_svg_mapping': False,
                'automatic_multi_svg': False,
            },
        },
        'compatibility': {
            'cube_get_capabilities_scope': 'legacy_P2_printer_only',
            'legacy_adapter_card_version': adapter['version'],
            'legacy_adapter_card_tools': list(PRINTER_TOOLS),
            'prefer_this_tool_for_whole_cube_discovery': True,
            'no_changes_to_p0_p1_p2': True,
        },
        'deployment': {
            'local_mcp_available': True,
            'remote_mcp_available': False,
            'http_api_available': False,
            'webmcp_available': False,
            'filesystem_side_effects_from_mcp_tools': False,
            'no_host_authentication_claim': True,
        },
        'cross_domain': {
            'p0_to_p1': 'NO_AUTOMATIC_REFERENCE_BINDING',
            'p1_to_p2': 'NO_AUTOMATIC_ACG_TO_VP03_MAPPING',
            'overall_status': 'NOT_DEFINED',
            'epistemic_warrant': 'NOT_EVALUATED',
            'current_authority': 'NOT_EVALUATED',
            'canonical_admission': 'NOT_EVALUATED',
        },
    }
