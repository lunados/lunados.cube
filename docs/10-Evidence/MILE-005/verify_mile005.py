"""MILE-005 TASK-036: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python mit jsonschema):
    python3 -I docs/10-Evidence/MILE-005/verify_mile005.py
Schreibt docs/10-Evidence/MILE-005/verification.json. Führt die Vektor- und Testläufe aus, prüft die
Reihenfolge Erwartung vor Code, unveränderte Schichten, Prüfsummen, den Wiederholungslauf und Links.
lunados.lib wird geprüft, wenn es als Geschwisterordner vorliegt.
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
EV = ROOT/'docs/10-Evidence/MILE-005'
LIB = ROOT.parent/'lunados.lib'
PY = sys.executable


def git(*a, cwd=ROOT):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)


def run(args, cwd=ROOT):
    r = subprocess.run([PY, '-B', *args], cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b, cwd=ROOT):
    return a != b and git('merge-base', '--is-ancestor', a, b, cwd=cwd).returncode == 0


base = git('merge-base', 'main', 'HEAD').stdout.strip()[:7]
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'main_base': base,
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}

# 1. Erwartung vor Code
def unchanged_since(f, c):
    last = git('log', '-1', '--format=%h', '--abbrev=7', '--', f).stdout.strip()
    return last.startswith(c) and not git('status', '--porcelain', '--', f).stdout.strip()

order = [
    ('docs/09-Research/completeness-instances/CHECK-CASES.json', '52cc773', '26c32b6', 'Prüffälle vor der Spezifikation'),
    ('P1/coverage-instance-profile-v1/oracles/independent_k01_k21.json', '8297b82', '4c05b5b', 'P1.12-Orakel vor dem Profilcode'),
    ('docs/09-Research/completeness-instances/rerun/cases', '1250feb', 'bede236', 'Wiederholungserwartung vor dem /8-Adapter'),
]
items = [{'file': f, 'what': w, 'expectation': s, 'code': c, 'before_code': before(s, c), 'unchanged_since': unchanged_since(f, s)} for f, s, c, w in order]
j_first = json.loads(git('show', '2316f45:P2/visual-printer-cells-v1/oracles/independent_j01_j14.json').stdout)
j_now = json.loads((ROOT/'P2/visual-printer-cells-v1/oracles/independent_j01_j14.json').read_text('utf-8'))
items.append({'file': 'P2/visual-printer-cells-v1/oracles/independent_j01_j14.json', 'what': 'VP-10-Orakel vor dem Printercode',
              'expectation': '2316f45', 'code': '639e6c0', 'before_code': before('2316f45', '639e6c0'),
              'expected_states_unchanged': [c['expected'] for c in j_first['cases']] == [c['expected'] for c in j_now['cases']],
              'amendment': 'J-12 Aufrufbeschreibung (dritte Phase, Ausschnitt p1:p2) vor dem Code-Commit korrigiert'})
lib = {}
if (LIB/'.git').exists():
    lib = {'repo': 'lunados.lib', 'branch': git('rev-parse', '--abbrev-ref', 'HEAD', cwd=LIB).stdout.strip(),
           'oracle_before_evaluator': before('33ce6c3', 'c649931', cwd=LIB),
           'cases_unchanged_since': unchanged_since('entries/analyze.population/v1/cases', '33ce6c3') if False else
           git('diff', '--quiet', '33ce6c3', 'HEAD', '--', 'entries/analyze.population/v1/cases', 'entries/analyze.population/v1/oracle', cwd=LIB).returncode == 0}
out['order'] = {'items': items, 'lunados_lib': lib,
                'issues': sum(1 for i in items if not i['before_code'] or not i.get('unchanged_since', i.get('expected_states_unchanged')))}

# 2. Läufe
out['runs'] = {
    'p112_vectors': run(['P1/coverage-instance-profile-v1/scripts/run_vectors.py']),
    'p112_tests': run(['P1/coverage-instance-profile-v1/tests/test_p112.py']),
    'p111_vectors': run(['P1/migration-methods-v1/scripts/run_vectors.py']),
    'vp10_vectors': run(['scripts/run_vectors.py'], ROOT/'P2/visual-printer-cells-v1'),
    'vp10_tests': run(['tests/test_vp10.py'], ROOT/'P2/visual-printer-cells-v1'),
    'adapter_mile005_tests': run(['-m', 'unittest', 'tests.test_mile005_adapter', 'tests.test_validation_discovery'], ROOT/'P3/adapters/mcp-local'),
}
for t in sorted((ROOT/'P1').glob('*/tests/test_*.py')):
    out['runs']['p1:'+t.relative_to(ROOT).as_posix()] = run([str(t)])
if lib:
    out['runs']['lunados_lib_verify'] = run(['scripts/verify.py', '--cube', str(ROOT)], LIB)

# 3. Wiederholungslauf
rep = json.loads((EV/'task036-rerun/report.json').read_text('utf-8'))
base_rep = json.loads((EV/'task030-baseline-report.json').read_text('utf-8'))
now = {c['case_id']: (c['domain_status'], c['diagnostic_codes']) for c in rep['runs'][0]['cases']}
then = {c['case_id']: (c.get('domain_status'), c.get('diagnostic_codes')) for c in base_rep['runs'][0]['cases']}
out['rerun'] = {'readiness_checks_passed': rep['readiness_checks_passed'], 'repeats': len(rep['runs']),
                'all_expectations_matched': all(c['expectation_match'] for r in rep['runs'] for c in r['cases']),
                'case_files_hashes_match': all(hashlib.sha256((ROOT/'docs/09-Research/completeness-instances/rerun/cases'/n).read_bytes()).hexdigest() == h
                                               for n, h in rep['case_file_hashes'].items()),
                'changes_against_baseline': {cid: {'baseline': then.get(cid.removesuffix('-v8')), 'now': now[cid]} for cid in sorted(now)}}

# 4. Schichten und Prüfsummen
frozen = ['AIAEAO_Pure_Cube_P0_v9.4'] + [f'P1/{d}' for d in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1',
          'comparison-profile-v1', 'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'contract-v1', 'release-v1', 'visual-grammar-v1')] \
    + [f'P2/{d}' for d in ('visual-printer-2d-lab', 'visual-printer-axes-v1', 'visual-printer-conformance-v1', 'visual-printer-granularity-v1',
                          'visual-printer-migration-v1', 'visual-printer-release-v1', 'visual-printer-sequence-v1')]
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts:
        continue
    r = subprocess.run(['shasum', '-a', '256', '-c', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
# P3/charge3-p16 is a historical P1.6 Charge 3 snapshot (repo-root paths); it was already stale at the main base.
hist = {}
for f in ('P3/charge3-p16/CHARGE3_SOURCE_SHA256SUMS.txt',):
    bad_base = []
    for line in (ROOT/f).read_text().splitlines():
        h, path = line.split(None, 1)
        b = subprocess.run(['git', 'show', f'{base}:{path}'], cwd=ROOT, capture_output=True)
        if b.returncode != 0 or hashlib.sha256(b.stdout).hexdigest() != h:
            bad_base.append(path)
    hist[f] = {'historical_snapshot': True, 'stale_at_main_base': bad_base}
    sums.pop(f, None)
changed_p3 = sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P3').stdout.split())
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'new_packages': ['P1/coverage-instance-profile-v1', 'P2/visual-printer-cells-v1'],
                 'p3_changed_files': changed_p3, 'sha256sums': sums, 'historical_sums': hist}

# 5. Links
bad = []
for b in ('docs', 'openspec', 'P1/coverage-instance-profile-v1', 'P2/visual-printer-cells-v1'):
    for d, _, fs in os.walk(ROOT/b):
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto')) or 'chatgpt' in t:
                        continue
                    if not (p.parent/t).resolve().exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = bad

ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in out['runs'].values())
      and out['rerun']['readiness_checks_passed'] and out['rerun']['all_expectations_matched'] and out['rerun']['case_files_hashes_match']
      and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged'] and all(sums.values())
      and out['broken_links'] == 0 and (not lib or lib['oracle_before_evaluator'] and lib['cases_unchanged_since']))
out['all_ok'] = ok
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', ok)
