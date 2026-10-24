"""G3 tests deliberately outside test_*.py to keep G2's fixed 137-test gate intact."""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from pathlib import Path
from aiaeao_mcp_local import bridge, g3_receipt as g3, p0_tool, p1_adapter

ROOT = Path(__file__).resolve().parents[4]
P1=ROOT/'P1/semantic-validator-v1/fixtures'
P2=ROOT/'P2/visual-printer-release-v1/examples'
P0_URI='https://cube.lunados.net/v9.4/grammar/concepts.json'
INDEX_URI='aiaeao://p0/resources/v1'
ACG=(P1/'migration.acg').read_text(encoding='utf-8')
CTX=json.loads((P1/'migration.binding-context.json').read_text(encoding='utf-8'))
BUNDLE=json.loads((P2/'flow_provenance_standard.vp03.bundle.json').read_text(encoding='utf-8'))
JOB_GOLD=json.loads((P2/'flow_provenance_standard.job.json').read_text(encoding='utf-8'))
REPORT_GOLD=json.loads((P2/'flow_provenance_standard.report.json').read_text(encoding='utf-8'))
SVG_GOLD=(P2/'flow_provenance_standard.svg').read_bytes()


def fixture():
    index=p0_tool.read_reference(INDEX_URI)
    page=p0_tool.read_reference(P0_URI,max_bytes=32768)
    p0=g3.verify_p0(index,P0_URI,[page])
    good=p1_adapter.validate(ACG,context=copy.deepcopy(CTX))
    p1=g3.verify_p1(good,ACG)
    bundle=copy.deepcopy(BUNDLE)
    job=bridge.prepare_print(bundle,'cube.lens.provenance','standard')
    check=bridge.check_print(job)
    render=bridge.render_svg(job)
    p2=g3.verify_p2(job,check,render,bundle,hashlib.sha256(SVG_GOLD).hexdigest())
    return index,page,good,job,check,render,p0,p1,p2


def assert_code(test, code, func, *args, **kw):
    with test.assertRaises(g3.G3ProofError) as err:
        func(*args,**kw)
    test.assertEqual(err.exception.code,code)


class CompleteTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index,cls.page,cls.good,cls.job,cls.check,cls.render,cls.p0,cls.p1,cls.p2=fixture()

    def test_p0_sha_independently_hashed(self):
        self.assertEqual(self.p0['content_sha256'],hashlib.sha256(self.page['content'].encode()).hexdigest())
        self.assertEqual(self.p0['bytes_read'],len(self.page['content'].encode()))
        self.assertEqual(self.p0['source_warrant'],'canonical_documentary_reference_only')
    def test_p0_index_sha_independently_hashed(self):
        self.assertEqual(self.p0['index_sha256'],hashlib.sha256(self.index['content'].encode()).hexdigest())
    def test_p1_pass_unmodified(self):
        self.assertEqual(self.p1['status'],'PASS')
        self.assertEqual(self.good['report']['overall_status'],'PASS')
        self.assertEqual(self.p1['input_sha256'],hashlib.sha256(ACG.encode()).hexdigest())
    def test_p1_report_no_authority(self):
        self.assertEqual([self.good['report'][x] for x in g3.NOT_EVALUATED_FIELDS],['NOT_EVALUATED']*3)
    def test_p2_job_golden(self):self.assertEqual(self.job,JOB_GOLD)
    def test_p2_report_golden(self):self.assertEqual(self.check,REPORT_GOLD)
    def test_p2_svg_golden(self):
        self.assertEqual(self.render['artifact']['svg_text'].encode(),SVG_GOLD)
    def test_p2_view_fields(self):
        self.assertEqual([self.p2[x] for x in ('view','lens','granularity')],
                         ['cube.flow','cube.lens.provenance','standard'])
    def test_no_implicit_mapping_even_if_p1_passes(self):
        receipt=g3.assemble(self.p0,self.p1,self.p2,scenario='declared_fixture')
        self.assertEqual(receipt['trace_status'],'COMPLETE')
        self.assertEqual(receipt['cross_domain_link'],'NOT_ESTABLISHED')
        self.assertEqual(receipt['acg_to_vp03_mapping'],'NOT_PERFORMED')
        self.assertNotIn('overall_status',receipt)
        self.assertNotIn('semantic_status',receipt)
    def test_p1_fail_does_not_block_valid_p2(self):
        fail=g3.verify_p1(p1_adapter.validate('this is not valid ACG'),'this is not valid ACG')
        receipt=g3.assemble(self.p0,fail,self.p2,scenario='p1_fail_p2_valid')
        self.assertEqual(receipt['p1']['status'],'FAIL')
        self.assertEqual(receipt['p2']['status'],'PASS')
        self.assertEqual(receipt['trace_status'],'COMPLETE')
        self.assertEqual(receipt['source_truth'],'NOT_EVALUATED')
    def test_p1_unresolved_does_not_block_valid_p2(self):
        unresolved=g3.verify_p1(p1_adapter.validate(ACG),ACG)
        receipt=g3.assemble(self.p0,unresolved,self.p2,scenario='p1_unresolved_p2_valid')
        self.assertEqual([receipt['p1']['status'],receipt['p2']['status']],['UNRESOLVED','PASS'])
    def test_g3_receipt_json_and_repeatable(self):
        r=g3.assemble(self.p0,self.p1,self.p2,scenario='declared_fixture')
        again=g3.assemble(self.p0,self.p1,self.p2,scenario='declared_fixture')
        self.assertEqual(json.dumps(r,sort_keys=True),json.dumps(again,sort_keys=True))
        self.assertEqual(r['format'],g3.FORMAT)
    def test_receipt_no_local_paths(self):
        self.assertNotIn(str(ROOT),json.dumps(g3.assemble(self.p0,self.p1,self.p2,scenario='declared_fixture')))
    def test_core_unchanged_and_no_new_mcp_tool(self):
        self.assertEqual(len(bridge.TOOL_NAMES),4)
        self.assertEqual(len([*g3.CHECKS]),8)
    def test_p1_not_called_when_p2_printed(self):
        from unittest.mock import patch
        with patch.object(p1_adapter,'validate',side_effect=AssertionError('P2 must not invoke P1')):
            self.assertEqual(bridge.render_svg(self.job),self.render)
    def test_p2_not_called_when_p1_validates(self):
        from unittest.mock import patch
        with patch.object(bridge,'render_svg',side_effect=AssertionError('P1 must not invoke P2')):
            self.assertEqual(p1_adapter.validate(ACG,context=CTX),self.good)


class MultiPageIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=p0_tool.read_reference(INDEX_URI)
        cls.uri='https://cube.lunados.net/v9.4/morphology.md'
        cls.pages=[]
        offset=0
        while True:
            page=p0_tool.read_reference(cls.uri,offset=offset,max_bytes=32768)
            cls.pages.append(page)
            if page['complete']:break
            offset=page['next_offset']

    def test_morphology_all_pages_roundtrip(self):
        info=g3.verify_p0(self.index,self.uri,self.pages)
        self.assertEqual(info['pages_read'],9)
        self.assertEqual(info['bytes_read'],268040)

    def test_missing_page_fails(self):
        assert_code(self,'G3_PAGE_OFFSET_MISMATCH',g3.verify_p0,self.index,self.uri,
                    self.pages[:1]+self.pages[2:])
    def test_page_out_of_order_fails(self):
        pages=copy.deepcopy(self.pages)
        pages[0],pages[1]=pages[1],pages[0]
        assert_code(self,'G3_PAGE_OFFSET_MISMATCH',g3.verify_p0,self.index,self.uri,pages)
    def test_page_content_same_size_changed_fails(self):
        pages=copy.deepcopy(self.pages)
        page=pages[0]
        original=page['content']
        page['content']=original.replace('AIAEAO','BIAEAO',1)
        self.assertEqual(len(page['content'].encode()),len(original.encode()))
        assert_code(self,'G3_REFERENCE_DIGEST_MISMATCH',g3.verify_p0,self.index,self.uri,pages)


class TamperingAndBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index,cls.page,cls.good,cls.job,cls.check,cls.render,cls.p0,cls.p1,cls.p2=fixture()

    def test_index_tampered_bytes(self):
        x=copy.deepcopy(self.index);x['content']+=' '
        assert_code(self,'G3_INDEX_DIGEST_MISMATCH',g3.verify_p0,x,P0_URI,[self.page])
    def test_index_missing(self):
        x=copy.deepcopy(self.index);x['complete']=False
        assert_code(self,'G3_INDEX_INCOMPLETE',g3.verify_p0,x,P0_URI,[self.page])
    def test_p0_bad_uri(self):
        assert_code(self,'G3_REFERENCE_NOT_PINNED',g3.verify_p0,self.index,'https://bad.invalid/',[self.page])
    def test_p0_incorrect_page_payload(self):
        page=copy.deepcopy(self.page);page['content']='not concepts'
        assert_code(self,'G3_PAGE_SIZE_MISMATCH',g3.verify_p0,self.index,P0_URI,[page])
    def test_p0_reference_incomplete(self):
        page=copy.deepcopy(self.page);page['complete']=False
        assert_code(self,'G3_REFERENCE_INCOMPLETE',g3.verify_p0,self.index,P0_URI,[page])
    def test_p0_bad_page_start(self):
        page=copy.deepcopy(self.page);page['offset']=10
        assert_code(self,'G3_PAGE_OFFSET_MISMATCH',g3.verify_p0,self.index,P0_URI,[page])
    def test_p0_changed_digest(self):
        page=copy.deepcopy(self.page);page['sha256']='f'*64
        assert_code(self,'G3_REFERENCE_DECLARATION_MISMATCH',g3.verify_p0,self.index,P0_URI,[page])
    def test_p1_mismatched_input(self):
        assert_code(self,'G3_P1_INPUT_DIGEST_MISMATCH',g3.verify_p1,self.good,ACG+' changed')
    def test_p1_claim_truth(self):
        x=copy.deepcopy(self.good);x['report']['epistemic_warrant']='VERIFIED'
        assert_code(self,'G3_P1_AUTHORITY_CLAIM',g3.verify_p1,x,ACG)
    def test_p1_warrant_escalation(self):
        x=copy.deepcopy(self.good);x['source_warrant']='verified'
        assert_code(self,'G3_P1_WARRANT_ESCALATED',g3.verify_p1,x,ACG)
    def test_p1_unknown_status(self):
        x=copy.deepcopy(self.good);x['report']['overall_status']='VALID'
        assert_code(self,'G3_P1_STATUS_INVALID',g3.verify_p1,x,ACG)
    def test_p2_source_mutated(self):
        x=copy.deepcopy(self.job);x['source_bundle']['view_plan']['title']='tampered'
        assert_code(self,'G3_P2_BUNDLE_CHANGED',g3.verify_p2,x,self.check,self.render,BUNDLE)
    def test_p2_report_mismatch(self):
        x=copy.deepcopy(self.check);x['decision']['action']='DID_SOMETHING'
        assert_code(self,'G3_P2_CHECK_RENDER_DISAGREE',g3.verify_p2,self.job,x,self.render,BUNDLE)
    def test_p2_svg_tampered(self):
        x=copy.deepcopy(self.render);x['artifact']['svg_text']+='<!--tampered-->'
        assert_code(self,'G3_P2_SVG_SIZE_MISMATCH',g3.verify_p2,self.job,self.check,x,BUNDLE)
    def test_p2_false_warrant(self):
        x=copy.deepcopy(self.render);x['source_status']='verified_true'
        assert_code(self,'G3_P2_WARRANT_ESCALATED',g3.verify_p2,self.job,self.check,x,BUNDLE)
    def test_p2_wrong_golden(self):
        assert_code(self,'G3_P2_GOLDEN_MISMATCH',g3.verify_p2,
                    self.job,self.check,self.render,BUNDLE,'0'*64)
    def test_p2_check_claim_authority(self):
        x=copy.deepcopy(self.check);x['canonical_admission']='ADMITTED'
        r=copy.deepcopy(self.render);r['report']=x
        assert_code(self,'G3_P2_AUTHORITY_CLAIM',g3.verify_p2,self.job,x,r,BUNDLE)
    def test_wrong_domain_in_receipt(self):
        x=copy.deepcopy(self.p0);x['domain']='P2'
        assert_code(self,'G3_DOMAIN_CONFUSION',g3.assemble,x,self.p1,self.p2,scenario='declared_fixture')
    def test_contradiction_missing(self):
        assert_code(self,'G3_CONTRADICTION_NOT_TESTED',g3.assemble,self.p0,self.p1,self.p2,
                    scenario='p1_fail_p2_valid')
    def test_unresolved_missing(self):
        assert_code(self,'G3_UNRESOLVED_NOT_TESTED',g3.assemble,self.p0,self.p1,self.p2,
                    scenario='p1_unresolved_p2_valid')
    def test_no_implicit_status_elevation(self):
        r=g3.assemble(self.p0,self.p1,self.p2,scenario='declared_fixture')
        self.assertEqual([r[k] for k in ('source_truth','authority','admission')],['NOT_EVALUATED']*3)

if __name__=='__main__':unittest.main()
