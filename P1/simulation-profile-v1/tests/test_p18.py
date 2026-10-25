"""P1.8 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1','instantiation-profile-v1','simulation-profile-v1'):
    sys.path.insert(0,str(ROOT/p))
sys.dont_write_bytecode=True
from cube_p18.validator import P18Validator
from cube_p18.simulation import SimulationError
from cube_p16.validator import P16Validator
from cube_semantic.validator import SemanticValidator

HERE=ROOT/'simulation-profile-v1'
VEC={c['id']:c for c in json.loads((HERE/'fixtures/s01_s17_materialized.json').read_text())['cases']}
ORACLE={c['id']:c for c in json.loads((HERE/'oracles/independent_s01_s17.json').read_text())['cases']}
RVEC=json.loads((ROOT.parent/'P3/charge3-p16/fixtures/r01_r13_materialized.json').read_text())['cases']
V=P18Validator()
NOPROMO=('epistemic_warrant','current_authority','canonical_admission')

def run(text, ctx):
    return V.validate_bytes(text.encode(), context=ctx)

def codes(r): return [d['code'] for d in r['diagnostics']]

def case(i):
    c=VEC[i]; return c['input_text'], copy.deepcopy(c['context'])


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC),set(ORACLE)); self.assertEqual(len(VEC),17)
        for i,c in sorted(VEC.items()):
            with self.subTest(id=i):
                self.assertEqual((c['expected_overall'],c['required_codes']),
                                 (ORACLE[i]['expected_overall'],ORACLE[i]['required_codes']))
                if c['expected_overall']=='MCP_ERROR':
                    with self.assertRaises(ValueError): run(c['input_text'],c['context'])
                    continue
                r=run(c['input_text'],c['context'])
                self.assertEqual(r['overall_status'],c['expected_overall'],r)
                for code in c['required_codes']: self.assertIn(code,codes(r))
                for k in NOPROMO: self.assertEqual(r[k],'NOT_EVALUATED')
                if c['expected_overall']=='PASS': self.assertEqual(r['diagnostics'],[])


class Regression(unittest.TestCase):
    def test_v1_v2_byte_identical_to_p16(self):
        p16=P16Validator()
        for c in RVEC:
            with self.subTest(id=c['id']):
                a=V.validate_bytes(c['input_text'].encode(),context=c['context'])
                b=p16.validate_bytes(c['input_text'].encode(),context=c['context'])
                self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))
    def test_no_context_identical_to_frozen(self):
        for t in ('X:α:Event["e"]','this is not valid ACG','rel("x",Y:α:Artifact["a"],Y:α:Revision["r"])'):
            self.assertEqual(V.validate_bytes(t.encode()),SemanticValidator().validate_bytes(t.encode()))
    def test_v3_fields_in_v2_rejected(self):
        t,c=case('S-14')
        with self.assertRaises(ValueError): run(t,c)


class ReturnTyping(unittest.TestCase):
    def test_many_cardinality_as_operand_fails(self):
        t,c=case('S-01'); c['method_contracts'][0]['return_cardinality']='many'
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_METHOD_RETURN_TYPE',codes(r))
    def test_partial_return_set_not_any_of(self):
        t,c=case('S-01'); c['method_contracts'][0]['return_concept_ids']=['Y:resource-object:evidence','Y:resource-object:artifact']
        r=run(t,c); self.assertIn('P1_METHOD_RETURN_TYPE',codes(r))
    def test_object_side_application(self):
        t,c=case('S-01'); t='rel("supports",Y:α:Evidence["ev-out"],verify.qualified-reuse/v1(Y:α:Artifact["a1"]))'
        c['method_contracts'][0]['return_concept_ids']=['Y:identified-object:annotation']
        self.assertEqual(run(t,c)['overall_status'],'PASS')
    def test_reference_side_still_typed(self):
        t,c=case('S-01'); t='rel("supports",verify.qualified-reuse/v1(Y:α:Artifact["a1"]),Y:α:Artifact["a1"])'
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_PREDICATE_SIGNATURE',codes(r))
    def test_judgment_return_is_config_error(self):
        t,c=case('S-01'); c['method_contracts'][0]['return_concept_ids']=['X:endpoint:conclusion']
        with self.assertRaises(SimulationError): run(t,c)
    def test_noninstantiable_return_is_config_error(self):
        t,c=case('S-01'); c['method_contracts'][0]['return_concept_ids']=['X:dimension:semantics']
        with self.assertRaises(SimulationError): run(t,c)
    def test_return_ids_without_cardinality(self):
        t,c=case('S-01'); del c['method_contracts'][0]['return_cardinality']
        with self.assertRaises(SimulationError): run(t,c)
    def test_malformed_library_ref(self):
        t,c=case('S-01'); c['method_contracts'][0]['library_ref']['sha256']='XYZ'
        with self.assertRaises(SimulationError): run(t,c)
    def test_library_never_resolved(self):
        t,c=case('S-01'); c['method_contracts'][0]['library_ref']['library_id']='unreachable.invalid'
        self.assertEqual(run(t,c)['overall_status'],'PASS')


class Scenario(unittest.TestCase):
    def test_replay_mode_allowed(self):
        t,c=case('S-05'); c['scenarios'][0]['mode']='replay'
        self.assertEqual(run(t,c)['overall_status'],'PASS')
    def test_method_not_listed_for_scenario(self):
        t,c=case('S-05'); c['scenarios'][0]['method_ids']=['other.method/v1']
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_SCENARIO_MODE',codes(r))
    def test_scenario_scope_conflict(self):
        t,c=case('S-05'); c['scenarios'][0]['scope']='elsewhere'
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_SCOPE_CONFLICT',codes(r))
    def test_undeclared_world_member_config(self):
        t,c=case('S-05'); c['scenarios'][0]['world_refs'].append('ghost')
        with self.assertRaises(SimulationError): run(t,c)
    def test_assumption_must_be_annotation(self):
        t,c=case('S-05'); c['scenarios'][0]['assumption_refs']=['a1']
        with self.assertRaises(SimulationError): run(t,c)
    def test_parameters_scalars_only(self):
        t,c=case('S-05'); c['scenarios'][0]['parameters']={'nested':{'x':1}}
        with self.assertRaises(SimulationError): run(t,c)
    def test_without_frame_no_scenario_checks(self):
        t,c=case('S-06'); del c['evaluation_frame']
        self.assertEqual(run(t,c)['overall_status'],'PASS')


class Evaluation(unittest.TestCase):
    def test_envelope_free_report_unchanged_keys(self):
        t,c=case('S-09'); r=run(t,c)
        self.assertEqual(set(r),set(SemanticValidator().validate_bytes(b'X:\xce\xb1:Event["e"]')))
    def test_record_unknown_scenario(self):
        t,c=case('S-09'); c['evaluation_records'][0]['scenario_ref']='nope'
        self.assertIn('P1_EVALUATION_RECORD_INCONSISTENT',codes(run(t,c)))
    def test_record_method_not_in_scenario(self):
        t,c=case('S-09'); c['evaluation_records'][0]['method_id']='other.method/v1'
        r=run(t,c); self.assertIn('P1_EVALUATION_RECORD_INCONSISTENT',codes(r)); self.assertIn('P1_EVALUATOR_UNDECLARED',codes(r))
    def test_output_outside_world(self):
        t,c=case('S-09'); c['scenarios'][0]['world_refs'].remove('ev-out')
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_SCENARIO_WORLD_VIOLATION',codes(r))
    def test_output_not_declared_for_evaluator(self):
        t,c=case('S-09'); c['evaluators'][0]['output_concept_ids']=['Y:resource-object:artifact']
        self.assertIn('P1_EVALUATION_OUTPUT_TYPE',codes(run(t,c)))
    def test_judgment_in_evaluator_outputs_config(self):
        t,c=case('S-09'); c['evaluators'][0]['output_concept_ids'].append('X:endpoint:satisfaction')
        with self.assertRaises(SimulationError): run(t,c)
    def test_status_verified_is_config_error(self):
        t,c=case('S-09'); c['evaluation_records'][0]['status']='verified'
        with self.assertRaises(SimulationError): run(t,c)
    def test_result_action_outside_world(self):
        t,c=case('S-16'); c['scenarios'][0]['world_refs'].remove('run-1-action')
        self.assertIn('P1_SCENARIO_WORLD_VIOLATION',codes(run(t,c)))
    def test_result_action_wrong_type(self):
        t,c=case('S-16'); next(r for r in c['referents'] if r['ref']=='res-out')['slots']['action_ref']='eval-actor'
        r=run(t,c); self.assertEqual(r['overall_status'],'FAIL'); self.assertIn('P1_INSTANTIATION_SLOT_TYPE',codes(r))


class ReportSchema(unittest.TestCase):
    def test_reports_validate_against_frozen_schema(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest('jsonschema with Draft 2020-12 not installed')
        schema=json.loads((ROOT/'semantic-validator-v1/baseline/P1_1_Contract_Freeze/contract/report.schema.json').read_text())
        val=Draft202012Validator(schema)
        for i,c in VEC.items():
            if c['expected_overall']=='MCP_ERROR': continue
            val.validate(run(c['input_text'],c['context']))


class Golden(unittest.TestCase):
    """P1.8-15: EXP-010 and EXP-024 as declared reference cases, with negative controls."""
    G={n:json.loads((HERE/f'fixtures/golden_{n}.json').read_text()) for n in ('exp010','exp024')}
    def g(self,n): c=self.G[n]; return c['input_text'], copy.deepcopy(c['context'])
    def test_goldens_pass_without_promotion(self):
        for n,c in self.G.items():
            with self.subTest(n=n):
                r=run(c['input_text'],c['context'])
                self.assertEqual((r['overall_status'],r['diagnostics']),('PASS',[]))
                for k in NOPROMO: self.assertEqual(r[k],'NOT_EVALUATED')
                self.assertTrue(c['reference']['sources'])
    def test_exp010_operative_mode_fails(self):
        t,c=self.g('exp010'); c['scenarios'][0]['mode']='operative'
        self.assertIn('P1_SCENARIO_MODE',codes(run(t,c)))
    def test_exp010_claim_outside_world_fails(self):
        t,c=self.g('exp010'); c['scenarios'][0]['world_refs'].remove('exp010:claim-ac-saving')
        self.assertIn('P1_SCENARIO_WORLD_VIOLATION',codes(run(t,c)))
    def test_exp010_without_witness_unresolved(self):
        t,c=self.g('exp010'); del c['evaluation_records'][0]['witness_ref']
        self.assertEqual(run(t,c)['overall_status'],'UNRESOLVED')
    def test_exp024_selection_as_conclusion_fails(self):
        t,c=self.g('exp024'); c['referents'].append({'ref':'exp024:selected','concept_id':'X:endpoint:conclusion','home':'X',
            'layers':['\u03b1'],'provenance_status':'declared_unverified','scope_ref':'exp024'})
        c['scenarios'][0]['world_refs'].append('exp024:selected'); c['evaluation_records'][0]['output_refs']=['exp024:selected']
        self.assertIn('P1_EVALUATION_OUTPUT_TYPE',codes(run(t,c)))
    def test_exp024_result_without_run_unresolved(self):
        t,c=self.g('exp024'); del next(r for r in c['referents'] if r['ref']=='exp024:result-dominates')['slots']['action_ref']
        self.assertIn('P1_INSTANTIATION_SLOT_MISSING',codes(run(t,c)))
    def test_exp024_return_type_must_match_predicate(self):
        t,c=self.g('exp024'); c['method_contracts'][0]['return_concept_ids']=['Y:resource-object:evidence']
        self.assertIn('P1_METHOD_RETURN_TYPE',codes(run(t,c)))


if __name__=='__main__': unittest.main()
