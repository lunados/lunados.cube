import json
import unittest
from pathlib import Path

class G5ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home=Path(__file__).resolve().parents[1]
        cls.index=json.loads((cls.home/'gateway/src/p0-registry.json').read_text('utf-8'))
        import sys
        sys.path.insert(0,str(cls.home/'.g5-runtime'))
        from core_runtime import dispatch,OPERATIONS
        cls.dispatch=staticmethod(dispatch)
        cls.operations=OPERATIONS

    def test_registration_count(self):self.assertEqual(len(self.index['resources']),14)
    def test_uris_unique(self):
        uris=[e['uri'] for e in self.index['resources']]
        self.assertEqual(len(set(uris)),14)
        self.assertIn('aiaeao://p0/resources/v1',uris)
    def test_operations_exact(self):self.assertEqual(len(self.operations),8) # 7 tools + resource operation
    def test_ref_indexes_offline(self):
        r=self.dispatch('cube_read_reference',{'uri':'aiaeao://p0/resources/v1'})
        self.assertTrue(r['ok']);self.assertEqual(r['result']['complete'],True)
        self.assertEqual(len(json.loads(r['result']['content'])['resources']),13)
    def test_resources_read_byte_parity(self):
        from aiaeao_mcp_local import p0_resources
        for entry in self.index['resources']:
            resp=self.dispatch('p0_resource_read',{'uri':entry['uri']})
            self.assertTrue(resp['ok'],entry['uri'])
            self.assertEqual(resp['result']['text'].encode(),p0_resources.read_bytes(entry['uri']))
    def test_ref_rejects_external_url(self):
        self.assertFalse(self.dispatch('cube_read_reference',{'uri':'https://evil.invalid/path'})['ok'])
    def test_p1_fail_is_successful_tool_result(self):
        r=self.dispatch('cube_validate',{'input_text':'this is not valid ACG'})
        self.assertTrue(r['ok']);self.assertEqual(r['result']['report']['overall_status'],'FAIL')
    def test_p1_config_error_is_tool_error(self):
        r=self.dispatch('cube_validate',{'input_text':'broken','context':{'source_kind':'trusted_source'}})
        self.assertFalse(r['ok']);self.assertEqual(r['diagnostic']['code'],'P1_MCP_CONFIG_INVALID')
    def test_surface_nonimplications(self):
        result=self.dispatch('cube_discover_surface')['result']
        self.assertEqual(result['cross_domain']['overall_status'],'NOT_DEFINED')
        for name in ('epistemic_warrant','current_authority','canonical_admission'):
            self.assertEqual(result['cross_domain'][name],'NOT_EVALUATED')
    def test_unknown_rejected(self):self.assertFalse(self.dispatch('eval',{'code':'print(1)'})['ok'])
    def test_no_user_files_or_network_functions(self):
        for x in ('read_file','open_url','execute','fetch','run_shell'):
            self.assertNotIn(x,self.operations)
    def test_legacy_printer_card_is_in_scope(self):
        r=self.dispatch('cube_get_capabilities')['result']
        self.assertEqual(len(r['core']['views']),3)
        self.assertFalse(r['core']['p1_validation_included'])
        self.assertTrue(r['remote_adapter']['remote_available'])
    def test_remote_no_auto_mapping(self):
        r=self.dispatch('cube_discover_surface')['result']
        self.assertEqual(r['cross_domain']['p1_to_p2'],'NO_AUTOMATIC_ACG_TO_VP03_MAPPING')
        self.assertEqual(r['deployment']['remote_transport'],'streamable_http')
    def test_p1_unresolved_and_pass(self):
        root=self.home.parents[1]
        acg=(root/'P1/semantic-validator-v1/fixtures/migration.acg').read_text('utf-8')
        context=json.loads((root/'P1/semantic-validator-v1/fixtures/migration.binding-context.json').read_text('utf-8'))
        unresolved=self.dispatch('cube_validate',{'input_text':acg})
        accepted=self.dispatch('cube_validate',{'input_text':acg,'context':context})
        self.assertEqual(unresolved['result']['report']['overall_status'],'UNRESOLVED')
        self.assertEqual(accepted['result']['report']['overall_status'],'PASS')
        for record in (unresolved,accepted):
            self.assertEqual(record['result']['report']['epistemic_warrant'],'NOT_EVALUATED')
            self.assertFalse(record['result']['p2_printing_performed'])

    def test_p1_fail_cannot_block_independent_p2(self):
        root=self.home.parents[1]
        bad=self.dispatch('cube_validate',{'input_text':'this is not valid ACG'})
        self.assertTrue(bad['ok']);self.assertEqual(bad['result']['report']['overall_status'],'FAIL')
        job=json.loads((root/'P2/visual-printer-release-v1/examples/flow_provenance_standard.job.json').read_text('utf-8'))
        good=self.dispatch('cube_render_svg',{'job':job})
        self.assertTrue(good['ok']);self.assertEqual(good['result']['report']['status'],'PASS')
        self.assertEqual(good['result']['report']['epistemic_warrant'],'NOT_EVALUATED')

    def test_g5_svg_exact_match(self):
        root=self.home.parents[1]
        fixture=root/'P2/visual-printer-release-v1/examples'
        job=json.loads((fixture/'flow_provenance_standard.job.json').read_text('utf-8'))
        good=self.dispatch('cube_render_svg',{'job':job})
        self.assertTrue(good['ok'])
        import hashlib
        raw=good['result']['artifact']['svg_text'].encode('utf-8')
        self.assertEqual(raw,(fixture/'flow_provenance_standard.svg').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),good['result']['artifact']['sha256'])


    def test_resource_mime_matches_pinned_lock(self):
        from aiaeao_mcp_local import p0_resources
        lock={e['uri']:e['mime_type'] for e in p0_resources.entries()}
        lock[p0_resources.INDEX_URI]='application/json'
        actual={e['uri']:e['mime_type'] for e in self.index['resources']}
        self.assertEqual(actual,lock)
        self.assertEqual(actual['https://cube.lunados.net/v9.4/morphology.md'],'text/markdown')
        read=self.dispatch('p0_resource_read',{'uri':'https://cube.lunados.net/v9.4/morphology.md'})
        self.assertTrue(read['ok'])
        self.assertEqual(read['result']['mime_type'],'text/markdown')

    def test_registry_has_p0_only(self):
        for item in self.index['resources']:
            self.assertTrue(item['uri'].startswith('https://cube.lunados.net/') or item['uri'].startswith('aiaeao://p0/'))

if __name__=='__main__':unittest.main()
