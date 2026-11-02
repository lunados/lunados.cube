"""MILE-008 TASK-048: Abgleich der Erwartung „heute“ (CHECK-CASES.json) mit dem Baseline-Lauf und einer Probe.
Aufruf aus dem Repo-Wurzelverzeichnis: python3 -I docs/10-Evidence/MILE-008/task048_baseline_check.py
Baseline: task048-baseline-report.json (unveränderter Runner, sechs MILE-002-Fälle, zwei Verbindungen).
Probe: zwei heute ausführbare Einzelaussagen ohne MILE-002-Fall (CF-06, CF-07) über den unveränderten lokalen
P1.12-Adapter, Kontext als /8. Für NE gilt: der Gateway-Check ist heute nicht ausführbar; der referenzierte MILE-002-Fall
ist entweder NOT_EXECUTED oder eine Einzelaussage, die für sich PASS ergibt (die Lücke).
"""
import copy, hashlib, json, sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT/'P3/adapters/mcp-local')); sys.dont_write_bytecode = True
from aiaeao_mcp_local import p1_adapter as p1  # noqa: E402

CC = ROOT/'docs/09-Research/control-flow/CHECK-CASES.json'
REP = json.loads((ROOT/'docs/10-Evidence/MILE-008/task048-baseline-report.json').read_text('utf-8'))
cases = json.loads(CC.read_text('utf-8'))['cases']
obs = {}
for run in REP['runs']:
    for c in run['cases']:
        st = 'NOT_EXECUTED' if c.get('invocation_status') == 'NOT_EXECUTED' else c.get('domain_status')
        obs.setdefault(c['case_id'], []).append((st, tuple(c.get('diagnostic_codes') or [])))


def probe(cid):
    gs = ROOT/'docs/09-Research/grammar-sampling/cases'
    if cid == 'CF-06':
        ctx = copy.deepcopy(json.loads((gs/'BPMN-01-routed.json').read_text('utf-8'))['arguments']['context'])
        ref = copy.deepcopy(next(r for r in ctx['referents'] if r['ref'] == 'bpmn:approve-manual')); ref['ref'] = 'bpmn:ship'
        text = 'rel("routedTo",Y:α:Evidence["bpmn:i1/tok-route"],Y:α:WorkItem["bpmn:ship"])'
    else:
        k = next(x for x in json.loads((ROOT/'P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases'] if x['id'] == 'K-14')
        ctx = copy.deepcopy(k['context'])
        ref = copy.deepcopy(next(r for r in ctx['referents'] if r['ref'] == 'bpmn:f-stock-done')); ref['ref'] = 'bpmn:f-ghost'
        text = 'rel("onFlow",Y:α:Evidence["bpmn:i1/tok-stock"],Y:α:WorkItem["bpmn:f-ghost"])'
    ctx['referents'].append(ref)
    ctx['format'] = 'aiaeao.cube.binding-context/8'
    env = p1.validate(text, 'acg_text', ctx)
    return {'input_text': text, 'status': env['report']['overall_status'], 'codes': [d['code'] for d in env['report']['diagnostics']],
            'profile': env.get('coverage_profile')}


rows = []
for c in cases:
    t = c['expected_today']
    if t.get('verified_by', '').startswith('Probe'):
        p = probe(c['case_id'])
        rows.append({'case_id': c['case_id'], 'expected_today': f"P1 {t['status']}", 'probe': p, 'match': p['status'] == t['status'] and not p['codes']})
        continue
    o = obs.get(t['mile002_case'])
    if t['kind'] == 'NE':
        ok = o is not None and all(s == 'NOT_EXECUTED' for s, _ in o) or (o is not None and all(s == 'PASS' and not codes for s, codes in o))
    else:
        ok = o is not None and all(s == t['status'] and list(codes) == t['diagnostic_codes'] for s, codes in o)
    rows.append({'case_id': c['case_id'], 'mile002_case': t['mile002_case'], 'expected_today': 'NE' if t['kind'] == 'NE' else f"P1 {t['status']}",
                 'observed': [list(x) for x in o] if o else None, 'match': bool(ok)})
out = {'format': 'mile008.baseline-check/1', 'task': 'TASK-048', 'check_cases_sha256': hashlib.sha256(CC.read_bytes()).hexdigest(),
       'report': 'task048-baseline-report.json', 'report_git_head': REP['snapshot']['git_head'][:7],
       'repeats_semantically_equal': REP['repeats_semantically_equal'], 'source_unchanged_during_run': REP['source_unchanged_during_run'],
       'readiness_checks_passed': REP['readiness_checks_passed'], 'all_match': all(r['match'] for r in rows), 'rows': rows}
(ROOT/'docs/10-Evidence/MILE-008/task048-baseline-check.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_match', out['all_match'], sum(r['match'] for r in rows), '/', len(rows))
