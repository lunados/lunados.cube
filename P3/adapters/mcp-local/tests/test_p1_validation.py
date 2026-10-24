"""CP-001 G2 independent tests: original P1 CLI vs MCP adapter, no SDK required."""
from __future__ import annotations
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aiaeao_mcp_local import bridge, p1_adapter as p1

ROOT=Path(__file__).resolve().parents[4]
P1=ROOT/'P1'/'semantic-validator-v1'
FIX=P1/'fixtures'
SOURCE=(FIX/'migration.acg').read_text(encoding='utf-8')
CTX=json.loads((FIX/'migration.binding-context.json').read_text(encoding='utf-8'))
PROFILE=json.loads((FIX/'semantic/migration.qualifier-profiles.json').read_text(encoding='utf-8'))
METHOD_CTX=json.loads((FIX/'semantic/migration-with-method.binding-context.json').read_text(encoding='utf-8'))


def cli(text, fmt='acg_text', context=None, profiles=None):
    """Independent execution through the frozen P1 command-line interface."""
    with tempfile.TemporaryDirectory() as tmp:
        argv=[sys.executable,'-S','-m','cube_semantic','--input','-', '--input-format',fmt]
        if context is not None:
            path=Path(tmp)/'ctx.json'
            path.write_text(json.dumps(context, ensure_ascii=False),encoding='utf-8')
            argv+=['--context',str(path)]
        if profiles is not None:
            path=Path(tmp)/'profile.json'
            path.write_text(json.dumps(profiles, ensure_ascii=False),encoding='utf-8')
            argv+=['--qualification-profiles',str(path)]
        env=os.environ.copy();env['PYTHONPATH']=str(P1);env['PYTHONDONTWRITEBYTECODE']='1'
        c=subprocess.run(argv,cwd=P1,input=text.encode('utf-8'),stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,env=env,timeout=15)
        if c.returncode==3:
            return 3, json.loads(c.stderr)
        return c.returncode, json.loads(c.stdout)


def report(text=SOURCE,format='acg_text',context=None,qualification_profiles=None):
    return p1.validate(text,format,context,qualification_profiles)['report']


class P1ReportParity(unittest.TestCase):
    def assert_parity(self,text,fmt='acg_text',context=None,profiles=None,expected=None):
        wrapper=p1.validate(text,fmt,context,profiles)
        c,original=cli(text,fmt,context,profiles)
        result=wrapper['report']
        self.assertIn(result['overall_status'],('PASS','FAIL','UNRESOLVED'))
        self.assertEqual(c,{'PASS':0,'UNRESOLVED':1,'FAIL':2}[result['overall_status']])
        self.assertEqual(result,original,'MCP adapter MUST return unmodified P1 report')
        if expected:self.assertEqual(result['overall_status'],expected)
        self.assertEqual(tuple(result['checks']),p1.CHECKS)
        self.assertEqual(result['input_sha256'],hashlib.sha256(text.encode('utf-8')).hexdigest())
        for field in ('epistemic_warrant','current_authority','canonical_admission'):
            self.assertEqual(result[field],'NOT_EVALUATED')
        self.assertEqual(wrapper['source_warrant'],'declared_unverified')
        self.assertFalse(wrapper['p2_printing_performed'])
        self.assertTrue(wrapper['p1_validation_performed'])
        self.assertEqual(wrapper['core_profile'],'P1-VC/1.0.0')
        self.assertNotIn('artifact',wrapper)
        return wrapper

    def test_pass_bound_context(self):self.assert_parity(SOURCE,context=CTX,expected='PASS')
    def test_unresolved_missing_context(self):self.assert_parity(SOURCE,expected='UNRESOLVED')
    def test_fail_syntax(self):self.assert_parity('unparseable input',expected='FAIL')
    def test_fail_unicode_wellformed_text(self):self.assert_parity('Y:α:Artifact["🧭🍄"]',expected='UNRESOLVED')
    def test_invalid_unicode_scalar_is_error(self):
        with self.assertRaises(p1.P1AdapterFailure) as c:p1.validate('\ud800')
        self.assertEqual(c.exception.diagnostic['code'],'P1_MCP_INPUT_INVALID')
    def test_illformed_escape_is_fail(self):self.assert_parity(r'Y:α:Artifact["\uD800"]',expected='FAIL')
    def test_surrounding_whitespace_preserved(self):self.assert_parity(' \n '+SOURCE+' \n',context=CTX,expected='PASS')
    def test_malformed_json_ast_is_fail(self):self.assert_parity('{bad',fmt='json_ast',expected='FAIL')
    def test_json_ast_known_fixture(self):
        text=(FIX/'migration.ast.json').read_text(encoding='utf-8')
        r=self.assert_parity(text,fmt='json_ast',context=CTX,expected='PASS')
        self.assertEqual(r['report']['checks']['syntax']['status'],'NOT_EVALUATED')
    def test_method_profile_with_context(self):
        text=(FIX/'semantic/example-method.acg').read_text(encoding='utf-8')
        self.assert_parity(text,context=METHOD_CTX)
    def test_qualified_profile_with_context(self):
        text=(FIX/'semantic/example-qualified.acg').read_text(encoding='utf-8')
        self.assert_parity(text,context=METHOD_CTX,profiles=PROFILE)
    def test_json_binding_digest_is_canonical_and_stable(self):
        a=p1.validate(SOURCE,context=CTX)
        b=p1.validate(SOURCE,context=dict(reversed(list(CTX.items()))))
        self.assertEqual(a['declared_context_sha256'],b['declared_context_sha256'])
        self.assertEqual(a['report'],b['report'])
    def test_absent_context_digest_null(self):
        a=p1.validate(SOURCE)
        self.assertIsNone(a['declared_context_sha256'])
        self.assertIsNone(a['declared_qualification_profiles_sha256'])
    def test_source_input_bytes_stable(self):
        a=p1.validate(SOURCE)
        self.assertEqual(a['report']['input_sha256'],hashlib.sha256((FIX/'migration.acg').read_bytes()).hexdigest())
    def test_determinism_three_repeats(self):
        a=p1.validate(SOURCE,context=CTX)
        for _ in range(3):self.assertEqual(p1.validate(SOURCE,context=CTX),a)
    def test_p0_frozen_reference_unmodified(self):
        from aiaeao_mcp_local.p0_resources import verify_snapshot
        self.assertEqual(verify_snapshot()['status'],'PASS')
    def test_report_json_schema(self):
        try:import jsonschema
        except ImportError:self.skipTest('Optional independent jsonschema missing')
        schema=json.loads((ROOT/'P1/contract-v1/contract/report.schema.json').read_text())
        for text,context in [(SOURCE,CTX),(SOURCE,None),('no syntax',None)]:
            jsonschema.Draft202012Validator(schema).validate(report(text,context=context))
    def test_cli_exit3_config_is_not_semantic_fail(self):
        bad=copy.deepcopy(CTX);bad['source_kind']='trusted'
        self.assertEqual(cli(SOURCE,context=bad)[0],3)
        with self.assertRaises(p1.P1AdapterFailure) as c:p1.validate(SOURCE,context=bad)
        self.assertEqual(c.exception.diagnostic['code'],'P1_MCP_CONFIG_INVALID')


class P1NegativeTests(unittest.TestCase):
    def check_error(self,code,*args,**kwargs):
        with self.assertRaises(p1.P1AdapterFailure) as caught:p1.validate(*args,**kwargs)
        r=caught.exception.diagnostic
        self.assertEqual(r['code'],code)
        self.assertEqual(r['semantic_status'],'NOT_EVALUATED')
        self.assertEqual(r['files_written'],False)
        self.assertNotIn('/Users/',str(r))
        return r
    def test_input_wrong_type(self):self.check_error('P1_MCP_INPUT_INVALID',123)
    def test_input_none(self):self.check_error('P1_MCP_INPUT_INVALID',None)
    def test_input_boolean(self):self.check_error('P1_MCP_INPUT_INVALID',True)
    def test_invalid_format(self):self.check_error('P1_MCP_FORMAT_INVALID',SOURCE,'html')
    def test_context_wrong_type(self):self.check_error('P1_MCP_CONTEXT_INVALID',SOURCE,context=[])
    def test_profiles_wrong_type(self):self.check_error('P1_MCP_PROFILE_INVALID',SOURCE,qualification_profiles=[])
    def test_context_unknown_fields(self):
        c=copy.deepcopy(CTX);c['unknown']='abc'
        self.check_error('P1_MCP_CONFIG_INVALID',SOURCE,context=c)
    def test_context_nan(self):
        c=copy.deepcopy(CTX);c['bad']=float('nan')
        self.check_error('P1_MCP_INPUT_INVALID',SOURCE,context=c)
    def test_profiles_unsupported_format(self):
        p=copy.deepcopy(PROFILE);p['format']='unsupported'
        self.check_error('P1_MCP_CONFIG_INVALID',SOURCE,qualification_profiles=p)
    def test_text_exceeds_cli_limit(self):
        self.check_error('P1_MCP_TEXT_TOO_LARGE','x'*(1024*1024+1))
    def test_request_exceeds_transport_limit(self):
        c=copy.deepcopy(CTX);c['extra']='x'*(2*1024*1024+1)
        self.check_error('P1_MCP_INPUT_TOO_LARGE',SOURCE,context=c)
    def test_input_no_leak_of_sensitive_text(self):
        c=copy.deepcopy(CTX);c['source_kind']='/Users/example/PrivateSecret'
        r=self.check_error('P1_MCP_CONFIG_INVALID',SOURCE,context=c)
        self.assertNotIn('PrivateSecret',str(r))
    def test_reference_exception_fails_closed(self):
        from cube_resolver.resolver import ContractError
        with patch.object(p1,'SemanticValidator',side_effect=ContractError('/Users/private/LocalSecret')):
            r=self.check_error('P1_MCP_CONFIG_INVALID',SOURCE)
            self.assertNotIn('LocalSecret',str(r))
    def test_no_implicit_p2_effect(self):
        from unittest.mock import patch
        with patch.object(bridge,'render_svg',side_effect=AssertionError('Must not print')):
            self.assertEqual(p1.validate(SOURCE)['report']['overall_status'],'UNRESOLVED')
    def test_fail_is_not_mcp_failure(self):
        result=p1.validate('invalid syntax')
        self.assertEqual(result['report']['overall_status'],'FAIL')
    def test_unresolved_is_not_mcp_failure(self):
        result=p1.validate(SOURCE)
        self.assertEqual(result['report']['overall_status'],'UNRESOLVED')
    def test_mcp_response_body_is_json_safe(self):
        for result in (p1.validate(SOURCE),p1.validate('invalid')):
            encoded=json.dumps(result,ensure_ascii=False,allow_nan=False)
            self.assertEqual(json.loads(encoded),result)
    def test_legacy_printer_capabilities_unmodified(self):
        caps=bridge.get_capabilities()
        self.assertFalse(caps['adapter']['p1_validation'])
        self.assertEqual(len(caps['adapter']['tools']),4)
        self.assertEqual(caps['adapter']['version'],'P3-MCP-LOCAL/0.1.1')

if __name__=='__main__':unittest.main()
