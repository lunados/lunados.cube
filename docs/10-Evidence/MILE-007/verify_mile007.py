"""MILE-007: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python mit jsonschema):
    python3 -I docs/10-Evidence/MILE-007/verify_mile007.py
Schreibt docs/10-Evidence/MILE-007/verification.json. Prüft die Reihenfolge Erwartung vor Code (Cube und lunados.lib),
führt die Vektor- und Testläufe aus (VP-10 0.11.0, 0.10.x-Pins, LIB-Verifikation), prüft die Sichtprüfung,
unveränderte Schichten, Prüfsummen und Links. Die lange G6-Parität steht im TASK-046-Lauf.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
EV = ROOT/'docs/10-Evidence/MILE-007'
LIB = ROOT.parent/'lunados.lib'
PY = sys.executable


def git(*a, cwd=ROOT):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)


def run(args, cwd=ROOT):
    r = subprocess.run([PY, '-B', *args], cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b, cwd=ROOT):
    return a != b and git('merge-base', '--is-ancestor', a, b, cwd=cwd).returncode == 0


def unchanged_since(f, c, cwd=ROOT):
    return git('diff', '--quiet', c, 'HEAD', '--', f, cwd=cwd).returncode == 0 and not git('status', '--porcelain', '--', f, cwd=cwd).stdout.strip()


base = git('merge-base', 'main', 'HEAD').stdout.strip()[:7]
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'main_base': base,
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}

# 1. Erwartung vor Code
items = []
for f, s, c, w in (('docs/09-Research/statement-sets/CHECK-CASES.json', '91e1c57', '310b522', 'A-Fälle vor LIB und Printer'),
                   ('P2/visual-printer-cells-v1/oracles/independent_s01_s16.json', '91e1c57', '310b522', 'S-Orakel vor dem Printercode'),
                   ('P2/visual-printer-cells-v1/fixtures/regression_0101_digests.json', '91e1c57', '310b522', 'Pins 0.10.1 vor dem Printercode'),
                   ('P2/visual-printer-cells-v1/fixtures/regression_0100_digests.json', '507f8a6', '310b522', 'Pins 0.10.0 (MILE-006)')):
    items.append({'file': f, 'what': w, 'expectation': s, 'code': c, 'before_code': before(s, c), 'unchanged_since': unchanged_since(f, s)})
items.append({'file': 'P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md', 'what': 'Entscheidungen Q-1–Q-10 vor dem Code', 'expectation': '594563c',
              'code': '310b522', 'before_code': before('594563c', '310b522'), 'unchanged_since': 'precisions §8 and status added later'})
lib = {}
if (LIB/'.git').exists():
    E = 'entries/project.aggregate-relations/v1/'
    lib = {'repo': 'lunados.lib', 'branch': git('rev-parse', '--abbrev-ref', 'HEAD', cwd=LIB).stdout.strip(),
           'oracle_cases_before_evaluator': before('cee4e36', 'a9b6dd6', cwd=LIB),
           'oracle_cases_unchanged_since': all(unchanged_since(E+p, 'cee4e36', cwd=LIB) for p in ('cases', 'oracle', 'schema'))}
out['order'] = {'items': items, 'lunados_lib': lib,
                'issues': sum(1 for i in items if not i['before_code'] or i['unchanged_since'] is False)
                          + (0 if not lib or (lib['oracle_cases_before_evaluator'] and lib['oracle_cases_unchanged_since']) else 1)}

# 2. Läufe
cells = ROOT/'P2/visual-printer-cells-v1'
out['runs'] = {
    'vp110_vectors_s': run(['scripts/run_vectors_s.py'], cells),
    'vp100_pins': run(['scripts/pin_0100_digests.py'], cells),
    'vp101_pins': run(['scripts/pin_0101_digests.py'], cells),
    'vp10_vectors_j': run(['scripts/run_vectors.py'], cells),
    'vp101_vectors_o': run(['scripts/run_vectors_o.py'], cells),
    'vpcells_tests': run(['-m', 'unittest', 'tests.test_vp110', 'tests.test_vp101', 'tests.test_vp10'], cells),
    'adapter_tests': run(['-m', 'unittest', 'tests.test_mile007_statements', 'tests.test_mile006_order', 'tests.test_mile005_adapter',
                          'tests.test_validation_discovery'], ROOT/'P3/adapters/mcp-local'),
}
if lib:
    out['runs']['lunados_lib_verify'] = run(['scripts/verify.py', '--cube', str(ROOT)], LIB)
t46 = json.loads((EV/'task046-run.json').read_text('utf-8'))
out['g6_parity_from_task046'] = t46['tests']['mcp-local']

# 3. Sichtprüfung
vis = (EV/'SICHTPRUEFUNG.md').read_text('utf-8')
out['visual_check'] = {'guide': 'docs/10-Evidence/MILE-007/SICHTPRUEFUNG.md', 'user_answer': '1–5 ja' if 'Nutzer: 1–5 ja' in vis else None}

# 4. Schichten und Prüfsummen
frozen = ['AIAEAO_Pure_Cube_P0_v9.4', 'P1'] + [f'P2/{d}' for d in ('visual-printer-2d-lab', 'visual-printer-axes-v1', 'visual-printer-conformance-v1',
                                                                    'visual-printer-granularity-v1', 'visual-printer-migration-v1',
                                                                    'visual-printer-release-v1', 'visual-printer-sequence-v1')] + ['P3/remote-mcp-g5']
cells_changed = sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P2/visual-printer-cells-v1').stdout.split())
old_files = ('vpcells/source.py', 'vpcells/locales/de.json', 'vpcells/locales/de-0101.json')
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts or 'charge3-p16' in f.parts:   # P3/charge3-p16: historical, stale before MILE-005
        continue
    r = subprocess.run(['shasum', '-a', '256', '-c', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'vpcells_0100_0101_sources_unchanged': not any(f'P2/visual-printer-cells-v1/{p}' in cells_changed for p in old_files),
                 'vp10x_byte_identity': 'via pins 0.10.0 (16) and 0.10.1 (9)',
                 'changed_outside_docs': sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P0', 'P1', 'P2', 'P3').stdout.split()),
                 'sha256sums': sums}

# 5. Links
bad = []
for b in ('docs', 'openspec', 'P2/visual-printer-cells-v1'):
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

ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in out['runs'].values()) and out['visual_check']['user_answer']
      and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged']
      and out['layers']['vpcells_0100_0101_sources_unchanged'] and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
