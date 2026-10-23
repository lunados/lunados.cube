#!/usr/bin/env python3
"""Independent black-box contract oracle. Calls executable via subprocess ONLY.

Expected statuses are manually specified in P1.1 and independent_vectors.json,
never generated from parser/resolver/validator implementation.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=ROOT/'contract-v1'
V=ROOT/'semantic-validator-v1'
ORACLE=ROOT/'release-v1'/'oracles'/'independent_vectors.json'
P0=Path(__file__).resolve().parents[3]/'AIAEAO_Pure_Cube_P0_v9.4'

class Conformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=[]
        cls.schema=None
        try:
            import jsonschema
            cls.schema=json.loads((C/'contract'/'report.schema.json').read_text(encoding='utf-8'))
            cls.jsonschema=jsonschema
        except ImportError:
            cls.jsonschema=None

    def run_cli(self,raw:bytes,context=None,qp=None,fmt='acg_text',seed=None):
        cmd=[sys.executable,'-S','-m','cube_semantic','--input','-','--input-format',fmt]
        if context:cmd+=['--context',str(V/context)]
        if qp:cmd+=['--qualification-profiles',str(V/qp)]
        env=os.environ.copy();env['PYTHONPATH']=str(V);env['PYTHONDONTWRITEBYTECODE']='1'
        if seed is not None:env['PYTHONHASHSEED']=str(seed)
        p=subprocess.run(cmd,input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=V,env=env,timeout=12)
        self.assertNotEqual(p.returncode,3,p.stderr.decode('utf8','replace'))
        try: report=json.loads(p.stdout)
        except ValueError as e:raise AssertionError((p.stdout,p.stderr)) from e
        self.assertIn(report['overall_status'],('PASS','FAIL','UNRESOLVED'))
        self.assertEqual(p.returncode,{'PASS':0,'UNRESOLVED':1,'FAIL':2}[report['overall_status']])
        if self.jsonschema:
            self.jsonschema.Draft202012Validator(self.schema).validate(report)
        else:
            self.assertEqual(set(report['checks']),{
                'syntax','structure','concept_resolution','referent_binding','predicate_typing',
                'method_typing','qualifier_typing','scope_consistency'})
        for k in ('epistemic_warrant','current_authority','canonical_admission'):
            self.assertEqual(report[k],'NOT_EVALUATED',(k,report))
        return report

    def assert_case(self,case,raw):
        r=self.run_cli(raw,case.get('context'),case.get('qualification_profiles'),case.get('input_format','acg_text'))
        self.assertEqual(r['overall_status'],case['expected_overall'],case['id'])
        for stage,status in case.get('expected_checks',{}).items():
            self.assertEqual(r['checks'][stage]['status'],status,(case['id'],stage))
        if case.get('expected_diagnostic_code'):
            self.assertIn(case['expected_diagnostic_code'],[d['code'] for d in r['diagnostics']],case['id'])
        if case.get('expect_code'):
            self.assertIn(case['expect_code'],[d['code'] for d in r['diagnostics']],case['id'])
        if case.get('expect_check'):
            self.assertEqual(r['checks'][case['expect_check']]['status'],'PASS',case['id'])
        # Three different interpreter hash seeds must produce byte-identical reports.
        if case['id'] in {'F01','F03','F10','I03-invert-direction','I13-time-observer-fixture'}:
            again=self.run_cli(raw,case.get('context'),case.get('qualification_profiles'),case.get('input_format','acg_text'),seed=11)
            again2=self.run_cli(raw,case.get('context'),case.get('qualification_profiles'),case.get('input_format','acg_text'),seed=9123)
            self.assertEqual(r,again,case['id']);self.assertEqual(r,again2,case['id'])
        self.records.append(case['id'])

    def test_01_p11_frozen_acceptance_oracle(self):
        d=json.loads((C/'fixtures'/'conformance_cases.json').read_text(encoding='utf8'))
        self.assertEqual(len(d['cases']),25)
        for case in d['cases']:
            with self.subTest(id=case['id']):
                if 'input_text' in case:raw=case['input_text'].encode('utf8')
                elif case['input'].startswith('v9.4/'):
                    # Literal published P0 reference, not a P1-generated Golden AST.
                    raw=(P0/case['input']).read_bytes()
                else:raw=(V/case['input']).read_bytes()
                mapped=dict(case)
                if 'context' in mapped and mapped['context']:mapped['context']='baseline/P1_1_Contract_Freeze/'+mapped['context']
                self.assert_case(mapped,raw)

    def test_02_additional_independent_cases(self):
        cases=json.loads(ORACLE.read_text(encoding='utf8'))['cases']
        self.assertGreaterEqual(len(cases),20)
        for c in cases:
            with self.subTest(id=c['id']):
                raw=c['input_text'].encode('utf8') if 'input_text' in c else (V/c['input_file']).read_bytes()
                self.assert_case(c,raw)

    def test_03_strict_lexical_matrix(self):
        # Invalid forms independent from the implementation parser tests.
        invalid=[b'Y:\xce\xb1:Artifact["x"]@T(role=NaN)',
                 b'Y:\xce\xb1:Artifact["x"]\nY:\xce\xb1:Artifact["y"]',
                 b'Y:\xce\xb1:Artifact["x"]@T(role="occurrence",role="recording")',
                 b'Y:\xce\xb1:Artifact["\xff"]',
                 b'Y:\xce\xb1:Artifact["x"] /*comment*/',
                 b'Y:\xce\xb1:Artifact["x"]@T(role="scheduling",offset=Infinity)',
                 b'Y:\xce\xb1:Artifact["x"]@O(delivered=True)',
                 b'Y:\xce\xb1:Artifact["x"]@T(role="occurrence",x=01)',
                 b'Y:\xce\xb1:Artifact["x"]@T(role="occurrence",x=1.)',
                 b'Y:\xce\xb1:Artifact["x"]@T(role="occurrence",x=.1)']
        for i,raw in enumerate(invalid):
            with self.subTest(index=i):
                r=self.run_cli(raw)
                self.assertEqual(r['checks']['syntax']['status'],'FAIL')
                self.assertEqual(r['overall_status'],'FAIL')

    def test_04_metamorphic_equivalence_and_non_implication(self):
        m=(V/'fixtures'/'migration.acg').read_bytes()
        c='fixtures/migration.binding-context.json'
        full=self.run_cli(m,c)
        # Whitespace between tokens has no semantic significance, but input digest changes.
        noisy=b'  \n'+m+b'  \n'
        r=self.run_cli(noisy,c)
        self.assertEqual(r['overall_status'],full['overall_status'])
        self.assertEqual({k:v['status'] for k,v in r['checks'].items()},
                         {k:v['status'] for k,v in full['checks'].items()})
        self.assertNotEqual(r['input_sha256'],full['input_sha256'])
        # Replacing context by no context must not retain descriptive PASS.
        no_context=self.run_cli(m)
        self.assertEqual(no_context['overall_status'],'UNRESOLVED')
        # Changing a declarative predicate to a causality name cannot grant causation.
        cause=self.run_cli(m.replace(b'"references"',b'"causedBy"'),c)
        self.assertEqual(cause['checks']['predicate_typing']['status'],'UNRESOLVED')
        # Timestamps and modes are never evidence or permission.
        test=b'Y:\xce\xb1:Artifact["example:migration-plan"]@O(delivered=true)'
        delivered=self.run_cli(test,c)
        self.assertEqual(delivered['checks']['qualifier_typing']['status'],'UNRESOLVED')
        self.assertEqual(delivered['current_authority'],'NOT_EVALUATED')

    def test_05_source_locks_and_freeze(self):
        locks=json.loads((C/'contract'/'source_lock.json').read_text(encoding='utf8'))['sources']
        aliases={'P0/v9.4/':'v9.4/','Morphology v9.4 source':'v9.4/morphology.md'}
        for item in locks:
            name=item['name']
            if name=='Morphology v9.4 source':path=P0/'v9.4/morphology.md'
            elif name.startswith('P0/v9.4/'):path=P0/name.removeprefix('P0/')
            else:continue
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['sha256'],name)
        # Contract copied into baseline by P1.4 must remain byte-for-byte original.
        old=V/'baseline'/'P1_1_Contract_Freeze'
        for f in C.rglob('*'):
            if f.is_file():
                rel=f.relative_to(C)
                self.assertEqual(f.read_bytes(),(old/rel).read_bytes(),str(rel))
        d=json.loads((V/'DIAGNOSTIC_EXTENSION.json').read_text(encoding='utf8'))
        self.assertEqual([x['code'] for x in d['codes']],['P1_QUALIFIER_SIGNATURE'])

if __name__=='__main__':unittest.main()
