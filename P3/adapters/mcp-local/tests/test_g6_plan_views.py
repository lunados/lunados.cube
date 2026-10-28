"""G6 offline tests: plan-view tools, limits, diagnostics, surface and CLI parity; no MCP SDK transport needed."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]; ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE/'scripts'))
from aiaeao_mcp_local import plan_views as PV, surface, bridge  # noqa: E402
import run_vectors_g6 as RV  # noqa: E402

G73 = json.loads((ROOT/'P2/visual-printer-migration-v1/fixtures/golden_v073.json').read_text('utf-8'))
GSEQ = json.loads((ROOT/'P2/visual-printer-sequence-v1/fixtures/golden_sequence.json').read_text('utf-8'))


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except PV.PlanFailure as e:
        return e.diagnostic['code']
    return 'PASS'


def src73():
    return PV.plan_source(G73['context'], G73['plan_id'], 'vpmigration')['source']


class Vectors(unittest.TestCase):
    def test_k01_k18(self):
        for cid in sorted(RV.VEC):
            with self.subTest(cid):
                status, out = RV.run(cid)
                self.assertTrue(RV.check(cid, status, out), (status, out.get('code') if status == 'ERROR' else out))


class Rows(unittest.TestCase):
    """One test per §2 row."""
    def test_printer_error_passes_through(self):
        with self.assertRaises(PV.PlanFailure) as cm:
            PV.plan_views(src73(), 'cube.phases', 'standard', partition='banana')
        d = cm.exception.diagnostic
        self.assertEqual(d['code'], 'VP07_PANEL_PARTITION')
        self.assertEqual((d['printer'], d['input_profile']), ('vpmigration', 'P2-VP-MIGRATION/0.7.3'))
        self.assertEqual(d['format'], 'aiaeao.cube.vp07-diagnostic/1')          # unchanged printer diagnostic

    def test_input_invalid(self):
        self.assertEqual(code_of(PV.plan_views, {'x': float('nan')}, 'cube.phases', 'standard', partition='subject'), 'P3_PLAN_INPUT_INVALID')
        s = src73()
        with patch.object(PV, 'MAX_REQUEST_BYTES', 1000):
            self.assertEqual(code_of(PV.plan_views, s, 'cube.phases', 'standard', partition='subject'), 'P3_PLAN_INPUT_INVALID')

    def test_view_unknown(self):
        self.assertEqual(code_of(PV.plan_views, src73(), 'cube.gantt', 'standard'), 'P3_PLAN_VIEW_UNKNOWN')

    def test_argument_invalid(self):
        s = src73()
        self.assertEqual(code_of(PV.plan_views, s, 'cube.phases', 'standard', partition='subject', rows='F'), 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code_of(PV.plan_views, s, 'cube.flow', 'standard', partition='subject'), 'P3_PLAN_ARGUMENT_INVALID')   # lens missing
        self.assertEqual(code_of(PV.plan_views, GSEQ['sequence_source'], 'cube.phases', 'standard', partition='subject'), 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code_of(PV.plan_source, G73['context'], G73['plan_id'], 'vpaxes', edge_styles=[]), 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code_of(PV.plan_check, {'printer': 'vp06'}), 'P3_PLAN_ARGUMENT_INVALID')

    def test_source_unsupported(self):
        self.assertEqual(code_of(PV.plan_source, G73['context'], G73['plan_id'], 'vpsequence'), 'P3_PLAN_SOURCE_UNSUPPORTED')

    def test_svg_too_large(self):
        s = src73()
        with patch.object(PV, 'MAX_SVG_BYTES', 4096):
            with self.assertRaises(PV.PlanFailure) as cm:
                PV.plan_views(s, 'cube.phases', 'standard', partition='subject')
        d = cm.exception.diagnostic
        self.assertEqual(d['code'], 'P3_PLAN_SVG_TOO_LARGE')
        self.assertGreater(d['size_bytes'], d['limit_bytes'])
        self.assertIn('nothing was truncated', d['hint'])

    def test_response_too_large(self):
        s = src73()
        with patch.object(PV, 'MAX_RESPONSE_BYTES', 50_000):
            self.assertEqual(code_of(PV.plan_views, s, 'cube.phases', 'standard', partition='subject'), 'P3_PLAN_RESPONSE_TOO_LARGE')

    def test_check_modified(self):
        res = PV.plan_views(src73(), 'cube.phases', 'standard', partition='subject')
        res['report']['coverage']['units_total'] += 1
        self.assertEqual(code_of(PV.plan_check, res), 'VP07_PANEL_COVERAGE')
        self.assertEqual(code_of(PV.plan_check, {'printer': 'vpaxes', 'format': 'x'}), 'VP09_PANEL_COVERAGE')


class Contract(unittest.TestCase):
    def test_result_shape_and_digests(self):
        import hashlib
        res = PV.plan_views(src73(), 'cube.phases', 'standard', partition='subject')
        self.assertEqual((res['format'], res['printer'], res['view']), ('aiaeao.cube.plan-views/1', 'vpmigration', 'cube.phases'))
        for p in res['panels']:
            self.assertEqual(hashlib.sha256(p['svg'].encode('utf-8')).hexdigest(), p['sha256'])
        self.assertEqual(PV.plan_check(res)['status'], 'PASS')

    def test_no_files_written(self):
        before = sorted(str(p) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts)
        PV.plan_check(PV.plan_views(src73(), 'cube.flow', 'standard', partition='subject', lens='cube.lens.execution'))
        after = sorted(str(p) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts)
        self.assertEqual(before, after)

    def test_sequence_and_axes_via_tools(self):
        r8 = PV.plan_views(GSEQ['sequence_source'], 'cube.sequence', 'standard', partition='use_case')
        self.assertEqual(PV.plan_check(r8)['status'], 'PASS')
        gax = json.loads((ROOT/'P2/visual-printer-axes-v1/fixtures/golden_axes.json').read_text('utf-8'))
        r9 = PV.plan_views(PV.plan_source(gax['context'], gax['plan_id'], 'vpaxes')['source'], 'cube.axes', 'standard', rows='Z:referent', cols='T')
        self.assertEqual(PV.plan_check(r9)['printer'], 'vpaxes')
        # VP-09 reads VP-07 sources 0.7.1/0.7.2 only: a 0.7.3 source reaches the printer and gets its own error (MP-2)
        self.assertEqual(code_of(PV.plan_views, src73(), 'cube.axes', 'standard', rows='Z:referent', cols='T'), 'VP09_SOURCE_INVALID')


class Surface(unittest.TestCase):
    def test_local_surface(self):
        card = surface.discover_surface_local()
        self.assertEqual(card['mcp']['tools'], list(surface.TOOLS_G6))
        pv = card['domains']['P2']['plan_views']
        self.assertEqual(pv['limits']['max_svg_bytes'], 512*1024)
        self.assertIs(pv['remote_available'], False)
        self.assertIn('P2-VP-MIGRATION/0.7.4', pv['printers']['vpmigration']['profiles'])

    def test_g4_base_and_legacy_unchanged(self):
        base = surface.discover_surface()
        self.assertEqual(base['mcp']['tools'], list(surface.TOOLS))         # what G5 derives its remote surface from
        self.assertEqual(base['release']['version'], 'P3-MCP-LOCAL/0.2.0-rc1')
        self.assertNotIn('plan_views', base['domains']['P2'])
        self.assertEqual(bridge.get_capabilities()['adapter']['tools'], list(surface.PRINTER_TOOLS))

    def test_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema not installed')
        schema = json.loads((BASE/'spec/G4_CAPABILITY_SURFACE.schema.json').read_text('utf-8'))
        jsonschema.validate(surface.discover_surface(), schema)
        jsonschema.validate(surface.discover_surface_local(), schema)


class C12(unittest.TestCase):
    """C-12 in G6: new profiles and display options through the plan tools (parity: parity_g6.py, O and H vectors)."""
    def test_discovery_lists_profiles_and_options(self):
        pv = surface.discover_surface_local()['domains']['P2']['plan_views']
        self.assertIn('P2-VP-MIGRATION/0.7.5', pv['printers']['vpmigration']['profiles'])
        self.assertIn('P2-VP-AXES/0.9.2', pv['printers']['vpaxes']['profiles'])
        d = pv['display_options']
        self.assertEqual(d['vpmigration']['locale'], ['de', 'en'])
        self.assertEqual(d['vpmigration']['selections'], ['method-sets'])
        self.assertEqual(d['vpaxes']['hide_empty'], ['rows', 'cols', 'both'])
        self.assertNotIn('plan_views', surface.discover_surface()['domains']['P2'])     # G5 base unchanged

    def test_vp075_options_via_tools(self):
        s = PV.plan_source(G73['context'], G73['plan_id'], 'vpmigration', profile='P2-VP-MIGRATION/0.7.5')['source']
        res = PV.plan_views(s, 'cube.phases', 'standard', partition='method-sets', locale='de', hide_ledger=True)
        self.assertEqual(res['report']['locale']['code'], 'de')
        self.assertIs(res['report']['ledger_hidden'], True)
        self.assertTrue(all(x['status'] == 'COMPLETE' for x in res['report']['method_sets'].values()))
        self.assertEqual(PV.plan_check(res)['status'], 'PASS')
        self.assertEqual(code_of(PV.plan_views, src73(), 'cube.phases', 'standard', partition='subject', locale='de'), 'VP07_LOCALE_INVALID')
        self.assertEqual(code_of(PV.plan_views, s, 'cube.phases', 'standard', partition='subject', hide_empty='both'), 'P3_PLAN_ARGUMENT_INVALID')

    def test_vp092_options_via_tools(self):
        g = json.loads((ROOT/'P2/visual-printer-axes-v1/fixtures/golden_v092.json').read_text('utf-8'))
        s = PV.plan_source(g['context'], g['plan_id'], 'vpaxes', profile='P2-VP-AXES/0.9.2')['source']
        res = PV.plan_views(s, 'cube.axes', 'standard', rows='Y:referent', cols='Y:referent', hide_empty='both', locale='de')
        self.assertEqual(res['report']['hidden_cols'], ['acme:ops-desk'])
        self.assertEqual(PV.plan_check(res)['status'], 'PASS')
        with self.assertRaises(PV.PlanFailure) as cm:
            PV.plan_views(s, 'cube.axes', 'standard', rows='Q', cols='T')
        self.assertEqual((cm.exception.diagnostic['profile'], cm.exception.diagnostic['input_profile']), ('P2-VP-AXES/0.9.2', 'P2-VP-AXES/0.9.2'))
        self.assertEqual(code_of(PV.plan_views, s, 'cube.axes', 'standard', rows='F', cols='T', hide_ledger=True), 'P3_PLAN_ARGUMENT_INVALID')


class Server(unittest.TestCase):
    def test_tools_registered_and_text_equals_structured(self):
        try:
            from aiaeao_mcp_local import server
        except ImportError:
            self.skipTest('MCP SDK not installed')
        res = server.cube_plan_source(G73['context'], G73['plan_id'], 'vpsequence')
        self.assertTrue(res.is_error)
        self.assertEqual(json.loads(res.content[0].text), res.structured_content)
        ok = server.cube_plan_views(src73(), 'cube.phases', 'standard', partition='subject')
        self.assertFalse(ok.is_error)
        self.assertEqual(ok.content[0].text.encode('utf-8'), PV.canonical(ok.structured_content))
        s75 = PV.plan_source(G73['context'], G73['plan_id'], 'vpmigration', profile='P2-VP-MIGRATION/0.7.5')['source']
        de = server.cube_plan_views(s75, 'cube.flow', 'standard', partition='subject', lens='cube.lens.execution', locale='de', hide_ledger=True)
        self.assertFalse(de.is_error)
        self.assertIs(de.structured_content['report']['ledger_hidden'], True)


if __name__ == '__main__':
    unittest.main()
