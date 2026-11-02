#!/usr/bin/env python3
"""Materialise S-01…S-16 (VP110_ACCEPTANCE_SPEC.md §6, §8) as explicit inputs.

Contexts and statement sets come from docs/09-Research/statement-sets/inputs. A projection record wraps the result of
the pinned lunados.lib evaluator for the named A case (PR-6); the script refuses unless that result equals the
hand-derived expectation in CHECK-CASES.json. Needs lunados.lib as a sibling checkout (or --lib). Expectations stay in
oracles/independent_s01_s16.json and are copied unchanged.
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
IN = REPO/'docs/09-Research/statement-sets/inputs'
ORACLE = json.loads((HERE/'oracles/independent_s01_s16.json').read_text('utf-8'))
CC = {c['case_id']: c for c in json.loads((REPO/'docs/09-Research/statement-sets/CHECK-CASES.json').read_text('utf-8'))['cases']}
TAIL = {'effectful_execution_authorized': False}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lib', default=str(REPO.parent/'lunados.lib')); a = ap.parse_args()
    lib = Path(a.lib).expanduser()
    entry = lib/'entries/project.aggregate-relations/v1'
    item = next(e for e in json.loads((lib/'INDEX.json').read_text('utf-8'))['entries'] if e['entry_id'] == 'project.aggregate-relations')
    ref = {'library_id': 'lunados.lib', 'entry_id': item['entry_id'], 'revision': item['revision'], 'sha256': item['sha256']}
    lib_cases = {json.loads(f.read_text('utf-8'))['check_case']: json.loads(f.read_text('utf-8')) for f in sorted((entry/'cases').glob('A*.json'))}
    records = {}
    for aid, c in lib_cases.items():
        p = subprocess.run([sys.executable, '-I', str(entry/'evaluator/evaluate.py')], input=json.dumps(c['call']).encode(), capture_output=True, check=True)
        res = json.loads(p.stdout)
        assert res == {**CC[aid]['expected'], **TAIL} or 'error' in CC[aid]['expected'], f'{aid}: lunados.lib result differs from CHECK-CASES'
        records[aid] = {'format': 'aiaeao.cube.projection-record/1', 'library_ref': ref, 'call': c['call'], 'result': res}
    out = []
    for s in ORACLE['cases']:
        out.append({'id': s['id'], 'context': json.loads((IN/s['context']).read_text('utf-8')),
                    'statements': json.loads((IN/s['set']).read_text('utf-8')), 'predicate': s.get('predicate'),
                    'projection': records[s['projection']] if s.get('projection') else None, 'projection_case': s.get('projection'),
                    'axis_order': s.get('axis_order'), 'locale': s.get('locale'), 'via': s.get('via', 'cli'), 'expected': s['expected']})
    (HERE/'fixtures/s01_s16_materialized.json').write_text(json.dumps(
        {'format': 'aiaeao.p2.vp110-vectors/1', 'source': 'VP110_ACCEPTANCE_SPEC.md §6, §8; docs/09-Research/statement-sets; lunados.lib '
         f"project.aggregate-relations/v1 ({item['sha256'][:12]}); synthetic, no client data", 'cases': out},
        ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('wrote', len(out), 'vectors;', len(records), 'projection records')


if __name__ == '__main__':
    main()
