"""PoC-A executable in-memory parity and security regression tests (no SDK required)."""
import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aiaeao_mcp_local import bridge
from vpprint.core import capabilities, make_job, render_job, PrintError
from vpgranularity.printer import sha

EXAMPLES=bridge.PRINTER/'examples'
BUNDLE=json.loads((EXAMPLES/'flow_provenance_standard.vp03.bundle.json').read_text())
JOB=json.loads((EXAMPLES/'flow_provenance_standard.job.json').read_text())

class BridgeParityTests(unittest.TestCase):
    def test_01_tool_names_order(self):
        self.assertEqual(bridge.TOOL_NAMES, ('cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg'))
    def test_02_capabilities_preserved(self):
        c=bridge.get_capabilities()
        self.assertEqual(c['core'],capabilities())
        self.assertFalse(c['adapter']['remote_available'])
        self.assertFalse(c['adapter']['p1_validation'])
    def test_03_no_remote_claim(self):
        c=bridge.get_capabilities()
        self.assertEqual(c['adapter']['transport'],'stdio')
        self.assertFalse(c['adapter']['http_endpoint'])
    def test_04_prepare_exact_original(self):
        self.assertEqual(bridge.prepare_print(BUNDLE,'cube.lens.provenance','standard'),
                         make_job(BUNDLE,'cube.lens.provenance','standard'))
    def test_05_prepare_matches_frozen_job(self):
        self.assertEqual(bridge.prepare_print(BUNDLE,'cube.lens.provenance','standard'), JOB)
    def test_06_check_exact_report(self):
        report,_=render_job(JOB)
        self.assertEqual(bridge.check_print(JOB),report)
    def test_07_svg_exact_bytes_and_report(self):
        report,svg=render_job(JOB)
        result=bridge.render_svg(JOB)
        self.assertEqual(result['report'],report)
        self.assertEqual(result['artifact']['svg_text'].encode('utf-8'),svg)
        self.assertEqual(result['artifact']['sha256'],hashlib.sha256(svg).hexdigest())
        self.assertEqual(result['artifact']['media_type'],'image/svg+xml')
    def test_08_parity_against_golden(self):
        svg=(EXAMPLES/'flow_provenance_standard.svg').read_bytes()
        result=bridge.render_svg(JOB)
        self.assertEqual(result['artifact']['svg_text'].encode(),svg)
        self.assertEqual(result['report'],json.loads((EXAMPLES/'flow_provenance_standard.report.json').read_text()))
    def test_09_repeat_three_times(self):
        all_outputs=[bridge.render_svg(JOB) for _ in range(3)]
        self.assertEqual(all_outputs[0],all_outputs[1]);self.assertEqual(all_outputs[0],all_outputs[2])
    def test_10_prepare_does_not_mutate_source(self):
        obj=copy.deepcopy(BUNDLE)
        bridge.prepare_print(obj,'cube.lens.provenance','standard')
        self.assertEqual(obj,BUNDLE)
    def test_11_order_is_stateless(self):
        first=bridge.check_print(JOB)
        other=json.loads((EXAMPLES/'tree_semantics_detail.job.json').read_text())
        self.assertEqual(bridge.check_print(other)['status'],'PASS')
        self.assertEqual(bridge.check_print(JOB),first)
    def test_12_output_source_status(self):
        result=bridge.render_svg(JOB)
        self.assertEqual(result['source_status'],'declared_unverified')
        self.assertEqual(result['report']['canonical_admission'],'NOT_EVALUATED')
        self.assertEqual(result['report']['current_authority'],'NOT_EVALUATED')
        self.assertEqual(result['report']['epistemic_warrant'],'NOT_EVALUATED')
    def test_13_no_silent_omission(self):
        report=bridge.check_print(JOB)
        self.assertIn('omitted_item_ids', report['loss_ledger'])
        self.assertIn('omitted_source_edge_ids', report['loss_ledger'])
    def test_14_all_four_golden_jobs(self):
        for f in sorted(EXAMPLES.glob('*.job.json')):
            with self.subTest(name=f.name):
                job=json.loads(f.read_text())
                result=bridge.render_svg(job)
                svg=(EXAMPLES/f.name.replace('.job.json','.svg')).read_bytes()
                expected=json.loads((EXAMPLES/f.name.replace('.job.json','.report.json')).read_text())
                self.assertEqual(result['artifact']['svg_text'].encode(),svg)
                self.assertEqual(result['report'],expected)
    def test_15_checks_all_three_views(self):
        for f in EXAMPLES.glob('*.job.json'):
            with self.subTest(f=f.name):
                report=bridge.check_print(json.loads(f.read_text()))
                self.assertEqual(report['status'],'PASS')

class BridgeRejectTests(unittest.TestCase):
    def assert_code(self,func,expected):
        with self.assertRaises(bridge.BridgeFailure) as got: func()
        self.assertEqual(got.exception.diagnostic['code'],expected)
        self.assertFalse(got.exception.diagnostic['files_written'])
    def test_16_missing_facet(self):
        self.assert_code(lambda:bridge.prepare_print(BUNDLE,'cube.lens.unknown','standard'),'VP06_LENS_UNKNOWN')
    def test_17_missing_declared_facet(self):
        missing=copy.deepcopy(BUNDLE)
        missing['facet_bindings']=[f for f in missing['facet_bindings'] if f['lens']!='cube.lens.provenance']
        self.assert_code(lambda:bridge.prepare_print(missing,'cube.lens.provenance','standard'),'VP06_LENS_NOT_DECLARED')
    def test_18_wrong_view(self):
        wrong=copy.deepcopy(BUNDLE); wrong['view_plan']['view']='cube.chart'
        self.assert_code(lambda:bridge.prepare_print(wrong,'cube.lens.provenance','standard'),'VP06_VIEW_INCOMPATIBLE')
    def test_19_wrong_level(self):
        self.assert_code(lambda:bridge.prepare_print(BUNDLE,'cube.lens.provenance','zoom'),'VP06_LEVEL_UNKNOWN')
    def test_20_hash_tamper(self):
        tampered=copy.deepcopy(JOB);tampered['source_bundle']['view_plan']['nodes'][0]['label']='changed'
        self.assert_code(lambda:bridge.check_print(tampered),'VP06_SOURCE_DIGEST_MISMATCH')
    def test_21_prevent_oversize(self):
        huge=copy.deepcopy(BUNDLE);huge['garbage']='x'*(bridge.MAX_REQUEST_BYTES+1)
        self.assert_code(lambda:bridge.prepare_print(huge,'cube.lens.provenance','standard'),'VP06_INPUT_TOO_LARGE')
    def test_22_nonfinite(self):
        huge=copy.deepcopy(BUNDLE);huge['nonfinite']=float('nan')
        self.assert_code(lambda:bridge.prepare_print(huge,'cube.lens.provenance','standard'),'VP06_INPUT_INVALID')
    def test_23_no_bool_budget(self):
        self.assert_code(lambda:bridge.prepare_print(BUNDLE,'cube.lens.provenance','standard',max_items=True),'VP06_BUDGET_INCOMPATIBLE')
    def test_24_budget_zero(self):
        self.assert_code(lambda:bridge.prepare_print(BUNDLE,'cube.lens.provenance','standard',max_edges=0),'VP06_BUDGET_INCOMPATIBLE')
    def test_25_bad_focus(self):
        self.assert_code(lambda:bridge.prepare_print(BUNDLE,'cube.lens.provenance','standard',focus={'kind':'file','id':'x'}),'VP06_FOCUS_INVALID')
    def test_26_bad_job_type(self):
        self.assert_code(lambda:bridge.render_svg([]),'VP06_INPUT_INVALID')
    def test_27_no_filesystem_tools(self):
        for tool in bridge.TOOL_NAMES:
            self.assertNotIn('file',tool);self.assertNotIn('shell',tool)
    def test_28_guard_malformed_xml(self):
        self.assert_code(lambda:bridge._guard_svg(b'<svg><invalid'), 'VP06_UNSAFE_SVG')
    def test_29_guard_external_ref(self):
        self.assert_code(lambda:bridge._guard_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://evil.test/x"/></svg>'), 'VP06_UNSAFE_SVG')
    def test_30_guard_script(self):
        self.assert_code(lambda:bridge._guard_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'), 'VP06_UNSAFE_SVG')
    def test_31_guard_event(self):
        self.assert_code(lambda:bridge._guard_svg(b'<svg xmlns="http://www.w3.org/2000/svg" onload="evil()"/>'), 'VP06_UNSAFE_SVG')
    def test_32_guard_output_budget(self):
        self.assert_code(lambda:bridge._guard_svg(b'a'*(bridge.MAX_SVG_BYTES+1)), 'VP06_OUTPUT_TOO_LARGE')
    def test_33_reject_inline_unsafe_script_text(self):
        # Inject text into properly rebound source, then exercise real printer escaping.
        altered=copy.deepcopy(BUNDLE)
        altered['view_plan']['nodes'][0]['label']='<script>alert("x")</script>&hello'
        altered['source_view_sha256']=sha(altered['view_plan'])
        job=bridge.prepare_print(altered,'cube.lens.provenance','standard')
        svg=bridge.render_svg(job)['artifact']['svg_text']
        self.assertNotIn('<script>',svg)
        self.assertIn('&lt;script&gt;',svg)
    def test_34_rejected_inputs_never_write_files(self):
        with tempfile.TemporaryDirectory() as temp:
            before=set(Path(temp).iterdir())
            self.assert_code(lambda:bridge.render_svg({'junk':temp}),'VP06_REQUEST_REJECTED')
            self.assertEqual(set(Path(temp).iterdir()),before)
    def test_35_guard_url_css(self):
        self.assert_code(lambda:bridge._guard_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(http://evil.test)"/></svg>'),'VP06_UNSAFE_SVG')
    def test_36_reject_undeclared_source_change(self):
        altered=copy.deepcopy(JOB);altered['projection']['lens']='cube.lens.unknown'
        self.assert_code(lambda:bridge.render_svg(altered),'VP06_LENS_UNKNOWN')

if __name__=='__main__':unittest.main()
