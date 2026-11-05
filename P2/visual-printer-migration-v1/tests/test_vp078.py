"""VP-07.8 (MILE-014): 0.7.7 plus the ten X endpoints (contract anchors) and source, cache, revision."""
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
from vpmigration.adapter import MAPPING_077, MAPPING_078  # noqa: E402
from vpmigration.common import P077, P078, LATEST, PROFILES  # noqa: E402

ENDPOINTS = ('perception', 'conclusion', 'authority', 'admission', 'expectation', 'satisfaction', 'delegation', 'completion',
             'action', 'result')
NEW = {**{f'X:endpoint:{e}': (f'contract-pairs.{e}', 'form.contract-anchor') for e in ENDPOINTS},  # VP078-02, spec §1
       'Y:resource-object:source': ('resource-objects.source', 'form.resource-card'),
       'Y:resource-object:cache': ('resource-objects.cache', 'form.resource-card'),
       'Y:resource-object:revision': ('resource-objects.revision', 'form.resource-card')}
SCOPE = 'synthetic:vp078'
SUBJECTS = {'s:core': 'Z:module-body:core', 's:connector': 'Z:module-body:connector', 's:toolbox': 'Z:module-body:toolbox',
            's:adapter': 'Z:module-body:adapter', 's:runtime': 'Z:module-body:runtime'}
OBJECTS = {f's:{c.split(":")[-1]}': c for c in NEW}
PLAN = {'s:core': ['s:authority', 's:admission', 's:result'], 's:connector': ['s:source', 's:cache', 's:revision'],
        's:toolbox': ['s:perception', 's:conclusion', 's:action'], 's:adapter': ['s:expectation', 's:satisfaction', 's:delegation'],
        's:runtime': ['s:completion']}


def context():
    refs = {**SUBJECTS, **OBJECTS}
    deps = [(f'd{i}', s, o) for i, (s, o) in enumerate(((s, o) for s, os_ in PLAN.items() for o in os_), 1)]
    return {
        'format': 'aiaeao.cube.binding-context/10', 'reference_version': 'v9.4', 'context_id': 'synthetic.vp078',
        'source_kind': 'external_declaration_unverified', 'scope_ref': SCOPE,
        'referents': [{'ref': r, 'concept_id': c, 'home': c[0], 'layers': ['α'], 'provenance_status': 'declared_unverified',
                       'scope_ref': SCOPE} for r, c in refs.items()],
        'predicate_contracts': [{'predicate_id': 'uses', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                                 'subject_concept_ids': sorted(set(SUBJECTS.values())), 'object_concept_ids': sorted(set(OBJECTS.values())),
                                 'direction': 'subject_to_object', 'origin_binding': 'required'}],
        'predicate_profile_refs': [], 'method_profile_refs': ['P1.11/migration-methods-v1'],
        'migration_plans': [{'plan_id': 'pm-078', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                             'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'target'}], 'transitions': [],
                             'dependencies': [{'dependency_id': i, 'subject': s, 'predicate_id': 'uses', 'object': o, 'kind': 'other',
                                               'holds_in': ['p0', 'p1'], 'origin': 'declared'} for i, s, o in deps]}]}


def source(profile, origin_lines=True, ctx=None):
    return g6.plan_source(ctx or context(), 'pm-078', 'vpmigration', profile=profile, origin_lines=origin_lines)


class VP078(unittest.TestCase):
    def test_table_is_077_plus_the_fixed_rows(self):
        self.assertEqual({k: v[:2] for k, v in MAPPING_078.items() if k not in MAPPING_077}, NEW)
        self.assertEqual({k: MAPPING_078[k] for k in MAPPING_077}, MAPPING_077)
        self.assertGreaterEqual(PROFILES.index(LATEST), PROFILES.index(P078))  # later profiles append
        self.assertIn(P078, g6.capabilities()['printers']['vpmigration']['profiles'])

    def test_new_rows_print_under_078(self):
        env = source(P078)
        got = {r['concept_id']: (r['anchor_id'], r['form_id']) for r in env['mapping']['referents']}
        self.assertEqual({k: v for k, v in got.items() if k in NEW}, NEW)
        res = g6.plan_views(env['source'], 'cube.flow', 'detail', partition='subject')
        self.assertEqual(res['report']['status'], 'PASS')
        self.assertEqual(g6.plan_check(res)['status'], 'PASS')
        svg = ''.join(p['svg'] for p in res['panels'])
        for e in ENDPOINTS:
            self.assertIn(f'contract-pairs.{e}', svg)

    def test_phases_view_under_078(self):
        res = g6.plan_views(source(P078, origin_lines=False)['source'], 'cube.phases', 'detail', partition='subject')
        self.assertEqual(res['report']['status'], 'PASS')
        self.assertEqual(g6.plan_check(res)['status'], 'PASS')

    def test_077_table_stays_closed(self):
        with self.assertRaises(g6.PlanFailure) as error:
            source(P077)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_x_scopes_stay_unmapped(self):
        ctx = context()
        ref = next(r for r in ctx['referents'] if r['ref'] == 's:admission')
        ref['concept_id'] = 'X:scope:policy'
        ctx['predicate_contracts'][0]['object_concept_ids'].append('X:scope:policy')
        with self.assertRaises(g6.PlanFailure) as error:
            source(P078, ctx=ctx)
        self.assertEqual(error.exception.diagnostic['code'], 'VP07_ADAPTER_MAPPING')

    def test_statement_path_under_078(self):
        ctx = context()
        statements = {'format': 'aiaeao.cube.statement-set/2', 'set_id': 'set-078', 'context_id': ctx['context_id'],
                      'referents': ['s:core', 's:admission'],
                      'statements': [{'statement_id': 'st-1', 'subject': 's:core', 'predicate_id': 'uses', 'object': 's:admission',
                                      'origin': 'declared'}]}
        env = g6.plan_source(ctx, None, 'vpmigration', profile=P078, origin_lines=True, statements=statements)
        self.assertEqual(g6.plan_views(env['source'], 'cube.flow', 'standard', partition='subject')['report']['status'], 'PASS')

    def test_077_and_076_outputs_byte_identical(self):
        for script in ('pin_076_digests.py', 'pin_077_digests.py'):
            run = subprocess.run([sys.executable, '-B', str(HERE / 'scripts' / script), '--check'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, script + run.stdout + run.stderr)

    def test_g6_cli_files_byte_identical(self):
        env_src = source(P078)
        result = g6.plan_views(env_src['source'], 'cube.flow', 'detail', partition='subject')
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / 'context.json').write_text(json.dumps(context(), ensure_ascii=False), 'utf-8')
            env = dict(os.environ, PYTHONPATH=str(HERE), PYTHONDONTWRITEBYTECODE='1')
            subprocess.run([sys.executable, '-m', 'vpmigration', 'from-plan', '--context', str(d / 'context.json'), '--plan', 'pm-078',
                            '--profile', P078, '--origin-lines', '--out', str(d / 'source.json')], env=env, capture_output=True, check=True)
            self.assertEqual(json.loads((d / 'source.json').read_text()), env_src['source'])
            subprocess.run([sys.executable, '-m', 'vpmigration', 'print-panels', '--source', str(d / 'source.json'), '--view', 'cube.flow',
                            '--partition', 'subject', '--granularity', 'detail', '--out', str(d / 'panels')],
                           env=env, capture_output=True, check=True)
            self.assertEqual({p.name: p.read_bytes() for p in (d / 'panels').iterdir()}, g6.vp07.to_files(result))


if __name__ == '__main__':
    unittest.main()
