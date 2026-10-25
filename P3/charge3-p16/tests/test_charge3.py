"""Charge 3: materialized transport vectors and strict v1 compatibility."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'P3/adapters/mcp-local'))
sys.path.insert(0,str(REPO/'P1/semantic-validator-v1'))
from aiaeao_mcp_local import p1_adapter, surface, bridge
from cube_semantic.validator import SemanticValidator

FIXTURE=Path(__file__).resolve().parents[1]/'fixtures/r01_r13_materialized.json'
VECTORS=json.loads(FIXTURE.read_text('utf-8'))['cases']

class Charge3LocalTests(unittest.TestCase):
    def test_01_fixed_thirteen_cases_through_local_mcp_facade(self):
        self.assertEqual(len(VECTORS),13)
        for v in VECTORS:
            with self.subTest(v=v['id']):
                w=p1_adapter.validate(v['input_text'],v['input_format'],v['context'])
                report=w['report']
                self.assertEqual(report['overall_status'],v['expected_overall'])
                self.assertEqual(w['core_profile'],'P1-VC/1.0.0')
                if v['context']['format'].endswith('/2'):
                    self.assertEqual(w['binding_context_profile'],'P1.6/instantiation-profile-v1')
                else:
                    self.assertNotIn('binding_context_profile',w)
                self.assertEqual(w['declared_context_sha256'], hashlib.sha256(
                    p1_adapter._json_bytes(v['context'])).hexdigest())
                codes={d['code'] for d in report['diagnostics']}
                self.assertTrue(set(v['required_codes']).issubset(codes))
                for field in ('epistemic_warrant','current_authority','canonical_admission'):
                    self.assertEqual(report[field],'NOT_EVALUATED')
                self.assertFalse(w['p2_printing_performed'])
                self.assertNotIn('artifact',w)

    def test_02_v1_unchanged_exact_frozen_core_report(self):
        fixture=REPO/'P1/semantic-validator-v1/fixtures'
        for name in ('migration','metaphysics'):
            context=json.loads((fixture/(name+'.binding-context.json')).read_text('utf-8'))
            text=(fixture/(name+'.acg')).read_text('utf-8')
            wrapper=p1_adapter.validate(text,context=context)
            exact=SemanticValidator().validate_bytes(text.encode('utf-8'),context=context)
            self.assertEqual(wrapper['report'],exact)
            self.assertNotIn('binding_context_profile',wrapper)
            self.assertEqual(set(wrapper),{'report','transport','core_profile','source_warrant',
                    'input_encoding','declared_context_sha256','declared_qualification_profiles_sha256',
                    'declaration_digest_encoding','p1_validation_performed','p2_printing_performed'})

    def test_03_no_context_unmodified(self):
        x=p1_adapter.validate('this is not valid ACG')
        self.assertEqual(x['report']['overall_status'],'FAIL')
        self.assertNotIn('binding_context_profile',x)

    def test_04_p16_config_failure_mcp_error(self):
        valid=copy.deepcopy(VECTORS[0]['context'])
        valid['instantiation_profiles'][0]['untrusted_extension']='bad'
        with self.assertRaises(p1_adapter.P1AdapterFailure) as c:
            p1_adapter.validate(VECTORS[0]['input_text'],context=valid)
        self.assertEqual(c.exception.diagnostic['code'],'P1_MCP_CONFIG_INVALID')
        self.assertEqual(c.exception.diagnostic['semantic_status'],'NOT_EVALUATED')

    def test_05_missing_p16_fails_closed(self):
        with patch.object(p1_adapter,'P16',Path('/nonexistent/p16')):
            with self.assertRaises(p1_adapter.P1AdapterFailure) as c:
                p1_adapter.validate(VECTORS[0]['input_text'],context=VECTORS[0]['context'])
        self.assertEqual(c.exception.diagnostic['code'],'P1_MCP_P16_UNAVAILABLE')

    def test_06_never_promote_source_truth_or_governance(self):
        for v in VECTORS:
            r=p1_adapter.validate(v['input_text'],context=v['context'])
            self.assertEqual(r['source_warrant'],'declared_unverified')
            self.assertFalse(r['p2_printing_performed'])
            self.assertEqual(r['report']['canonical_admission'],'NOT_EVALUATED')

    def test_07_surface_exact_tool_count_and_explicit_formats(self):
        surf=surface.discover_surface()
        self.assertEqual(len(surf['mcp']['tools']),7)
        self.assertEqual(len(surf['mcp']['resource_uris']),14)
        p1=surf['domains']['P1']
        self.assertEqual(p1['checks'],list(p1_adapter.CHECKS))
        # G4 frozen discovery remains golden-byte stable; G5 /2 metadata is additive.
        self.assertNotIn('binding_context_formats',p1)
        self.assertEqual(surf['cross_domain']['overall_status'],'NOT_DEFINED')
        self.assertEqual(bridge.get_capabilities()['adapter']['tools'],list(surface.PRINTER_TOOLS))

    def test_08_never_accept_unknown_context_format(self):
        v=copy.deepcopy(VECTORS[0]['context']);v['format']='aiaeao.cube.binding-context/3'
        with self.assertRaises(p1_adapter.P1AdapterFailure) as c:
            p1_adapter.validate(VECTORS[0]['input_text'],context=v)
        self.assertEqual(c.exception.diagnostic['code'],'P1_MCP_CONFIG_INVALID')

    def test_10_historical_freeze_anchors_byte_exact(self):
        lock=json.loads((REPO/'P3/charge3-p16/BASELINE_LOCK.json').read_text('utf-8'))
        for rel,digest in lock['anchors'].items():
            with self.subTest(file=rel):
                self.assertEqual(hashlib.sha256((REPO/rel).read_bytes()).hexdigest(),digest)

    def test_09_full_v2_report_same_closed_field_set(self):
        v=VECTORS[0]
        report=p1_adapter.validate(v['input_text'],context=v['context'])['report']
        frozen=SemanticValidator().validate_bytes('this is not valid ACG'.encode('utf-8'))
        self.assertEqual(set(report),set(frozen))
        self.assertEqual(tuple(report['checks']),p1_adapter.CHECKS)

if __name__=='__main__':unittest.main()
