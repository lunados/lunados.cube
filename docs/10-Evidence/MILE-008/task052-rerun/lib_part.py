"""MILE-008 TASK-052: LIB part of the BPMN re-run. Runs the pinned lunados.lib evaluator analyze.trace-conformance/v1
(sibling checkout) on the cases CF-12, CF-22, CF-23 and compares with the preregistered expectations of CHECK-CASES.json.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/10-Evidence/MILE-008/task052-rerun/lib_part.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); LIB = ROOT.parent/'lunados.lib'
E = LIB/'entries/analyze.trace-conformance/v1'
CC = {c['case_id']: c for c in json.loads((ROOT/'docs/09-Research/control-flow/CHECK-CASES.json').read_text('utf-8'))['cases']}
item = next(e for e in json.loads((LIB/'INDEX.json').read_text('utf-8'))['entries'] if e['entry_id'] == 'analyze.trace-conformance')
rows = []
for cid, question in (('CF-12', 'BPMN-01-exclusivity: Nahm i1 zwei Pfade?'), ('CF-22', 'BPMN-02-sync-condition: Startete Ship für i2 ohne Lagerprüfung?'),
                      ('CF-23', 'BPMN-02-sync-condition: Warum wartet i2?')):
    case = json.loads((E/'cases'/f'{cid}.json').read_text('utf-8'))
    p = subprocess.run([sys.executable, '-I', str(E/'evaluator/evaluate.py')], input=json.dumps(case['call']).encode(), capture_output=True, check=True)
    got = json.loads(p.stdout)
    pre = CC[cid]['expected_with_profile']
    match = got == case['expected'] and all(got.get(k) == v for k, v in pre.items() if k != 'layer')
    rows.append({'case_id': cid, 'question': question, 'status': got['status'], 'value': got['value'],
                 **{k: got[k] for k in ('paths', 'missing', 'foreign', 'excess', 'activations') if k in got}, 'preregistered': pre, 'match': match})
out = {'format': 'mile008.lib-rerun/1', 'entry': {'entry_id': item['entry_id'], 'index_sha256': item['sha256']},
       'lib_head': subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=LIB, capture_output=True, text=True).stdout.strip(),
       'check_cases_sha256': hashlib.sha256((ROOT/'docs/09-Research/control-flow/CHECK-CASES.json').read_bytes()).hexdigest(),
       'rows': rows, 'all_match': all(r['match'] for r in rows)}
(ROOT/'docs/10-Evidence/MILE-008/task052-rerun/lib-part.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_match', out['all_match'], [(r['case_id'], r['status'], r['value']) for r in rows])
