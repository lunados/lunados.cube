"""G4 offline whole-Cube capability contract tests; no MCP SDK required."""
from __future__ import annotations
import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from aiaeao_mcp_local import bridge, p0_resources, p1_adapter, surface

BASE = Path(__file__).resolve().parents[1]
NAMES = list(surface.TOOLS)

class TestG4Surface(unittest.TestCase):
    def setUp(self): self.card = surface.discover_surface()
    def test_format(self): self.assertEqual(self.card['format'],'aiaeao.cube.mcp-capability-surface/1')
    def test_release(self): self.assertEqual(self.card['release']['version'],'P3-MCP-LOCAL/0.2.0-rc1')
    def test_status(self): self.assertEqual(self.card['release']['status'],'release_candidate')
    def test_ref(self): self.assertEqual(self.card['release']['reference_version'],'v9.4')
    def test_stdio(self): self.assertEqual(self.card['mcp']['transport'],'stdio')
    def test_protocol(self): self.assertEqual(self.card['mcp']['protocol_target'],'2026-07-28')
    def test_sdk(self): self.assertEqual(self.card['mcp']['official_python_sdk_major'],2)
    def test_tool_inventory(self): self.assertEqual(self.card['mcp']['tools'],NAMES)
    def test_legacy_tool_prefix(self): self.assertEqual(NAMES[:4],list(bridge.TOOL_NAMES))
    def test_seventh_tool(self): self.assertEqual(NAMES[-1],'cube_discover_surface')
    def test_no_duplicate_tools(self): self.assertEqual(len(NAMES),len(set(NAMES)))
    def test_resource_number(self): self.assertEqual(len(self.card['mcp']['resource_uris']),14)
    def test_resource_uris(self): self.assertEqual(set(self.card['mcp']['resource_uris']),{x['uri'] for x in p0_resources.entries()}|{p0_resources.INDEX_URI})
    def test_resource_index(self): self.assertIn(p0_resources.INDEX_URI,self.card['mcp']['resource_uris'])
    def test_lock(self): self.assertEqual(self.card['domains']['P0']['snapshot_lock_sha256'],p0_resources.PINNED_LOCK_SHA256)
    def test_p0_source_count(self): self.assertEqual(self.card['domains']['P0']['source_reference_count'],13)
    def test_p0_warrant(self): self.assertEqual(self.card['domains']['P0']['source_warrant'],'canonical_documentary_reference_only')
    def test_p0_not_validation(self): self.assertIs(self.card['domains']['P0']['validation_performed'],False)
    def test_p1_tool(self): self.assertEqual(self.card['domains']['P1']['tools'],['cube_validate'])
    def test_p1_profile(self): self.assertEqual(self.card['domains']['P1']['core_profile'],'P1-VC/1.0.0')
    def test_p1_statuses(self): self.assertEqual(self.card['domains']['P1']['statuses'],['PASS','FAIL','UNRESOLVED'])
    def test_p1_checks(self): self.assertEqual(self.card['domains']['P1']['checks'],list(p1_adapter.CHECKS))
    def test_p1_not_mcp_error(self): self.assertIs(self.card['domains']['P1']['semantic_failure_is_mcp_error'],False)
    def test_p1_config_error(self): self.assertIs(self.card['domains']['P1']['configuration_error_is_mcp_error'],True)
    def test_p1_no_authority(self): self.assertEqual(self.card['domains']['P1']['authority'],'NOT_EVALUATED')
    def test_p1_no_admission(self): self.assertEqual(self.card['domains']['P1']['admission'],'NOT_EVALUATED')
    def test_p2_profile(self): self.assertEqual(self.card['domains']['P2']['core_profile'],'P2-VP/1.0.0-rc1')
    def test_p2_tools(self): self.assertEqual(self.card['domains']['P2']['tools'],list(bridge.TOOL_NAMES))
    def test_p2_views(self): self.assertEqual(self.card['domains']['P2']['views'],bridge.get_capabilities()['core']['views'])
    def test_p2_lenses(self): self.assertEqual(self.card['domains']['P2']['lenses'],bridge.get_capabilities()['core']['lenses'])
    def test_p2_granularity(self): self.assertEqual(self.card['domains']['P2']['granularity'],['overview','standard','detail'])
    def test_p2_no_validation(self): self.assertIs(self.card['domains']['P2']['p1_validation_included'],False)
    def test_no_acg_mapping(self): self.assertIs(self.card['domains']['P2']['automatic_acg_to_svg_mapping'],False)
    def test_legacy_card_untouched(self):
        card=bridge.get_capabilities()['adapter']
        self.assertEqual(card['version'],'P3-MCP-LOCAL/0.1.1')
        self.assertEqual(card['tools'],NAMES[:4])
        self.assertFalse(card['p1_validation'])
    def test_legacy_card_scope_disclosed(self): self.assertEqual(self.card['compatibility']['cube_get_capabilities_scope'],'legacy_P2_printer_only')
    def test_host_visibility_not_promised(self): self.assertEqual(self.card['mcp']['host_resource_visibility'],'host_dependent_unverified')
    def test_tool_fallback(self): self.assertEqual(self.card['mcp']['fallback_when_host_hides_resources'],'cube_read_reference')
    def test_no_remote_mcp(self): self.assertIs(self.card['deployment']['remote_mcp_available'],False)
    def test_no_http(self): self.assertIs(self.card['deployment']['http_api_available'],False)
    def test_no_webmcp(self): self.assertIs(self.card['deployment']['webmcp_available'],False)
    def test_no_fs_effects(self): self.assertIs(self.card['deployment']['filesystem_side_effects_from_mcp_tools'],False)
    def test_not_overall_status(self): self.assertEqual(self.card['cross_domain']['overall_status'],'NOT_DEFINED')
    def test_not_cross_domain_link(self): self.assertEqual(self.card['cross_domain']['p1_to_p2'],'NO_AUTOMATIC_ACG_TO_VP03_MAPPING')
    def test_no_epistemic_warrant(self): self.assertEqual(self.card['cross_domain']['epistemic_warrant'],'NOT_EVALUATED')
    def test_not_authority(self): self.assertEqual(self.card['cross_domain']['current_authority'],'NOT_EVALUATED')
    def test_not_admission(self): self.assertEqual(self.card['cross_domain']['canonical_admission'],'NOT_EVALUATED')
    def test_deterministic(self): self.assertEqual(surface.discover_surface(),surface.discover_surface())
    def test_no_shared_mutation(self):
        x=surface.discover_surface(); x['mcp']['tools'].append('fake'); x['domains']['P2']['views'].append('fake')
        self.assertEqual(surface.discover_surface()['mcp']['tools'],NAMES)
        self.assertNotIn('fake',surface.discover_surface()['domains']['P2']['views'])
    def test_serializable(self): json.dumps(self.card,allow_nan=False,ensure_ascii=False)
    def test_no_local_paths(self): self.assertNotIn(str(BASE),json.dumps(self.card,ensure_ascii=False))
    def test_registrations_match(self):
        tree=ast.parse((BASE/'aiaeao_mcp_local/server.py').read_text(encoding='utf-8'))
        found=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
               and any(isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='tool' for d in n.decorator_list)]
        # G6: the server registers the seven G4 tools first, then the three plan-view tools (G4 card itself unchanged)
        self.assertEqual(found[:7],NAMES)
        self.assertEqual(found,list(surface.TOOLS_G6))
    def test_golden(self):
        path=BASE/'evidence/G4_CAPABILITIES_GOLDEN.json'
        self.assertEqual(self.card,json.loads(path.read_text(encoding='utf-8')))
    def test_missing_p0_lock_is_fail_closed(self):
        with patch.object(p0_resources, 'PINNED_LOCK_SHA256','0'*64):
            with self.assertRaises(p0_resources.P0ResourceError):surface.discover_surface()
    def test_p1_check_drift_is_fail_closed(self):
        with patch.object(p1_adapter,'CHECKS',('syntax',)):
            with self.assertRaisesRegex(RuntimeError,'P1_CHECK_CONTRACT_MISMATCH'):surface.discover_surface()
    def test_p2_registry_drift_is_fail_closed(self):
        fake=copy.deepcopy(bridge.get_capabilities())
        fake['adapter']['tools'].append('made_up_tool')
        with patch.object(bridge,'get_capabilities',return_value=fake):
            with self.assertRaisesRegex(RuntimeError,'LEGACY_PRINTER_TOOL_CONTRACT_MISMATCH'):surface.discover_surface()
    def test_static_legacy_signature(self):
        src=(BASE/'aiaeao_mcp_local/server.py').read_text()
        tree=ast.parse(src)
        calls={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(list(calls['cube_get_capabilities'].args.args),[])  # no new arguments

if __name__=='__main__': unittest.main()
