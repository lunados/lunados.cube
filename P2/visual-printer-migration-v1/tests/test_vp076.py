"""VP-07.6 fixed OL oracle, per-edge display, G6/CLI parity and safety checks."""
import copy
import inspect
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'P3/adapters/mcp-local'))
sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402
from aiaeao_mcp_local import server as g6_server  # noqa: E402
from vpmigration.common import NS, P076, DASH  # noqa: E402

VEC = {c['id']: c for c in json.loads((HERE / 'fixtures/ol01_ol12_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_ol01_ol12.json').read_text())['cases']}
HEADER = 'CUBE.FLOW · FIXTURE ASSERTIONS · no inferred chronology or causality'


def run(case):
    source = g6.plan_source(**case['plan_source'])
    return source, g6.plan_views(source['source'], **case['plan_views'])


def edges(result):
    for panel in result['panels']:
        root = ET.fromstring(panel['svg'])
        for group in root.iter(f'{{{NS}}}g'):
            if group.get('data-vp07-origin') is not None:
                yield group


class OriginOracle(unittest.TestCase):
    def test_g6_registered_source_option(self):
        params = inspect.signature(g6_server.cube_plan_source).parameters
        self.assertIn('origin_lines', params)
        self.assertIn('P2-VP-MIGRATION/0.7.6', g6.capabilities()['printers']['vpmigration']['profiles'])

    def test_fixed_oracle_and_edge_text(self):
        self.assertEqual(set(VEC), set(ORACLE))
        self.assertEqual(len(VEC), 13)
        for id, case in VEC.items():
            with self.subTest(id=id):
                o = ORACLE[id]
                self.assertEqual((case['expected_status'], case['required_codes'], case['edges'], case['also']),
                                 (o['expected_status'], o['required_codes'], o['edges'], o['also']))
                if o['expected_status'] == 'FAIL':
                    with self.assertRaises(g6.PlanFailure) as error:
                        run(case)
                    self.assertIn(error.exception.diagnostic['code'], o['required_codes'])
                    continue
                source, result = run(case)
                report = result['report']
                self.assertEqual((report['status'], report['profile']), ('PASS', P076))
                self.assertTrue(set(o['required_codes']) <= {w['code'] for w in report['warnings']})
                ledger = {e['cell_id']: e for e in report['origin_ledger']}
                for expected in o['edges']:
                    if 'other_dependencies' in expected:
                        for key, row in ledger.items():
                            if key not in ('m01a', 'm01b'):
                                self.assertEqual((row['origin'], row['style'], row['text']),
                                                 (expected['other_dependencies'], expected['style'], expected['text']))
                        continue
                    key = expected.get('edge', expected.get('edge_dependency'))
                    self.assertIn(key, ledger)
                    self.assertEqual((ledger[key]['origin'], ledger[key]['style'], ledger[key]['text']),
                                     (expected['origin'], expected['style'], expected['text']))
                byref = {e['declaration_ref']: e for e in ledger.values()}
                seen = set()
                for group in edges(result):
                    ref = group.get('data-declaration-ref')
                    self.assertIn(ref, byref)
                    entry = byref[ref]; seen.add(ref)
                    self.assertEqual(group.get('data-vp07-origin'), entry['origin'])
                    self.assertEqual(group.get('data-vp07-edge-style'), entry['style'])
                    label = group.find(f'{{{NS}}}text')
                    self.assertIn(entry['text'], label.text)
                    self.assertIn(entry['predicate_id'], label.text)
                    for line in group.findall(f'{{{NS}}}line'):
                        self.assertEqual(line.get('stroke-dasharray'), DASH.get(entry['style']))
                self.assertEqual(seen, set(byref))
                for panel in result['panels']:
                    root = ET.fromstring(panel['svg'])
                    texts = [t.text for t in root.iter(f'{{{NS}}}text')]
                    self.assertIn(HEADER, texts)
                    self.assertEqual(len([g for g in root.iter(f'{{{NS}}}g')
                                          if g.get('data-vp07-origin-legend')]), 1)
                    self.assertTrue(any('origin unknown' in (t or '') for t in texts) if id != 'OL-11'
                                    else any('Herkunft unbekannt' in (t or '') for t in texts))
                    self.assertTrue(any('origin not bound' in (t or '') for t in texts) if id != 'OL-11'
                                    else any('Herkunft nicht gebunden' in (t or '') for t in texts))
                    self.assertTrue(all(e['arrow_anchor_id'] == 'relation-arrows.reference'
                                        for e in panel['input']['job']['source_bundle']['view_plan']['edges']))
                for field in ('epistemic_warrant', 'current_authority', 'canonical_admission'):
                    self.assertEqual(report[field], 'NOT_EVALUATED')
                self.assertEqual(g6.plan_check(result)['status'], 'PASS')
                if case['op'] == 'statements':
                    self.assertEqual(source['source']['source_kind'], 'statement_set')
                    self.assertIsNone(source['source']['plan_id'])
                    self.assertTrue(all('/statement_sets/' in e['declaration_ref'] for e in ledger.values()))

    def test_origin_colour_is_not_a_code(self):
        _, result = run(VEC['OL-01'])
        by_origin = {}
        for group in edges(result):
            by_origin.setdefault(group.get('data-vp07-origin'), set()).update(
                line.get('stroke') for line in group.findall(f'{{{NS}}}line'))
        self.assertEqual(by_origin['declared'], by_origin['unbound'])

    def test_bad_statement_set_codes(self):
        for change, code in (
            (lambda c: c['plan_source']['statements']['statements'].append(
                copy.deepcopy(c['plan_source']['statements']['statements'][0])), 'VP07_STATEMENT_SET_INVALID'),
            (lambda c: c['plan_source']['statements']['referents'].append('ghost'), 'VP07_STATEMENT_REF_UNKNOWN'),
            (lambda c: c['plan_source']['statements']['statements'][0].update(predicate_id='ghost'),
             'VP07_STATEMENT_PREDICATE_INVALID'),
        ):
            c = copy.deepcopy(VEC['OL-01']); change(c)
            with self.subTest(code=code), self.assertRaises(g6.PlanFailure) as error:
                run(c)
            self.assertEqual(error.exception.diagnostic['code'], code)

    def test_unopted_origin_is_not_bound(self):
        c = copy.deepcopy(VEC['OL-01'])
        c['plan_source']['statements']['statements'][0]['origin'] = 'declared'  # contains is not opted in
        _, result = run(c)
        self.assertEqual(next(e for e in result['report']['origin_ledger'] if e['cell_id'] == 'm-1')['origin'], 'unbound')

    def test_legacy_plan_context_has_unbound_origins(self):
        c = copy.deepcopy(VEC['OL-07'])
        context = c['plan_source']['context']
        context['format'] = 'aiaeao.cube.binding-context/9'
        for p in context['predicate_contracts']:
            p.pop('origin_binding', None)
        for plan in context['migration_plans']:
            for dep in plan['dependencies']:
                dep.pop('origin', None); dep.pop('basis', None)
        _, result = run(c)
        self.assertTrue(all(e['origin'] == 'unbound' for e in result['report']['origin_ledger']))

    def test_artifact_mapping_and_closed_table(self):
        c = copy.deepcopy(VEC['OL-03a'])
        context = c['plan_source']['context']
        template = next(r for r in context['referents'] if r['ref'] == 'c4:shop/api')
        artifact = dict(template, ref='synthetic:artifact-a', concept_id='Y:resource-object:artifact', home='Y')
        context['referents'].extend([artifact, dict(artifact, ref='synthetic:artifact-b')])
        pred = copy.deepcopy(next(p for p in context['predicate_contracts'] if p['predicate_id'] == 'uses'))
        pred.update(predicate_id='artifact-link', subject_concept_ids=['Y:resource-object:artifact'],
                    object_concept_ids=['Y:resource-object:artifact'])
        context['predicate_contracts'].append(pred)
        s = c['plan_source']['statements']
        s['referents'] = ['synthetic:artifact-a', 'synthetic:artifact-b']
        s['statements'][0].update(subject='synthetic:artifact-a', object='synthetic:artifact-b', predicate_id='artifact-link')
        source, result = run(c)
        self.assertEqual(result['report']['status'], 'PASS')
        self.assertEqual(source['source']['rows'][0]['anchor_id'], 'resource-objects.artifact')
        context['referents'][-1]['concept_id'] = 'Z:unknown:unknown'
        pred['object_concept_ids'] = ['Z:unknown:unknown']
        with self.assertRaises(g6.PlanFailure) as error:
            run(c)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_long_basis_label_and_full_ledger(self):
        c = copy.deepcopy(VEC['OL-03b'])
        basis = c['plan_source']['context']['origin_bases'][0]
        basis['statement_ids'] = ['s-1', 's-2', 's-3', 's-4', 's-5']
        _, result = run(c)
        entry = result['report']['origin_ledger'][0]
        self.assertEqual(entry['source_ids'], basis['statement_ids'])
        self.assertEqual(entry['text'], '· derived from s-1, s-2, s-3 +2')

    def test_check_refuses_tampered_origin_svg(self):
        _, result = run(VEC['OL-02'])
        bad = copy.deepcopy(result)
        bad['panels'][0]['svg'] = bad['panels'][0]['svg'].replace('derived from', 'declared from', 1)
        with self.assertRaises(g6.PlanFailure) as error:
            g6.plan_check(bad)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_PANEL_COVERAGE')

    def test_unresolved_basis_is_warning_not_verdict(self):
        _, result = run(VEC['OL-06'])
        self.assertEqual(result['report']['status'], 'PASS')
        self.assertIn('VP07_ORIGIN_UNRESOLVED', [w['code'] for w in result['report']['warnings']])
        self.assertIn('VP07_ORIGIN_UNRESOLVED', [w['code'] for w in result['report']['warning_summary']])

    def test_g6_cli_files_byte_identical(self):
        case = VEC['OL-12']
        source, result = run(case)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            args = case['plan_source']
            for name in ('context', 'statements', 'records'):
                (d / f'{name}.json').write_text(json.dumps(args[name], ensure_ascii=False), 'utf-8')
            src_file = d / 'source.json'
            env = dict(os.environ, PYTHONPATH=str(HERE))
            one = subprocess.run([sys.executable, '-m', 'vpmigration', 'from-plan', '--context', str(d/'context.json'),
                                  '--statements', str(d/'statements.json'), '--records', str(d/'records.json'),
                                  '--profile', P076, '--origin-lines', '--out', str(src_file)],
                                 env=env, capture_output=True, check=True)
            self.assertEqual(json.loads(src_file.read_text()), source['source'])
            self.assertEqual(json.loads((d/'source.mapping.json').read_text()), source['mapping'])
            out = d / 'panels'
            two = subprocess.run([sys.executable, '-m', 'vpmigration', 'print-panels', '--source', str(src_file),
                                  '--view', 'cube.flow', '--partition', 'subject', '--granularity', 'standard',
                                  '--out', str(out)], env=env, capture_output=True, check=True)
            files = g6.vp07.to_files(result)
            self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, files)
            self.assertEqual(g6.plan_check(result)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
