"""VP-07.7 (MILE-013): 0.7.6 plus closed rows for core, connector, toolbox, adapter, grant, evidence and content."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'P3/adapters/mcp-local'))
sys.dont_write_bytecode = True
from aiaeao_mcp_local import plan_views as g6  # noqa: E402
from vpmigration.adapter import MAPPING_076, MAPPING_077  # noqa: E402
from vpmigration.common import P076, P077, LATEST  # noqa: E402

NEW = {  # VP077-02: the fixed table, written down before the code (spec §2)
    'Z:module-body:core': ('module-bodies.core', 'form.module-block'),
    'Z:module-body:connector': ('module-bodies.connector', 'form.module-block'),
    'Z:module-body:toolbox': ('module-bodies.toolbox', 'form.module-block'),
    'Z:module-body:adapter': ('module-bodies.adapter', 'form.module-block'),
    'Z:boundary:grant': ('governance-boundary.grant', 'form.boundary-frame'),
    'Y:resource-object:evidence': ('resource-objects.evidence', 'form.resource-card'),
    'Y:resource-object:content': ('resource-objects.content', 'form.resource-card'),
}
SCOPE = 'synthetic:vp077'
REFS = [('s:core', 'Z:module-body:core'), ('s:connector', 'Z:module-body:connector'), ('s:toolbox', 'Z:module-body:toolbox'),
        ('s:adapter', 'Z:module-body:adapter'), ('s:grant', 'Z:boundary:grant'), ('s:evidence', 'Y:resource-object:evidence'),
        ('s:content', 'Y:resource-object:content'), ('s:runtime', 'Z:module-body:runtime')]
DEPS = [('d1', 's:core', 's:grant', ['p0', 'p1']), ('d2', 's:connector', 's:evidence', ['p0', 'p1']),
        ('d3', 's:toolbox', 's:content', ['p1']), ('d4', 's:adapter', 's:runtime', ['p0', 'p1']),
        ('d5', 's:connector', 's:core', ['p1'])]


def context():
    concepts = dict(REFS)
    return {
        'format': 'aiaeao.cube.binding-context/10', 'reference_version': 'v9.4', 'context_id': 'synthetic.vp077',
        'source_kind': 'external_declaration_unverified', 'scope_ref': SCOPE,
        'referents': [{'ref': r, 'concept_id': c, 'home': c[0], 'layers': ['α'], 'provenance_status': 'declared_unverified',
                       'scope_ref': SCOPE} for r, c in REFS],
        'predicate_contracts': [{'predicate_id': 'uses', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                                 'subject_concept_ids': sorted({concepts[s] for _, s, _, _ in DEPS}),
                                 'object_concept_ids': sorted({concepts[o] for _, _, o, _ in DEPS}),
                                 'direction': 'subject_to_object', 'origin_binding': 'required'}],
        'predicate_profile_refs': [], 'method_profile_refs': ['P1.11/migration-methods-v1'],
        'migration_plans': [{'plan_id': 'pm-077', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                             'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'target'}],
                             'transitions': [{'transition_id': 't-p1', 'at_phase': 'p1', 'retires': [],
                                              'introduces': ['s:toolbox', 's:content']}],
                             'dependencies': [{'dependency_id': i, 'subject': s, 'predicate_id': 'uses', 'object': o,
                                               'kind': 'other', 'holds_in': h, 'origin': 'declared'} for i, s, o, h in DEPS]}]}


def source(profile, ctx=None, origin_lines=True):
    return g6.plan_source(ctx or context(), 'pm-077', 'vpmigration', profile=profile, origin_lines=origin_lines)


class VP077(unittest.TestCase):
    def test_table_is_076_plus_the_fixed_rows(self):
        self.assertEqual({k: v[:2] for k, v in MAPPING_077.items() if k not in MAPPING_076}, NEW)
        self.assertEqual({k: MAPPING_077[k] for k in MAPPING_076}, MAPPING_076)
        self.assertEqual(LATEST, P077)
        self.assertIn(P077, g6.capabilities()['printers']['vpmigration']['profiles'])

    def test_new_rows_print_under_077(self):
        env = source(P077)
        got = {r['concept_id']: (r['anchor_id'], r['form_id']) for r in env['mapping']['referents']}
        self.assertEqual({k: v for k, v in got.items() if k in NEW}, NEW)
        self.assertEqual(env['source']['profile'], P077)
        res = g6.plan_views(env['source'], 'cube.flow', 'detail', partition='subject')
        self.assertEqual(res['report']['status'], 'PASS')
        self.assertTrue(all(e['origin'] == 'declared' for e in env['source']['origin_ledger']))
        self.assertEqual(g6.plan_check(res)['status'], 'PASS')

    def test_phases_view_under_077(self):
        env = source(P077, origin_lines=False)
        res = g6.plan_views(env['source'], 'cube.phases', 'detail', partition='subject')
        self.assertEqual(res['report']['status'], 'PASS')
        self.assertEqual(g6.plan_check(res)['status'], 'PASS')

    def test_076_table_stays_closed(self):
        with self.assertRaises(g6.PlanFailure) as error:
            source(P076)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_x_endpoints_stay_unmapped(self):
        ctx = context()
        ref = next(r for r in ctx['referents'] if r['ref'] == 's:grant')
        ref.update(concept_id='X:endpoint:admission', home='X')
        ctx['predicate_contracts'][0]['object_concept_ids'].append('X:endpoint:admission')
        with self.assertRaises(g6.PlanFailure) as error:
            source(P077, ctx)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_statement_path_under_077(self):
        ctx = context()
        statements = {'format': 'aiaeao.cube.statement-set/2', 'set_id': 'set-077', 'context_id': ctx['context_id'],
                      'referents': ['s:core', 's:grant'],
                      'statements': [{'statement_id': 'st-1', 'subject': 's:core', 'predicate_id': 'uses', 'object': 's:grant',
                                      'origin': 'declared'}]}
        env = g6.plan_source(ctx, None, 'vpmigration', profile=P077, origin_lines=True, statements=statements)
        self.assertEqual(env['source']['source_kind'], 'statement_set')
        self.assertEqual(g6.plan_views(env['source'], 'cube.flow', 'standard', partition='subject')['report']['status'], 'PASS')
        with self.assertRaises(g6.PlanFailure) as error:
            g6.plan_source(ctx, None, 'vpmigration', profile=P076, origin_lines=True, statements=statements)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_076_outputs_byte_identical(self):
        run = subprocess.run([sys.executable, '-B', str(HERE / 'scripts/pin_076_digests.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_g6_cli_files_byte_identical(self):
        env_src = source(P077)
        result = g6.plan_views(env_src['source'], 'cube.flow', 'detail', partition='subject')
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / 'context.json').write_text(json.dumps(context(), ensure_ascii=False), 'utf-8')
            env = dict(os.environ, PYTHONPATH=str(HERE), PYTHONDONTWRITEBYTECODE='1')
            subprocess.run([sys.executable, '-m', 'vpmigration', 'from-plan', '--context', str(d / 'context.json'), '--plan', 'pm-077',
                            '--profile', P077, '--origin-lines', '--out', str(d / 'source.json')], env=env, capture_output=True, check=True)
            self.assertEqual(json.loads((d / 'source.json').read_text()), env_src['source'])
            subprocess.run([sys.executable, '-m', 'vpmigration', 'print-panels', '--source', str(d / 'source.json'), '--view', 'cube.flow',
                            '--partition', 'subject', '--granularity', 'detail', '--out', str(d / 'panels')],
                           env=env, capture_output=True, check=True)
            self.assertEqual({p.name: p.read_bytes() for p in (d / 'panels').iterdir()}, g6.vp07.to_files(result))


if __name__ == '__main__':
    unittest.main()
