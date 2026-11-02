"""MILE-008: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python mit jsonschema), in zwei Schritten
wegen der Zeitgrenze des Geräts:
    python3 -I docs/10-Evidence/MILE-008/verify_mile008.py --lib   # lunados.lib verify --cube und Differenzprüfung -> lib-verify.json
    python3 -I docs/10-Evidence/MILE-008/verify_mile008.py         # alles andere; liest lib-verify.json, wenn es zum LIB-Stand passt
Schreibt docs/10-Evidence/MILE-008/verification.json. Prüft die Reihenfolge Erwartung vor Code (Cube und lunados.lib),
führt Vektoren und Tests aus (P1, Adapter, LIB), prüft die Wiederholung, unveränderte Schichten, Prüfsummen und Links.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); EV = ROOT/'docs/10-Evidence/MILE-008'; LIB = ROOT.parent/'lunados.lib'; PY = sys.executable


def git(*a, cwd=ROOT):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)


def run(args, cwd=ROOT):
    r = subprocess.run([PY, '-B', *args], cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b, cwd=ROOT):
    return a != b and git('merge-base', '--is-ancestor', a, b, cwd=cwd).returncode == 0


def unchanged_since(f, c, cwd=ROOT):
    return git('diff', '--quiet', c, 'HEAD', '--', f, cwd=cwd).returncode == 0 and not git('status', '--porcelain', '--', f, cwd=cwd).stdout.strip()


LIBRUN = EV/'lib-verify.json'
if '--lib' in sys.argv:
    res = {'lib_head': git('rev-parse', '--short', 'HEAD', cwd=LIB).stdout.strip(), 'lib_clean': not git('status', '--porcelain', cwd=LIB).stdout.strip(),
           'lunados_lib_verify': run(['scripts/verify.py', '--cube', str(ROOT)], LIB), 'lunados_lib_differential': run(['scripts/differential_trace.py'], LIB)}
    LIBRUN.write_text(json.dumps(res, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('lib', res['lunados_lib_verify']['exit'], res['lunados_lib_differential']['exit']); sys.exit(0)
base = git('merge-base', 'main', 'HEAD').stdout.strip()[:7]
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'main_base': base,
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}
items = [{'file': f, 'what': w, 'expectation': s, 'code': c, 'before_code': before(s, c), 'unchanged_since': unchanged_since(f, s)}
         for f, s, c, w in (('docs/09-Research/control-flow/CHECK-CASES.json', 'aefe6aa', 'ff31bd5', 'Prüffälle vor der Spezifikation'),
                            ('P1/control-flow-profile-v1/oracles/independent_kf01_kf09.json', 'd33f22c', '9222424', 'KF-Orakel vor dem Profilcode'),
                            ('docs/09-Research/control-flow/rerun/cases', '76e5ac1', '70d0469', 'Wiederholungserwartung vor dem /9-Adapter'))]
lib = {}
if (LIB/'.git').exists():
    E = 'entries/analyze.trace-conformance/v1/'
    exp_same = True
    for f in sorted((LIB/E/'cases').glob('CF-*.json')):
        old = json.loads(git('show', f'ebb3110:{E}cases/{f.name}', cwd=LIB).stdout)
        now = json.loads(f.read_text('utf-8'))
        exp_same &= (old['expected'], old['preregistered_expected']) == (now['expected'], now['preregistered_expected'])
    lib = {'repo': 'lunados.lib', 'branch': git('rev-parse', '--abbrev-ref', 'HEAD', cwd=LIB).stdout.strip(),
           'oracle_cases_before_evaluator': before('ebb3110', 'd823a4a', cwd=LIB), 'expectations_unchanged_since_ebb3110': exp_same,
           'oracle_changed_after_evaluator': not unchanged_since(E+'oracle', 'ebb3110', cwd=LIB),
           'oracle_change_note': '5511574: sort key for flows without order in oracle and evaluator, documented in TASK-051-LIB.md; expectations unchanged'}
out['order'] = {'items': items, 'lunados_lib': lib,
                'issues': sum(1 for i in items if not (i['before_code'] and i['unchanged_since']))
                          + (0 if not lib or (lib['oracle_cases_before_evaluator'] and lib['expectations_unchanged_since_ebb3110']) else 1)}
jobs = {'p113_vectors': (['P1/control-flow-profile-v1/scripts/run_vectors.py'], ROOT),
        'adapter_tests': (['-m', 'unittest', 'tests.test_mile008_adapter', 'tests.test_mile005_adapter', 'tests.test_validation_discovery',
                           'tests.test_mile006_order', 'tests.test_mile007_statements', 'tests.test_p1_validation'], ROOT/'P3/adapters/mcp-local'),
        'rerun_lib_part': (['-I', 'docs/10-Evidence/MILE-008/task052-rerun/lib_part.py'], ROOT)}
for t in sorted((ROOT/'P1').glob('*/tests/test_*.py')):
    jobs['p1:'+t.relative_to(ROOT).as_posix()] = ([str(t)], ROOT)
for v in sorted((ROOT/'P1').glob('*/scripts/run_vectors.py')):
    jobs['p1-vectors:'+v.relative_to(ROOT).as_posix()] = ([str(v)], ROOT)
from concurrent.futures import ThreadPoolExecutor  # unabhängige Läufe parallel (Zeitgrenze des Geräts)
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {k: ex.submit(run, *v) for k, v in jobs.items()}
out['runs'] = {k: futs[k].result() for k in jobs}
if lib:
    lr = json.loads(LIBRUN.read_text('utf-8')) if LIBRUN.exists() else {}
    current = lr.get('lib_head') == git('rev-parse', '--short', 'HEAD', cwd=LIB).stdout.strip() and lr.get('lib_clean')
    for k in ('lunados_lib_verify', 'lunados_lib_differential'):
        out['runs'][k] = dict(lr.get(k, {'exit': None, 'tail': []}), source='lib-verify.json', lib_head=lr.get('lib_head'), current=bool(current))
        if not current:
            out['runs'][k]['exit'] = None
rep = json.loads((EV/'task052-rerun/report.json').read_text('utf-8'))
out['rerun'] = {'readiness_checks_passed': rep['readiness_checks_passed'], 'repeats': len(rep['runs']),
                'all_expectations_matched': all(c['expectation_match'] for r in rep['runs'] for c in r['cases']),
                'cases': len(rep['runs'][0]['cases'])}
frozen = ['AIAEAO_Pure_Cube_P0_v9.4', 'P2', 'P3/remote-mcp-g5'] + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'P1').iterdir())
                                                                  if p.is_dir() and p.name != 'control-flow-profile-v1']
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts or 'charge3-p16' in f.parts:
        continue
    r = subprocess.run(['shasum', '-a', '256', '-c', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'changed_outside_docs': sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P0', 'P1', 'P2', 'P3').stdout.split()), 'sha256sums': sums}
bad = []
for b in ('docs', 'openspec', 'P1/control-flow-profile-v1', 'P3/adapters/mcp-local'):
    for d, _, fs in os.walk(ROOT/b):
        if 'p0_snapshot' in Path(d).parts:  # eingefrorene P0-Kopie, Links zeigen auf nicht mitkopierte Dokumente
            continue
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto')) or 'chatgpt' in t:
                        continue
                    if not (p.parent/t).resolve().exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = bad
ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in out['runs'].values()) and out['rerun']['readiness_checks_passed']
      and out['rerun']['all_expectations_matched'] and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged']
      and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
